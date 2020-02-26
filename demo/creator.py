'''
IBM-Review-Requirement: Art30.3 - DO NOT TRANSFER OR EXCLUSIVELY LICENSE THE FOLLOWING CODE
UNTIL 30/11/2025!
Please note that the following code was developed for the project MUSKETEER in DRL funded by
the European Union under the Horizon 2020 Program.
The project started on 01/12/2018 and will be / was completed on 30/11/2021. Thus, in accordance
with article 30.3 of the Multi-Beneficiary General Model Grant Agreement of the Program, the above
limitations are in force until 30/11/2025.

Author: Tran Ngoc Minh (M.N.Tran@ibm.com).
Modified from creator.py
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

# to run:
# python3 creator.py --credentials <> --user <> --password <> --task_name <>

import argparse
import logging

from demo import fflapi


# Set up logger
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger('creator_pom1_nn')
LOGGER.setLevel(logging.DEBUG)


def args_parse():
    """
    Parse command line args.
    :return: namespace of key/value cmdline args
    :rtype: `namespace`
    """
    parser = argparse.ArgumentParser(description='musketeer worker')
    parser.add_argument('--credentials', required=True)
    parser.add_argument('--task_name', required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--password', required=True)
    cmdline = parser.parse_args()

    return cmdline


def create_task(credentials, user, password, task_name, task_definition):
    """
    Create a Federated ML task.
    :param credentials: json file containing credentials.
    :type credentials: `str`
    :param user: user name for authentication as task creator
    :type user: `str`
    :param password: password for authentication as task creator
    :type password: `str`
    :param task_name: name of the task (must be unique)
    :type task_name: `str`
    :param task_definition: definition of the task
    :type task_definition: `dict`
    """
    creator_context = fflapi.Context.from_credentials_file(credentials,
                                                           user,
                                                           password)

    creator = fflapi.User(creator_context, task_name=task_name)
    topology = fflapi.Topology.star

    with creator:
        result = creator.create_task(topology, task_definition)

    return result


def get_task_participants(credentials, user, password, task_name):
    """
    Retrieve a list with details of all the task participants.
    If called by a participant different from the task creator, the returned list will be empty.
    :param credentials: json file containing credentials.
    :type credentials: `str`
    :param user: user name for authentication as task creator
    :type user: `str`
    :param password: password for authentication as task creator
    :type password: `str`
    :param task_name: name of the task (must be unique)
    :type task_name: `str`
    :return: list with the details of all the task participants
    :rtype: `list`
    """
    context = fflapi.Context.from_credentials_file(credentials, user, password)
    user = fflapi.User(context)

    with user:
        return user.messenger.task_assignments(task_name)


def main():
    """
    Main entry point
    """
    try:
        cmdline = args_parse()

        # create new machine learning task
        task_definition = {"aggregator": "neural_network.Aggregator",
                           "participant": "neural_network.Participant",
                           "quorum": 1,
                           "round": 5,
                           "epoch": 2,
                           "batch_size": 256,
                           "learning_rate": 0.001,
                           "training_size": 3000,
                           "test_size": 1000,
                           }

        result = create_task(cmdline.credentials,
                             cmdline.user,
                             cmdline.password,
                             cmdline.task_name,
                             task_definition)

        LOGGER.debug(result)
        LOGGER.info('task created.')

    except Exception as err:
        LOGGER.error('error: %s', err)
        raise err


if __name__ == '__main__':
    main()
