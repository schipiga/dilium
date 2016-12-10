import uuid

import requests

from dilium.node import Node


class Client(object):

    def __init__(self, dilium_url):
        self._dilium_url = dilium_url
        self._uuid = str(uuid.uuid4())
        self._host = None
        self._capabilities = None
        self._duration = None

    def get_node(self, capabilities, duration=600):
        self._capabilities = capabilities
        self._duration = duration
        self._host = self.request_host()
        self.acquire_host()
        return Node(self)

    def request_host(self, capabilities):
        return requests.get(self._dilium_url + '/request-host/',
                            headers={'client-uuid': self._uuid},
                            json=self._capabilities).content

    def acquire_host(self):
        requests.post(self._dilium_url + '/acquire-host/',
                      headers={'client-uuid': self._uuid},
                      json={'host': self._host, 'duration': self._duration})

    def release_host(self):
        requests.post(self._dilium_url + '/release-host/',
                      headers={'client-uuid': self._uuid},
                      json={'host': self._host})
