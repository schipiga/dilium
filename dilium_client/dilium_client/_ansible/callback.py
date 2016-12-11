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
    """Callback to process result of ansible execution.

    Args:
        bucket (list): Bucket to put execution results.
        display (Display, optional): Ansible Display.
    """

    def __init__(self, bucket, display=None):
        super(Callback, self).__init__(display)
        self._bucket = bucket

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Process execution result on failed."""
        super(Callback, self).v2_runner_on_failed(result, ignore_errors)
        self._store(result, STATUS_FAILED)

    def v2_runner_on_ok(self, result):
        """Process execution result on ok."""
        super(Callback, self).v2_runner_on_ok(result)
        self._store(result, STATUS_OK)

    def v2_runner_on_skipped(self, result):
        """Process execution result on skipped."""
        super(Callback, self).v2_runner_on_skipped(result)
        self._store(result, STATUS_SKIPPED)

    def v2_runner_on_unreachable(self, result):
        """Process execution result on unreachable."""
        super(Callback, self).v2_runner_on_unreachable(result)
        self._store(result, STATUS_UNREACHABLE)

    def _store(self, result, status):
        """Store result in bucket."""
        response = Response(
            host=result._host.get_name(),
            status=status,
            task=result._task.get_name(),
            payload=result._result)
        self._bucket.append(response)
