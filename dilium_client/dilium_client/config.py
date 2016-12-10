import os

CONN_TYPE = 'ssh'
REMOTE_USER = 'vagrant'
SSH_OPTS = '-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

MAX_DISPLAY = 2147483647

ANSIBLE_MODULES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '_ansible', 'modules'))
