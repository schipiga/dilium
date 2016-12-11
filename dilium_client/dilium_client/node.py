"""
-----------
Dilium node
-----------
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

from contextlib import contextmanager
import logging
import random
import signal
import tempfile
import time

from pylru import lrudecorator

from dilium_client._ansible import Executor
from dilium_client._selenium import Chrome

from . import config, utils

LOGGER = logging.getLogger(__name__)


class Node(object):
    """Remote node with requested browser.

    Args:
        client (Client): Dilium client.
    """

    def __init__(self, client):
        self._client = client
        self._display = random.randint(1, config.MAX_DISPLAY)
        self._video_path = None
        self._driver_pid = None
        self._video_pid = None
        self._xvfb_pid = None

    def get_browser(self, *args, **kwgs):
        """Get browser on node.

        Args:
            *args (optional): ``*args`` of browser instantiation.
            **kwgs (optional): ``**kwgs`` of browser instantiation.
        """
        browser = {
            config.CHROME: Chrome,
        }[self._client.browser_name]

        return browser(self, *args, **kwgs)

    def start_video(self, width, height):
        """Start video capturing.

        Args:
            width (int): Video width.
            height (int): Video height.
        """
        if self._video_pid:
            LOGGER.warn('Video capturing is launched already')
            return

        self._video_path = tempfile.mktemp() + '.mp4'

        try:
            self._video_pid = utils.get_pid(
                self.remote_exec.avconv(
                    self._video_path, self._display, width, height))
            time.sleep(1)
        except:
            self._video_path = None
            raise

    def stop_video(self):
        """Stop video capturing."""
        if not self._video_pid:
            LOGGER.warn('Video capturing isn\'t launched still')
            return

        try:
            self.remote_exec.kill(self._video_pid)
            time.sleep(1)
        finally:
            self._video_pid = None

    @contextmanager
    def capture_video(self, width, height):
        """Capture video in context.

        Args:
            width (int): Video width.
            height (int): Video height.
        """
        self.start_video(width, height)
        try:
            yield
        finally:
            self.stop_video()

    def download_video(self, file_path=None):
        """Download captured video.

        Args:
            file_path (str, optional): Path to download video.

        Returns:
            str: Path of downloaded video.
        """
        file_path = file_path or tempfile.mkstemp()[1]
        self.remote_exec.download(self.video_path, file_path)
        return file_path

    def start_xvfb(self, width, height):
        """Start virtual display.

        Args:
            width (int): Screen width.
            height (int): Screen height.
        """
        if self._xvfb_pid:
            LOGGER.warn('Xvfb is launched already')
            return

        self._xvfb_pid = utils.get_pid(
            self.remote_exec.xvfb(self._display, width, height,
                                  options=["-noreset", "-ac"]))
        time.sleep(1)

    def stop_xvfb(self):
        """Stop virtual display."""
        if not self._xvfb_pid:
            LOGGER.warn('Xvfb isn\'t launched still')
            return

        try:
            self.remote_exec.kill(self._xvfb_pid)
            time.sleep(1)
        finally:
            self._xvfb_pid = None

    @contextmanager
    def inside_xvfb(self, width, height):
        """Launch virtual display in context.

        Args:
            width (int): Screen width.
            height (int): Screen height.
        """
        self.start_xvfb(width, height)
        try:
            yield
        finally:
            self.stop_xvfb()

    def start_webdriver(self):
        """Start remote webdriver."""
        if self._driver_pid:
            LOGGER.warn('Webdriver is launched already')
            return

        port = random.randint(*config.PORT_RANGE)
        chrome_cmd = 'chromedriver --port={} --whitelisted-ips=""'.format(port)

        driver_cmd = {
            config.CHROME: chrome_cmd,
        }[self._client.browser_name]

        env = {'DISPLAY': ':{}'.format(self._display)}

        self._driver_pid = utils.get_pid(
            self.remote_exec.webdriver(driver_cmd, env=env))
        time.sleep(1)

        self._webdriver_url = 'http://{}:{}'.format(self._client.host, port)

    def stop_webdriver(self):
        """Stop remote webdriver."""
        if not self._driver_pid:
            LOGGER.warn('Webdriver isn\'t launched still')
            return

        try:
            self.remote_exec.kill(self._driver_pid, signal.SIGTERM)
            time.sleep(1)
        finally:
            self._driver_pid = None

    @property
    @lrudecorator(None)
    def remote_exec(self):
        """Remote ansible executor."""
        return Executor(self._client.host)

    @property
    def webdriver_url(self):
        """Launched webdriver url."""
        assert self._webdriver_url
        return self._webdriver_url

    @property
    def video_path(self):
        """Remote path to captured video."""
        assert self._video_path
        return self._video_path
