"""
-------------
Dilium config
-------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

DEBUG = bool(os.environ.get('DEBUG'))
TMP_BLOCKERS = {}
DEFAULT = object()
DATABASE = 'dilium.db' if not DEBUG else ':memory:'
CAPABILITIES = 'capabilities'
MAX_INSTANCES = 'maxInstances'
BROWSER_NAME = 'browserName'
CLIENT_UUID = 'client-uuid'
TMP_BLOCK_DURATION = 10
APP_PORT = 8888
