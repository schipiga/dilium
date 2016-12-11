#!/usr/bin/python

"""
-----------------------
Ansible module for xvfb
-----------------------

Usage example::

    task = {
        'xvfb': {
            'display': display,
            'width': width,
            'height': height,
            'depth': depth,
            'options': options
        }
    }
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

from ansible.module_utils.basic import *

import tempfile


def wrap_async(cmd):
    pid_path = tempfile.mktemp()
    cmd = 'nohup ' + cmd
    cmd += ' & echo $! > ' + pid_path + ' && cat ' + pid_path
    return 'bash -c "{}"'.format(cmd)


def main():
    module = AnsibleModule(
        argument_spec={
            'display': {'required': True, 'type': 'int'},
            'width': {'required': True, 'type': 'int'},
            'height': {'required': True, 'type': 'int'},
            'depth': {'required': True, 'type': 'int'},
            'options': {'required': True, 'type': 'list'},
        })

    display = module.params['display']
    width = module.params['width']
    height = module.params['height']
    depth = module.params['depth']
    options = module.params['options']

    cmd = 'Xvfb :{} -screen 0 {}x{}x{} >/dev/null 2>&1'.format(
        display, width, height, depth)

    if options:
        cmd += ' ' + ' '.join(options)

    cmd = wrap_async(cmd)

    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
    module.exit_json(cmd=cmd, rc=rc, stderr=stderr, stdout=stdout)


if __name__ == '__main__':
    main()
