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

import pytest

def pytest_addoption(parser):
    parser.addoption("--credentials", required=True)


@pytest.fixture
def credentials(request):
    value = request.config.getoption('credentials')
    if request.cls:
        request.cls.credentials = value
    return value

@pytest.fixture
def broker_user(request):
    value = request.config.getoption('credentials')
    value = value['broker_admin_user']
    if request.cls:
        request.cls.broker_user = value
    return value

@pytest.fixture
def broker_password(request):
    value = request.config.getoption('credentials')
    value = value['broker_admin_password']
    if request.cls:
        request.cls.broker_password = value
    return value
