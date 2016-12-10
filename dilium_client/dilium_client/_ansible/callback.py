from collections import namedtuple
from ansible.plugins.callback import CallbackBase

Response = namedtuple('Response', ('host', 'status', 'task', 'payload'))

STATUS_OK = 'OK'
STATUS_FAILED = 'FAILED'
STATUS_UNREACHABLE = 'UNREACHABLE'
STATUS_SKIPPED = 'SKIPPED'


class Callback(CallbackBase):

    def __init__(self, bucket, display=None):
        super(Callback, self).__init__(display)
        self._bucket = bucket

    def v2_runner_on_failed(self, result, ignore_errors=False):
        super(Callback, self).v2_runner_on_failed(result, ignore_errors)
        self._store(result, STATUS_FAILED)

    def v2_runner_on_ok(self, result):
        super(Callback, self).v2_runner_on_ok(result)
        self._store(result, STATUS_OK)

    def v2_runner_on_skipped(self, result):
        super(Callback, self).v2_runner_on_skipped(result)
        self._store(result, STATUS_SKIPPED)

    def v2_runner_on_unreachable(self, result):
        super(Callback, self).v2_runner_on_unreachable(result)
        self._store(result, STATUS_UNREACHABLE)

    def _store(self, result, status):
        response = Response(
            host=result._host.get_name(),
            status=status,
            task=result._task.get_name(),
            payload=result._result)
        self._bucket.append(response)
