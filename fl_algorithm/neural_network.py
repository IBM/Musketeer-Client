'''
IBM-Review-Requirement: Art30.3 - DO NOT TRANSFER OR EXCLUSIVELY LICENSE THE FOLLOWING CODE
UNTIL 30/11/2025!
Please note that the following code was developed for the project MUSKETEER in DRL funded by
the European Union under the Horizon 2020 Program.
The project started on 01/12/2018 and will be / was completed on 30/11/2021. Thus, in accordance
with article 30.3 of the Multi-Beneficiary General Model Grant Agreement of the Program, the above
limitations are in force until 30/11/2025.

Author: Tran Ngoc Minh (M.N.Tran@ibm.com).
'''
"""
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at
 
 http://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import os
import logging

import numpy as np
from keras.utils import to_categorical
from keras import losses, optimizers
from keras.models import model_from_json, Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten
from keras.datasets import mnist
import pycloudmessenger.ffl.fflapi as fflapi


# Set up logger
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger('fl_training')
LOGGER.setLevel(logging.INFO)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.FATAL)


class BasicParticipant:
    """
    This class implements basic properties and functionalities to be performed in a Federated ML setup.
    """

    def __init__(self, task_definition, comms): 
        """
        Create a :class:`BasicParticipant` instance.
        
        :param task_definition: A specification of the ML task to be performed.
        :type task_definition: `dict`
        :param comms: A communication interface that enables communication between the aggregator and participants.
        :type comms: :class:`pycloudmessenger.ffl.fflapi.BasicParticipant`
        """        
        self.quorum = task_definition['quorum']
        self.epoch = task_definition['epoch']
        self.batch_size = task_definition['batch_size']
        self.learning_rate = task_definition['learning_rate']
        self.round = task_definition['round']
        self.training_size = task_definition['training_size']
        self.test_size = task_definition['test_size']
        self.comms = comms
        self.timeout = 600

    def load_data(self, train=True):
        """
        Load data to be used for training/test.

        :param train: Load train or test data.
        :type train: `bool`
        """
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        if train:
            indices = np.random.choice(np.shape(y_train)[0], self.training_size)
            x, y = x_train, y_train

        else:
            indices = np.random.choice(np.shape(y_test)[0], self.test_size)
            x, y = x_test, y_test

        x, y = x[indices], y[indices]

        return x.reshape(x.shape[0], 28, 28, 1), to_categorical(y, 10)


class Aggregator(BasicParticipant):
    """
    This class implements the functionality of the aggregator.
    """

    def __init__(self, task_definition, comms):
        """
        Create a :class:`Aggregator` instance.

        :param task_definition: A specification of the ML task to be performed.
        :type task_definition: `dict`
        :param comms: A communication interface that enables communication between the aggregator and participants.
        :type comms: :class:`pycloudmessenger.ffl.fflapi.Aggregator`
        """
        super(Aggregator, self).__init__(task_definition, comms)
        self.feature, self.label = self.load_data(train=False)

    def wait_for_workers_to_join(self):
        """
        Wait for workers to join until quorum is met.
        """
        with self.comms:
            results = self.comms.get_participants()
        LOGGER.debug(results)

        if results:
            if len(results) == self.quorum:
                LOGGER.debug('Workers have already joined')
                return results

        LOGGER.info('Waiting on workers to join (%d of %d present)', len(results), self.quorum)

        ready = False
        while not ready:
            try:
                with self.comms:
                    result = self.comms.receive(self.timeout)

            except fflapi.TimedOutException as err:
                raise err

            LOGGER.debug(result)

            if len(results) == self.quorum:
                ready = True

        return results

    def wait_for_workers_to_complete(self):
        """
        Wait for workers to complete assignment.
        """
        results = []
        complete = False
        while not complete:
            try:
                result = self.comms.receive(self.timeout)
                LOGGER.info('Received model update from participant')

            except fflapi.TimedOutException as err:
                raise err

            if fflapi.Notification.is_participant_updated(result):
                results.append(result)

            if len(results) == self.quorum:
                complete = True

        return results

    def start(self):
        """
        Run the Aggregator.
        """
        LOGGER.info('Waiting on quorum')
        self.wait_for_workers_to_join()
        LOGGER.info('Quorum of workers found')

        LOGGER.info('Starting training')

        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(28, 28, 1)))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(10, activation='softmax'))
        model.compile(loss=losses.categorical_crossentropy,
                      optimizer=optimizers.Adam(lr=self.learning_rate),
                      metrics=['accuracy'])

        LOGGER.info('Distributing neural network architecture to participants')

        with self.comms:
            self.comms.send({'model': model.to_json()})

        import time
        for iter in range(self.round):
            start = time.time() 
          
            LOGGER.info("Round " + str(iter))
            LOGGER.info('Asking participants to update model weights, do local training and send back model update')

            with self.comms:
                self.comms.send({'weights': model.get_weights()})
                weight_updates = self.wait_for_workers_to_complete()
                LOGGER.info('Received model updates from all participants, start updating the central model')

            list_updates = []
            for weight_update in weight_updates:
                weight = weight_update['params']['updated_weights']
                weight = np.array([np.array(w) for w in weight])
                list_updates.append(weight)

            model.set_weights(np.mean(np.array(list_updates), axis=0))

            [loss, accuracy] = model.evaluate(self.feature, self.label, verbose=0)
            end = time.time()
            LOGGER.info("Round %d, loss %f, val accuracy %f, time %f" % (iter, loss, accuracy, end - start))

        LOGGER.info('Finished %d rounds, done' % self.round)
        [_, accuracy] = model.evaluate(self.feature, self.label)
        LOGGER.info("Test accuracy %f" % accuracy)

        LOGGER.info('END')

        return {'weights': model.get_weights()}


class Participant(BasicParticipant):
    """
    This class implements the functionality of the participant.
    """

    def __init__(self, task_definition, comms):
        """
        Create a :class:`Participant` instance.

        :param task_definition: A specification of the ML task to be performed.
        :type task_definition: `dict`
        :param comms: A communication interface that enables communication between the aggregator and participants.
        :type comms: :class:`pycloudmessenger.ffl.fflapi.Participant`
        """
        super(Participant, self).__init__(task_definition, comms)
        self.feature, self.label = self.load_data(train=True)

    def start(self):
        """
        Run the Participant.
        """        
        try:
            with self.comms:
                msg = self.comms.receive(self.timeout)
                LOGGER.info("Received model architecture from the aggregator")

            model = model_from_json(msg['params']['model'])
            model.compile(loss=losses.categorical_crossentropy,
                          optimizer=optimizers.Adam(lr=self.learning_rate),
                          metrics=['accuracy'])

        except fflapi.TimedOutException as timeout:
            LOGGER.exception(timeout)
        except fflapi.ConsumerException as consumer_ex:
            LOGGER.exception(consumer_ex)

        for iter in range(self.round):
            try:
                with self.comms:
                    msg = self.comms.receive(self.timeout)

                LOGGER.info("Round " + str(iter))
                LOGGER.info('Received model update from the aggregator, start to update local model and train locally')

                weights = msg['params']['weights']
                model.set_weights(weights)
                model.fit(self.feature, self.label, batch_size=self.batch_size, epochs=self.epoch)
                updated_weights = model.get_weights()

                LOGGER.info('Finished local training and send back model update to the aggregator')
                with self.comms:
                    self.comms.send({'updated_weights': updated_weights})

            except fflapi.TimedOutException as timeout:
                LOGGER.exception(timeout)
            except fflapi.ConsumerException as consumer_ex:
                LOGGER.exception(consumer_ex)

        LOGGER.info('Finished %d rounds, done.' % self.round)

        try:
            with self.comms:
                result = self.comms.receive(self.timeout)

            if fflapi.Notification.is_aggregator_stopped(result):
                weights = result['params']['weights']
                model.set_weights(weights)

                LOGGER.info('Received the final model from aggregator')

        except fflapi.TimedOutException as timeout:
            LOGGER.exception(timeout)
        except fflapi.ConsumerException as consumer_ex:
            LOGGER.exception(consumer_ex)
