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
# python3 register.py --credentials <> --user <> --password <> --org <> --platform <>

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
    parser = utils.create_args(description='Musketeer user registration')
    parser.add_argument('--org', required=True, help='Your organisation')
    cmdline = parser.parse_args()

    return cmdline


def create_user(context, user, password, org):
    """
    Create the user to communicate with FFL.

    :param context: context info.
    :type context: `pycloudmessenger.ffl.abstractions.AbstractContext`
    :param user: user name (must be unique).
    :type user: `str`
    :param password: password.
    :type password: `str`
    :param org: organization the user belongs to.
    :type org: `str`
    """
    ffl_user = ffl.Factory.user(context)

    with ffl_user:
        ffl_user.create_user(user, password, org)


def main():
    """
    Main entry point.
    """
    try:
        cmdline = args_parse()
        context = utils.platform(cmdline.platform, cmdline.credentials)
        create_user(context, cmdline.user, cmdline.password, cmdline.org)
        LOGGER.info('User %s created', cmdline.user)

    except Exception as err:
        LOGGER.error('Error: %s', err)


if __name__ == '__main__':
    main()
