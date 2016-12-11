"""
------------
Dilium utils
------------
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

import tempfile


def wrap_async(cmd):
    """Wrap shell command to async execution command."""
    pid_path = tempfile.mktemp()
    cmd = 'nohup ' + cmd
    cmd += ' & echo $! > ' + pid_path + ' && cat ' + pid_path
    return 'bash -c "{}"'.format(cmd)


def get_pid(ansible_result):
    """Get process ID from ansible result of remote async command."""
    return int(ansible_result[0].payload['stdout'].strip())
