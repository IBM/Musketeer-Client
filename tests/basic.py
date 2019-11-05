#!/usr/bin/env python3
#author markpurcell@ie.ibm.com

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

"""
IBM-Review-Requirement: Art30.3 - DO NOT TRANSFER OR EXCLUSIVELY LICENSE THE FOLLOWING CODE UNTIL 30/11/2025!
Please note that the following code was developed for the project MUSKETEER in DRL funded by the European Union
under the Horizon 2020 Program.
The project started on 01/12/2018 and was completed on 30/11/2021. Thus, in accordance with article 30.3 of the
Multi-Beneficiary General Model Grant Agreement of the Program, the above limitations are in force until 30/11/2025.
"""

import logging
import time
import unittest
import pytest
import pycloudmessenger.ffl.fflapi as fflapi


#Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-6s %(name)-16s :: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

LOGGER = logging.getLogger(__package__)


@pytest.mark.usefixtures("credentials")
class MessengerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_file = None

        import os
        cfg = os.environ.get('PYCLOUDMESSENGER')
        if cfg is not None:
            import json
            jsn = json.loads(cfg)

            cls.config_file = 'config.json'
            with open(cls.config_file, 'w') as jout:
                json.dump(jsn, jout)

    @classmethod
    def tearDownClass(cls):
        import os

        cfg = os.environ.get('PYCLOUDMESSENGER')
        if cfg is not None:
            import os
            os.remove(cls.config_file)

    #@unittest.skip("temporarily skipping")
    def test_get_tasks(self):
        if self.config_file is None:
            self.config_file = self.credentials

        context = fflapi.Context.from_credentials_file(self.config_file)
        user = fflapi.User(context)
        with user:
            result = user.get_tasks()
            for r in result:
                LOGGER.info(f"{r['task_name']}")
