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
# python3 participant.py --credentials <> --user <> --password <> --task_name <> --platform <> --kwargs <>

import json
import logging
import traceback

import pycloudmessenger.ffl.abstractions as ffl
from pycloudmessenger.serializer import JsonPickleSerializer as serializer

#from demo.aggregator import get_class
from aggregator import get_class
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
    parser = utils.create_args(description='Musketeer participant')
    parser.add_argument('--task_name', required=True)
    parser.add_argument('--kwargs', required=False, default=None)
    cmdline = parser.parse_args()

    return cmdline


def run(context, task_name, **kwargs):
    """
    Run the algorithm for the given task as participant.

    :param context: context info.
    :type context: `pycloudmessenger.ffl.abstractions.AbstractContext`
    :param task_name: training task to be performed.
    :type task_name: `str`
    """
    user = ffl.Factory.user(context)

    with user:
        task_definition = serializer().deserialize(user.task_info(task_name)['definition'])

    participant = ffl.Factory.participant(context, task_name=task_name)

    import sys
    sys.path.append("../fl_algorithm")

    alg_class = get_class(task_definition['participant'])
    algorithm = alg_class(task_definition, participant, **kwargs)

    try:
        algorithm.start()

    except Exception as e:
        traceback.print_exc()
        LOGGER.error(str(e))

    LOGGER.info('Completed training !!!')


def main():
    """
    Main entry point.
    """
    try:
        cmdline = args_parse()
        context = utils.platform(cmdline.platform, cmdline.credentials, cmdline.user, cmdline.password)

        if cmdline.kwargs is not None:
            run(context, cmdline.task_name, **json.load(cmdline.kwargs))
        else:
            run(context, cmdline.task_name)

    except Exception as err:
        LOGGER.error('Error: %s', err)
        raise err


if __name__ == '__main__':
    main()
