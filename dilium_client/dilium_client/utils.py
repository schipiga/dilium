import tempfile


def wrap_async(cmd):
    pid_path = tempfile.mktemp()
    cmd = 'nohup ' + cmd
    cmd += ' & echo $! > ' + pid_path + ' && cat ' + pid_path
    return 'bash -c "{}"'.format(cmd)


def get_pid(ansible_result):
    """Get process ID from ansible result of remote async command."""
    return int(ansible_result[0].payload['stdout'].strip())
