import tempfile
import signal

from ansible.plugins import module_loader
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import play
from ansible.executor import task_queue_manager

from dilium_client import config, utils

from .callback import Callback
from .options import Options

module_loader.add_directory(config.ANSIBLE_MODULES_PATH)


class Executor(object):

    def __init__(self, *hosts, **options):
        self._hosts = list(hosts)

        self.options = Options()
        self.options.connection = options.get('conn_type',
                                              config.CONN_TYPE)
        self.options.remote_user = options.get('remote_user',
                                               config.REMOTE_USER)
        self.options.ssh_common_args = config.SSH_OPTS

    def __call__(self, cmd, async=False):
        if async:
            cmd = utils.wrap_async(cmd)

        return self._exec({'shell': cmd})

    def download(self, src, dst=None, flat=True):
        dst = dst or tempfile.mkstemp()
        task = {
            'fetch': {
                'src': src,
                'dest': dst,
                'flat': flat,
            }
        }
        self._exec(task)
        return dst

    def xvfb(self, display, width=800, height=600, depth=24, options=None):
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

    def avconv(self, file_path, display, frame_rate=30,
               width=800, height=600, codec='libx264', options=None):
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
        task = {
            'webdriver': {
                'command': command,
                'log_file': log_path,
                'env': env
            }
        }
        return self._exec(task)

    def kill(self, pid, sig=signal.SIGINT):
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

        storage = []
        callback = Callback(storage)

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
            if tqm is not None:
                tqm.cleanup()

        return storage
