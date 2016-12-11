"""
-----------------------
Dilium ansible executor
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

import signal

from ansible.executor import task_queue_manager
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import play
from ansible.plugins import module_loader
from ansible.vars import VariableManager

from dilium_client import config, utils

from .callback import Callback
from .options import Options

module_loader.add_directory(config.ANSIBLE_MODULES_PATH)


class Executor(object):
    """Remote commands executor via ansible.

    Args:
        *hosts (optional): Sequence of hosts where commands will be executed.
            As minimum one host should be passed
        **options (optional): Options for ansible. Full sequence is described
            in ``Options`` section.
    """

    def __init__(self, *hosts, **options):
        assert hosts
        self._hosts = list(hosts)

        self.options = Options()
        self.options.connection = options.get('conn_type',
                                              config.CONN_TYPE)
        self.options.remote_user = options.get('remote_user',
                                               config.REMOTE_USER)
        self.options.ssh_common_args = config.SSH_OPTS

    def __call__(self, cmd, async=False):
        """Execute shell command."""
        if async:
            cmd = utils.wrap_async(cmd)

        return self._exec({'shell': cmd})

    def download(self, src, dst, flat=True):
        """Download file from remote to local host."""
        task = {
            'fetch': {
                'src': src,
                'dest': dst,
                'flat': flat,
            }
        }
        return self._exec(task)

    def xvfb(self, display, width=800, height=600, depth=24, options=None):
        """Launch xvfb on remote host."""
        task = {
            'xvfb': {
                'display': display,
                'width': width,
                'height': height,
                'depth': depth,
                'options': options
            }
        }
        return self._exec(task)

    def avconv(self, file_path, display, width=800, height=600,
               frame_rate=30, codec='libx264', options=None):
        """Launch avconv on remote host."""
        task = {
            'avconv': {
                'rate': frame_rate,
                'width': width,
                'height': height,
                'display': display,
                'codec': codec,
                'options': options,
                'file': file_path
            }
        }
        return self._exec(task)

    def webdriver(self, command, env=None, log_path='/dev/null'):
        """Launch webdriver on remote host."""
        task = {
            'webdriver': {
                'command': command,
                'log_file': log_path,
                'env': env
            }
        }
        return self._exec(task)

    def kill(self, pid, sig=signal.SIGINT):
        """Send signal to process on remote host."""
        return self._exec({'shell': 'kill -{} {}'.format(sig, pid)})

    def _exec(self, task):
        """Execute ansible task."""
        play_source = {'hosts': self._hosts,
                       'tasks': [task],
                       'gather_facts': 'no'}

        loader = DataLoader()
        variable_manager = VariableManager()
        inventory_inst = Inventory(loader=loader,
                                   variable_manager=variable_manager,
                                   host_list=self._hosts)
        variable_manager.set_inventory(inventory_inst)

        play_inst = play.Play().load(play_source,
                                     variable_manager=variable_manager,
                                     loader=loader)

        bucket = []
        callback = Callback(bucket)

        tqm = task_queue_manager.TaskQueueManager(
            inventory=inventory_inst,
            variable_manager=variable_manager,
            loader=loader,
            options=self.options,
            passwords=dict(vault_pass='secret'),
            stdout_callback=callback)

        try:
            tqm.run(play_inst)
        finally:
            tqm.cleanup()

        return bucket
