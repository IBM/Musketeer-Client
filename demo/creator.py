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

# to run:
# python3 creator.py --credentials <> --user <> --password <> --task_name <> --platform <>

import logging

import pycloudmessenger.ffl.abstractions as ffl

import platform_utils as utils


# Set up logger
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)s %(thread)d :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def args_parse():
    """
    Parse command line args.

    :return: namespace of key/value cmdline args.
    :rtype: `namespace`
    """
    parser = utils.create_args(description='Musketeer task creation')
    parser.add_argument('--task_name', required=True)
    cmdline = parser.parse_args()

    return cmdline


def create_task(context, task_name, task_definition):
    """
    Create a Federated ML task.

    :param context: context info.
    :type context: `pycloudmessenger.ffl.abstractions.AbstractContext`
    :param task_name: name of the task (must be unique).
    :type task_name: `str`
    :param task_definition: definition of the task.
    :type task_definition: `dict`
    """
    user = ffl.Factory.user(context)

    with user:
        result = user.create_task(task_name, ffl.Topology.star, task_definition)

    return result


def main():
    """
    Main entry point.
    """
    try:
        cmdline = args_parse()
        context = utils.platform(cmdline.platform, cmdline.credentials, cmdline.user, cmdline.password)

        # create new machine learning task
        task_definition = {"aggregator": "neural_network.Aggregator",
                           "participant": "neural_network.Participant",
                           "quorum": 1,
                           "round": 1,
                           "epoch": 2,
                           "batch_size": 256,
                           "learning_rate": 0.001,
                           "training_size": 10000,
                           "test_size": 1000,
                           }

        result = create_task(context, cmdline.task_name, task_definition)

        LOGGER.debug(result)
        LOGGER.info('Task created.')

    except Exception as err:
        LOGGER.error('Error: %s', err)
        raise err


if __name__ == '__main__':
    main()
