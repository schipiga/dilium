from dilium.node import Node


class Dilium(object):

    def __init__(self, server_url):
        self._client = Client(server_url)
        self._capabilities = self._client.get_capabilities()

    def get_node(self, capabilities):
        self_client.get_connect(capabilities)
        return Node(self)
