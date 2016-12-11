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

- Selenium grid doesn't manage node. It just provide webdriver API. Some
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
