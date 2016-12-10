#!/usr/bin/python

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

from ansible.module_utils.basic import *  # noqa


def main():
    """
    """
    module = AnsibleModule(
        argument_spec={
            'rate': {'required': True, 'type': 'int'},
            'width': {'required': True, 'type': 'int'},
            'height': {'required': True, 'type': 'int'},
            'display': {'required': True, 'type': 'int'},
            'codec': {'required': True, 'type': 'str'},
            'options': {'required': True, 'type': 'list'},
            'file': {'required': True, 'type': 'str'},
        })

    rate = module.params['rate']
    width = module.params['width']
    height = module.params['height']
    display = module.params['display']
    codec = module.params['codec']
    options = module.params['options']
    file = module.params['file']
    pid_path = tempfile.mktemp()

    cmd = 'nohup avconv -f x11grab -r {} -s {}x{} -i :{} -codec {}'.format(
        rate, width, height, display, codec)
    if options:
        cmd += ' ' + ' '.join(options)
    cmd += ' ' + file + ' >/dev/null 2>&1'
    cmd += ' & echo $! > ' + pid_path
    cmd = 'bash -c "{}"'.format(cmd)

    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
    rc, stdout, stderr = module.run_command('cat ' + pid_path, check_rc=True)
    module.exit_json(cmd=cmd, rc=rc, stderr=stderr, stdout=stdout)


if __name__ == '__main__':
    main()
