"""
--------------
Chrome wrapper
--------------
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

from selenium import webdriver
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection


class Chrome(webdriver.Chrome):

    def __init__(self,
                 node,
                 chrome_options=None,
                 desired_capabilities=None):
        """Constructor.

        Args:
            node (Node): Remote node with chrome browser.
            chrome_options (object, optional): Chrome options.
            desired_capabilities (dict, optional): Desired chrome capabilities.
        """
        chrome_options = chrome_options or self.create_options()
        desired_capabilities = desired_capabilities or {}
        desired_capabilities.update(chrome_options.to_capabilities())

        self._desired_capabilities = desired_capabilities
        self._node = node

    def launch(self):
        """Launch chrome browser."""
        self._node.start_webdriver()

        executor = ChromeRemoteConnection(
            remote_server_addr=self._node.webdriver_url)

        try:
            super(webdriver.Chrome, self).__init__(
                command_executor=executor,
                desired_capabilities=self._desired_capabilities)
        except:
            self.quit()
            raise

    def quit(self):
        """Quit from browser."""
        try:
            super(webdriver.Chrome, self).quit()
        finally:
            self._node.stop_webdriver()
