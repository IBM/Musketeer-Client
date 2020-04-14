'''
IBM-Review-Requirement: Art30.3 - DO NOT TRANSFER OR EXCLUSIVELY LICENSE THE FOLLOWING CODE
UNTIL 30/11/2025!
Please note that the following code was developed for the project MUSKETEER in DRL funded by
the European Union under the Horizon 2020 Program.
The project started on 01/12/2018 and will be / was completed on 30/11/2021. Thus, in accordance
with article 30.3 of the Multi-Beneficiary General Model Grant Agreement of the Program, the above
limitations are in force until 30/11/2025.
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
import time
import requests
import json

import pycloudmessenger.ffl.abstractions as fflabc
from pycloudmessenger.serializer import JsonPickleSerializer as serializer


class TimedOutException(Exception):
    """
    Over-ride exception.
    """


class ConsumerException(Exception):
    """
    Over-ride exception.
    """


class Context(dict):
    """
    A faked class pretending to hold connection details for an FFL service.
    """

    def __init__(self, config, *args, **kwargs):
        self.update(config)

        if len(args) > 0:
            user = args[0]
        else:
            user = kwargs.get('user')

        self.update({'user': user})


participant_list = []


class BasicParticipant:
    """
    Base class for an FFL general user.
    """

    def __init__(self, context):
        """
        Class initializer.

        :param context: connection details.
        :type context: :class:`.Context`
        """
        self.context = context
        self.url = context['url']
        self.port = context['port']
        self.path = self.url + ':' + str(self.port) + '/'
        self.user = context['user']
        self.serializer = serializer()

    def __enter__(self):
        """
        Context manager enters - call connect.
        Throws: An exception on failure.

        :return: self
        :rtype: :class:`.BasicParticipant`
        """
        return self

    def __exit__(self, *args):
        """
        Context manager exits - call close.
        Throws: An exception on failure.
        """
        pass


class User(fflabc.AbstractUser, BasicParticipant):
    """
    Class that allows a general user to avail of the FFL platform services.
    """

    def create_user(self, user_name, password, organisation):
        """
        Register a new user on the platform.
        Throws: An exception on failure.

        :param user_name: user name (must be a non-empty string and unique;
                                     if a user with this name has registered
                                     before, an exception is thrown).
        :type user_name: `str`
        :param password: password (must be a non-empty string).
        :type password: `str`
        :param organisation: name of the user's organisation.
        :type organisation: `str`
        """
        pass

    def create_task(self, task_name: str, topology, definition):
        """
        Creates a task with the given definition and returns a dictionary
        with the details of the created tasks.
        Throws: An exception on failure.

        :param task_name: Name of the task
        :type task_name: `str`
        :param topology: topology of the task participants' communication network.
        :type topology: `str`
        :param definition: definition of the task to be created.
        :type definition: `dict`
        :return: details of the created task.
        :rtype: `dict`
        """
        # First reset the local platform as we only allow it to serve 1 task at a time
        global participant_list
        participant_list = []
        requests.post(self.path + 'reset')

        # Then create a new task
        message = self.serializer.serialize(definition)
        payload = {'message': message, 'task_name': task_name}
        r = requests.post(self.path + 'create_task', params=payload)

        return {task_name: r}

    def task_info(self, task_name: str):
        """
        Returns the details of a given task.
        Throws: An exception on failure.

        :param task_name: Name of the task
        :type task_name: `str`
        :return: details of the task.
        :rtype: `dict`
        """
        r = requests.get(self.path + 'task_info', params={})

        if r.status_code == requests.codes.ok:
            definition = json.loads(r.text)['message']
        else:
            raise Exception('Unexpected status code when receiving message: %i' % r.status_code)

        return definition

    def join_task(self, task_name: str):
        """
        As a potential task participant, try to join an existing task that has yet to start.
        Throws: An exception on failure.

        :param task_name: Name of the task
        :type task_name: `str`
        :return: details of the task assignment.
        :rtype: `dict`
        """
        payload = {'message': self.user}
        r = requests.post(self.path + 'join_task', params=payload)

        return {task_name: r}

    def get_tasks(self):
        """
        Returns a list with all the available tasks.
        Throws: An exception on failure.

        :return: list of all the available tasks.
        :rtype: `list`
        """
        r = requests.get(self.path + 'get_tasks', params={})

        if r.status_code == requests.codes.ok:
            task_name = json.loads(r.text)['message']
        else:
            raise Exception('Unexpected status code when receiving message: %i' % r.status_code)

        return task_name

    def get_joined_tasks(self):
        """
        Returns a list with all the joined tasks.
        Throws: An exception on failure.

        :return: list of all the available tasks.
        :rtype: `list`
        """
        payload = {'message': self.user}
        r = requests.get(self.path + 'get_joined_tasks', params=payload)

        if r.status_code == requests.codes.ok:
            joined_tasks = json.loads(r.text)['message']
        else:
            raise Exception('Unexpected status code when receiving message: %i' % r.status_code)

        return joined_tasks


class Aggregator(fflabc.AbstractAggregator, BasicParticipant):
    """
    This class provides the functionality needed by the aggregator of a federated learning task.
    """

    def __init__(self, context, task_name=None):
        """
        Class initializer.
        Throws: An exception on failure.

        :param context: Connection details.
        :type context: :class:`.Context`
        :param task_name: Name of the task (note: the user must be the creator of this task).
        :type task_name: `str`
        :param download_models: Whether downloaded model file name or model url should
                                be returned by receive function.
        :type download_models: `bool`
        """
        super().__init__(context)
        self.task_name = task_name

    def get_participants(self):
        """
        Return a list of participants.
        Throws: An exception on failure.

        :return participant: list of participants.
        :rtype participant: `dict`
        """
        r = requests.get(self.path + 'get_participants', params={})

        global participant_list

        if r.status_code == requests.codes.ok:
            participants = json.loads(r.text)['message']
        else:
            raise Exception('Unexpected status code when receiving message: %i' % r.status_code)

        participant_list.extend(participants)

        return participant_list

    def send(self, message=None):
        """
        Send a message to all task participants and return immediately (not waiting for a reply).
        Throws: An exception on failure.

        :param message: message to be sent (needs to be serializable into json string).
        :type message: `dict`
        """
        message = self.serializer.serialize(message)
        payload = {'message': message}
        requests.post(self.path + 'aggregator_send', json=payload)

    def receive(self, timeout=0):
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure.

        :param timeout: timeout in seconds.
        :type timeout: `int`
        :return: received message.
        :rtype: `dict`
        """
        start = time.time()

        global participant_list

        while time.time() - start < timeout:
            r = requests.get(self.path + 'aggregator_receive', params={})

            if r.status_code == requests.codes.ok:
                result = r.json()['message']

                if isinstance(result, list) and result[0] == fflabc.Notification.participant_joined:
                    participant_list.append(result[1])
                    return fflabc.Response(result, None)
                else:
                    result['params'] = self.serializer.deserialize(result['params'])
                    return fflabc.Response(result['notification'], result['params'])

        raise TimedOutException('Timeout when receiving data (%f over %f seconds)' % ((time.time() - start), timeout))

    def stop_task(self, model=None):
        """
        As a task creator, stop the given task.
        The status of the task will be changed to 'COMPLETE'.
        Throws: An exception on failure.
        """
        self.send(message=model)


class Participant(fflabc.AbstractParticipant, BasicParticipant):
    """
    This class provides the functionality needed by the participants of a federated learning task.
    """

    def __init__(self, context, task_name=None):
        """
        Class initializer.
        Throws: An exception on failure.

        :param context: connection details.
        :type context: :class:`.Context`
        :param task_name: name of the task (the user needs to be a participant of this task).
        :type task_name: `str`
        :param download_models: whether downloaded model file name or model url should
                                be returned by receive function.
        :type download_models: `bool`
        """
        super().__init__(context)
        self.task_name = task_name

    def send(self, message=None):
        """
        Send a message to the aggregator and return immediately (not waiting for a reply).
        Throws: An exception on failure.

        :param message: message to be sent (needs to be serializable into json string).
        :type message: `dict`
        """
        message = self.serializer.serialize(message)
        payload = {'message': message}
        requests.post(self.path + 'participant_send', json=payload)

    def receive(self, timeout=0):
        """
        Wait for a message to arrive or until timeout period is exceeded.
        Throws: An exception on failure.

        :param timeout: timeout in seconds.
        :type timeout: `int`
        :return: received message.
        :rtype: `dict`
        """
        start = time.time()
        while time.time() - start < timeout:
            r = requests.get(self.path + 'participant_receive', params={'user': self.user})

            if r.status_code == requests.codes.ok:
                result = self.serializer.deserialize(r.json()['message'])
                return fflabc.Response(None, result)

        raise TimedOutException('Timeout when receiving data (%f over %f seconds)' % ((time.time() - start), timeout))

    def leave_task(self):
        """
        As a task participant, leave the given task.
        Throws: An exception on failure.
        """
        pass
