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

from ansible.module_utils.basic import *

import tempfile


def wrap_async(cmd, env=None):
    pid_path = tempfile.mktemp()
    cmd = 'nohup ' + cmd
    if env:
        envs = ' '.join("{0}='{1}'".format(*item) for item in env.items())
        cmd = 'env ' + envs + ' ' + cmd
    cmd += ' & echo $! > ' + pid_path + ' && cat ' + pid_path
    return 'bash -c "{}"'.format(cmd)


def main():
    """
    """
    module = AnsibleModule(
        argument_spec={
            'command': {'required': True, 'type': 'str'},
            'log_file': {'required': False,
                         'type': 'str',
                         'default': '/dev/null'},
            'env': {'required': False, 'type': 'dict'}
        })

    command = module.params['command']
    log_file = module.params['log_file']
    env = module.params['env']

    cmd = '{} >{} 2>&1'.format(command, log_file)
    cmd = wrap_async(cmd, env)

    rc, stdout, stderr = module.run_command(cmd, check_rc=True)
    module.exit_json(cmd=cmd, rc=rc, stderr=stderr, stdout=stdout)


if __name__ == '__main__':
    main()
