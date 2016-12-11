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

It is alternate of selenium grid. But it's fully *python* project, which
uses selenium and ansible under hood.

---------
Why is it
---------

Selenium grid has some disadvantages:

- Selenium grid doesn't manage node. It just provide webdriver API. Some
  additional functionalities, like video capture and xvfb mode, are implemented
  via hacks (proxies, servlets, etc).
- Selenium grid requires additional client (minion) on node.
- Selenium grid is developed with Java. If it's necessary to expand its
  functionality we need to learn Java, even if project(s) is developed with
  other language.

Gridless advantages:
- Ansible provides flexible and extensible way to manipulate with node.
- Ansible doesn't require client-side software, just ssh-access.
- Webdriver can be launched directly on node and listen remote connections as
  it happens in localhost.

-------------
How to launch
-------------

-----------------
Current abilities
-----------------


---------
TODO list
---------


-----------------
Deep to structure
-----------------

.. toctree::
   :maxdepth: 1

   server
   client
