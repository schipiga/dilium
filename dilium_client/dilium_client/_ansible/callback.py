"""
-----------------------
Dilium ansible callback
-----------------------
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

from collections import namedtuple
from ansible.plugins.callback import CallbackBase

Response = namedtuple('Response', ('host', 'status', 'task', 'payload'))

STATUS_OK = 'OK'
STATUS_FAILED = 'FAILED'
STATUS_UNREACHABLE = 'UNREACHABLE'
STATUS_SKIPPED = 'SKIPPED'


class Callback(CallbackBase):
    """Callback to process result of ansible execution."""

    def __init__(self, bucket, display=None):
        super(Callback, self).__init__(display)
        self._bucket = bucket

    def v2_runner_on_failed(self, result, ignore_errors=False):
        super(Callback, self).v2_runner_on_failed(result, ignore_errors)
        self._store(result, STATUS_FAILED)

    def v2_runner_on_ok(self, result):
        super(Callback, self).v2_runner_on_ok(result)
        self._store(result, STATUS_OK)

    def v2_runner_on_skipped(self, result):
        super(Callback, self).v2_runner_on_skipped(result)
        self._store(result, STATUS_SKIPPED)

    def v2_runner_on_unreachable(self, result):
        super(Callback, self).v2_runner_on_unreachable(result)
        self._store(result, STATUS_UNREACHABLE)

    def _store(self, result, status):
        response = Response(
            host=result._host.get_name(),
            status=status,
            task=result._task.get_name(),
            payload=result._result)
        self._bucket.append(response)
