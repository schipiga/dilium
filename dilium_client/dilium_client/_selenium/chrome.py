from selenium import webdriver
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection


class Chrome(webdriver.Chrome):

    def __init__(self,
                 node,
                 chrome_options=None,
                 desired_capabilities=None):
        self._node = node

        if chrome_options is None:
            # desired_capabilities stays as passed in
            if desired_capabilities is None:
                desired_capabilities = self.create_options().to_capabilities()
        else:
            if desired_capabilities is None:
                desired_capabilities = chrome_options.to_capabilities()
            else:
                desired_capabilities.update(chrome_options.to_capabilities())

        self._node.start_webdriver()

        try:
            super(webdriver.Chrome, self).__init__(
                command_executor=ChromeRemoteConnection(
                    remote_server_addr=self._node.webdriver_url),
                desired_capabilities=desired_capabilities)
        except Exception:
            self.quit()
            raise

    def quit(self):
        """
        """
        try:
            super(webdriver.Chrome, self).quit()
        finally:
            self._node.stop_driver()
