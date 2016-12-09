from selenium import webdriver
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection


class Chrome(webdriver.Chrome):

    def __init__(self,
                 node,
                 executable_path="chromedriver",
                 port=0,
                 chrome_options=None,
                 service_args=None,
                 desired_capabilities=None,
                 service_log_path=None):
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

        self._node.remote_exec.start_driver(
            executable_path,
            port=port,
            service_args=service_args,
            log_path=service_log_path)

        remote_url = 'http://{}:{}'.format(self._node.host, port)

        try:
            super(webdriver.Chrome, self).__init__(
                command_executor=ChromeRemoteConnection(
                    remote_server_addr=remote_url),
                desired_capabilities=desired_capabilities)
        except Exception:
            self.quit()
            raise

    def quit(self):
        """
        """
        super(webdriver.Chrome, self).quit()
        self._node.remote_exec.stop_driver(self._node.host, self._driver_path)
