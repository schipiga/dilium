"""
-------------
Dilium client
-------------
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

import uuid

import requests

from . import config, node


class Client(object):
    """Client for Dilium server to get node."""

    def __init__(self, dilium_url):
        """Constructor.

        Args:
            dilium_url (str): URL to dilium server.
        """
        self._dilium_url = dilium_url.strip('/')
        self._uuid = str(uuid.uuid4())
        self._host = None
        self._duration = None
        self._browser_name = None

    def get_node(self, capabilities, duration=config.ACQUIRE_DURATION):
        """Get node with browser according to requested capabilities.

        Arguments:
            capabilities (dict): Requested browser|node capabilities
            duration (int, optional): Duration of acquisition in seconds.

        Returns:
            Node: Remote node with browser.
        """
        host = self.request_host(capabilities)
        self.acquire_host(host, duration)
        return node.Node(self)

    def request_host(self, capabilities):
        """Request host with desired capabilities.

        Args:
            capabilities (dict): Desired host capabilities.

        Returns:
            str: Available host IP.
        """
        response = requests.get(
            self._dilium_url + '/request-host/',
            headers={'client-uuid': self._uuid},
            json=capabilities)

        response.raise_for_status()
        return response.json()['host']

    def acquire_host(self, host, duration):
        """Confirm host acquisition.

        Args:
            host (str): Acquired host IP.
            duration (int): Duration of acquisition in seconds.
        """
        response = requests.post(
            self._dilium_url + '/acquire-host/',
            headers={'client-uuid': self._uuid},
            json={'host': host, 'duration': duration})

        response.raise_for_status()

        self._host = host
        self._duration = duration
        self._browser_name = response.json()['browser']

    def release_host(self):
        """Release acquired host."""
        response = requests.post(
            self._dilium_url + '/release-host/',
            headers={'client-uuid': self._uuid},
            json={'host': self._host})

        response.raise_for_status()

        self._host = None
        self._duration = None
        self._browser_name = None

    @property
    def host(self):
        """Acquired host."""
        assert self._host, 'No host is acquired'
        return self._host

    @property
    def browser_name(self):
        """Browser name in acquired host."""
        assert self._browser_name, 'Undefined browser because no acquired host'
        return self._browser_name
