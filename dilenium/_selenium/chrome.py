from selenium import webdriver

class Chrome(webdriver.Chrome):

    def __init__(self, executable_path="chromedriver", port=0,
                chrome_options=None, service_args=None,
             desired_capabilities=None, service_log_path=None):


    def quit(self):
        remote_webdriver.WebDriver.quit(self)
        remote_executor.stop_driver(self._node.host, self._driver_path)
