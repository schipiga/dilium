from dilium_client import Client
import requests
client = Client('http://127.0.0.1:8888/')
config = {'192.168.1.8': {'capabilities': [{'browserName': 'chrome'}]}}
requests.post('http://127.0.0.1:8888/upload-config/', json=config)

node = client.get_node({'browserName': 'chrome'})
screen_size = (1366, 768)
with node.inside_xvfb(*screen_size):
    with node.capture_video(*screen_size):
        browser = node.get_browser()
        browser.launch()
        # in xvfb direct ``maximize_window``-call doesn't work properly :(
        browser.set_window_size(*screen_size)
        browser.maximize_window()
        browser.get('http://yandex.ru')
        browser.save_screenshot('/home/user/dilium.png')
        browser.quit()
node.download_video('/home/user/dilium.mp4')
client.release_host()
