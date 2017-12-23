Radicale Remind Storage
=======================

Radicale storage backends for Remind, Abook and Taskwarrior.

Dependencies
------------

* `Radicale <https://www.radicale.org>`_
* `python-remind <https://github.com/jspricke/python-remind>`_
* `Remind <https://www.roaringpenguin.com/products/remind>`_
* `python-abook <https://github.com/jspricke/python-abook>`_
* `python-icstask <https://github.com/jspricke/python-icstask>`_
* `Taskwarrior <https://taskwarrior.org>`_

Installation
------------

You need to have the Remind and Taskwarrior command line tools installed.
For Debian/Ubuntu use::

  $ sudo apt-get install remind task

Using pip
~~~~~~~~~

::

  $ pip install radicale-remind

This will install all Python dependencies as well.

Using python-setuptools
~~~~~~~~~~~~~~~~~~~~~~~

::

  $ python setup.py install


Config
------

::

  [server]
  hosts = 0.0.0.0:5232
  ssl = True
  certificate = /path/to/certificate.crt
  key = /path/to/privateKey.key
  
  [auth]
  type = htpasswd
  htpasswd_filename = /path/to/users
  htpasswd_encryption = sha1
  
  [storage]
  type = radicale_remind
  filesystem_folder = /home
  remind_file = /path/to/.reminders
  remind_timezone = Europe/Berlin
  abook_file = /path/to/.abook/addressbook
  task_folder = /path/to/.task
  
  [web]
  type = none

Put this into ``~/.config/radicale/config``.
The ``remind_file``, ``abook_file`` and ``task_folder`` are optional, and can be left out if not used.
Also have a look at the `Radicale documentation <http://radicale.org/documentation/>`_.

Run
---

::

  $ radicale

Add hostname:5232 to your CalDAV clients, like `DAVdroid <https://www.davdroid.com/>`_ available in `F-Droid <https://f-droid.org/>`_.
