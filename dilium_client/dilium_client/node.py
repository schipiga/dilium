import random
import signal
from contextlib import contextmanager
import tempfile

from pylru import lrudecorator

from dilium._ansible import Executor
from dilium._selenium import Chrome


class Node(object):
    """
    """
    MAX_DISPLAY = 2147483647

    def __init__(self, client):
        self._client = client
        self._display = random.randint(1, self.MAX_DISPLAY)
        self._video_path = None

    def get_browser(self):
        """
        """
        browser = {
            'Chrome': Chrome,
        }[self._client.browser]
        return browser(self)

    def start_video(self):
        """
        """
        self._video_path = tempfile.mktemp()
        self._video_pid = self.remote_exec.avconv(self._video_path)

    def stop_video(self):
        """
        """
        self.remote_exec.kill(self._video_pid, signal.SIGINT)

    @contextmanager
    def capture_video(self):
        """
        """
        self.start_video()
        try:
            yield
        finally:
            self.start_video()

    def download_video(self):
        """
        """
        self.remote_exec.download(self._video_path)

    def start_xvfb(self):
        """
        """
        self._xvfb_pid = self.remote_exec.xvfb(
            self._display, options=["-noreset", "-ac"])

    def stop_xvfb(self):
        """
        """
        self.remote_exec.kill(self._xvfb_pid)

    @contextmanager
    def inside_xvfb(self):
        """
        """
        self.start_xvfb()
        try:
            yield
        finally:
            self.stop_xvfb()

    def start_webdriver(self):
        """
        """
        self._driver_pid = self.remote_exec('chromedriver', async=True)

    def stop_webdriver(self):
        """
        """
        self.remote_exec.kill(self._driver_pid)

    @property
    @lrudecorator(None)
    def remote_exec(self):
        return Executor(self._client._host)
