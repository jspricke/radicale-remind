Radicale Remind Storage
=======================

Radicale storage backends providing a two way sync for Remind, Abook and
Taskwarrior. Remind files included from the main file are exported as
individual iCal calendars, Taskwarrior projects as individual iCal todo lists.
Also see the limitations sections for `Remind limitations
<https://github.com/jspricke/python-remind#known-limitations>`_ and
`Taskwarrior limitations
<https://github.com/jspricke/python-icstask#known-limitations>`_ for what can
be converted.

Dependencies
------------

* `Radicale <https://radicale.org>`_
* `python-remind <https://github.com/jspricke/python-remind>`_
* `Remind <https://dianne.skoll.ca/projects/remind/>`_
* `python-abook <https://github.com/jspricke/python-abook>`_
* `python-icstask <https://github.com/jspricke/python-icstask>`_
* `Taskwarrior <https://taskwarrior.org>`_

Installation
------------

You need to have the Remind and Taskwarrior command line tools installed if you
want to use the respective adapters. For Debian/Ubuntu use::

  $ sudo apt-get install remind taskwarrior

Using pip
~~~~~~~~~

::

  $ pip install radicale-remind

This will install all Python dependencies as well.

Using python-setuptools
~~~~~~~~~~~~~~~~~~~~~~~

::

  $ python3 setup.py install


Config
------

::

  [server]
  hosts = 0.0.0.0:5232

  [rights]
  type = from_file
  file = /home/user/.config/radicale/rights
  
  [storage]
  type = radicale_remind
  filesystem_folder = /home
  remind_file = /home/user/.reminders
  abook_file = /home/user/.abook/addressbook
  task_folder = /home/user/.task

Put this into ``/home/user/.config/radicale/config`` (replace ``/home/user`` by your ``$HOME``).
The ``remind_file``, ``abook_file`` and ``task_folder`` are optional, and can be removed if not used.

The ``filesystem_folder`` must be the absolute file path up until your user directory. 
This will typically be ``/home``.  

::

  # Allow reading root collection for authenticated users
  [root]
  user: .+
  collection:
  permissions: R

  # Allow reading and writing principal collection (same as username)
  [principal]
  user: .+
  collection: {user}
  permissions: RW

  # Allow reading and writing calendars and address books that are
  # children of the principal collection
  [calendars]
  user: .+
  collection: {user}/.*
  permissions: rw

Put this into ``/home/user/.config/radicale/rights``.
This is modified from ``owner_only`` and needed to allow access to collections with a slash in the name like ``.abook/addressbook/``.
Please read the `Radicale documentation <https://radicale.org/master.html#documentation>`_ for how to set up secure connections and authentication.

Run
---

::

  $ radicale

Add ``http://hostname:5232`` to your CalDAV clients, like `DAVx⁵ <https://www.davx5.com/>`_ available in `F-Droid <https://f-droid.org/packages/at.bitfire.davdroid/>`_.


Client test
-----------

::

  $ curl -u user:password -X PROPFIND -H "Depth: 1" -d "<propfind><prop></prop></propfind>" "http://localhost:5232"
  $ curl -u user:password "http://localhost:5232/user/.reminders/"
  $ curl -u user:password "http://localhost:5232/user/.abook/addressbook/"
  $ curl -u user:password "http://localhost:5232/user/.task/all_projects/"

Note that the trailing slash is required for all paths (directories and singular files). 
The trailing slashes are not required in your ``radicale`` conf.
