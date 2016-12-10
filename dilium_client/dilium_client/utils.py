import tempfile


def wrap_async(cmd):
    pid_path = tempfile.mktemp()
    cmd = 'nohup ' + cmd
    cmd += ' & echo $! > ' + pid_path + ' && cat ' + pid_path
    return 'bash -c "{}"'.format(cmd)
