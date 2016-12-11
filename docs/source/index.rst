.. dilium documentation master file, created by
   sphinx-quickstart on Sat Dec 10 20:14:04 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================================
Welcome to Dilium - Distributed Selenium project!
=================================================

----------
What is it
----------

It is **python** alternative of ``selenium grid``, which uses **selenium** and
**ansible** under hood.

---------
Why is it
---------

Selenium grid has some disadvantages:

- Selenium grid doesn't manage node. It just provides webdriver API. Some
  additional functionalities, like video capture and xvfb mode, are implemented
  via hacks on client side (proxies, servlets, etc).
- Selenium grid requires additional client (minion) on node.
- Selenium grid is developed with Java. If it's necessary to expand its
  functionality we need to learn Java, even if project(s) is developed with
  other language.

Gridless advantages:

- Ansible provides flexible and extensible way to manipulate with nodes.
- Ansible doesn't require client-side software, just ssh-access.
- Webdriver can be launched directly on node and listen remote connections as
  it happens in localhost.

-------------
How to launch
-------------

*Functionality in development*

- Clone project::

   git clone https://github.com/sergeychipiga/dilium

- Launch ubuntu virtual machine (for ex. via *vagrant*) with available IP.
- Add your ``.ssh/id_rsa.pub`` to vm ``.ssh/authorized_keys`` in order to
  enable ssh access with key.
- Install ``google-chrome``, ``chromedriver``, ``xvfb``, ``libav-tools`` to vm.
- Add chromedriver path to ``$PATH`` in ``/etc/environment``.

- Install dilium server::

   pip install -r dilium_server/requirements.txt
   pip install -e dilium_server

- Install dilium client::

   pip install -r dilium_client/requirements.txt
   pip install -e dilium_client

- Launch dilium server::

   DEBUG=1 python dilium_server/dilium_server/bin/app.py

- Execute code to upload test config:

  .. code:: python


     import requests
     remote_ip = 'ip.of.your.vm'  # for ex. 192.168.1.8
     config = {
         remote_ip: {
             'capabilities': [
                 {'browserName': 'chrome'}
             ]
         }
     }
     requests.post('http://127.0.0.1:8888/upload-config/',
                   json=config)

- Execute code on remote node to launch browser in xvfb with video capturing:

  .. code:: python

     from dilium_client import Client

     client = Client('http://127.0.0.1:8888/')
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
             browser.save_screenshot('/path/to/screenshot.png')
             browser.quit()

     node.download_video('/path/to/video.mp4')
     client.release_host()


-----------------
Current abilities
-----------------

- Hosts distribution
- Nodes provisioning (*verified with ubuntu 14.04*)
- Browser manipulation (*verfied with google chrome*)
- Xvfb launching
- Video capturing

---------
TODO list
---------

- Check that async call really starts process. (*It isn't verified by default
  due to shell specific.*)
- Support firefox on linux.
- Support windows and macos.
- Expand capabilities to manage nodes from client and server.

-----------------
Deep to structure
-----------------

.. toctree::
   :maxdepth: 1

   server
   client
