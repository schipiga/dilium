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
            'width': {},
            'height': {},
            'depth': {},
            'options': {},
        })

    width = module.params['width']
    height = module.params['height']
    depth = module.params['depth']
    options = module.params['options']
    pid_path = tempfile.mktemp()

    cmd = 'Xvfb :1 -screen 0 {}x{}x{}'.format(width, height, depth)
    if options:
        cmd += ' ' + ' '.join(options)
    cmd += ' & echo $! > ' + pid_path
    cmd = 'bash -c "{}"'.format(cmd)

    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
    rc, stdout, stderr = module.run_command('cat ' + pid_path, check_rc=True)
    module.exit_json(cmd=cmd, rc=rc, stderr=stderr, stdout=stdout)


if __name__ == '__main__':
    main()
