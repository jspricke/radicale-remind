# -*- coding: utf-8 -*-
#
# This file is part of Radicale Server - Calendar Server
# Copyright © 2013-2015 Jochen Sprickerhof
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radicale.  If not, see <http://www.gnu.org/licenses/>.

"""
Remind storage backend.

"""

from contextlib import contextmanager
from dateutil.tz import gettz
from os import sep
from os.path import expanduser, basename, getmtime, join, isfile, isdir
from radicale.ical import Collection as icalCollection
from radicale.config import get
from remind import Remind
from time import strftime, gmtime


class Collection(icalCollection):

    _tz = gettz(get('storage', 'remind_timezone'))
    # Manually set timezone name to generate correct ical files
    # (python-vobject tests for the zone attribute)
    _tz.zone = get('storage', 'remind_timezone')
    _remind = Remind(expanduser(get('storage', 'remind_file')), _tz)

    @staticmethod
    def _abs_path(path):
        return join(expanduser(get("storage", "filesystem_folder")), path.replace("/", sep))

    def append(self, _, text):
        """Append items from ``text`` to collection.

        If ``name`` is given, give this name to new items in ``text``.

        """
        if 'remind' in self.path:
            self._remind.append(text, self._abs_path(self.path))

    def remove(self, name):
        """Remove object named ``name`` from collection."""
        if 'remind' in self.path:
            self._remind.remove(name, self._abs_path(self.path))

    def replace(self, name, text):
        """Replace content by ``text`` in collection objet called ``name``."""
        if 'remind' in self.path:
            self._remind.replace(name, text, self._abs_path(self.path))

    def save(self, text):
        """Save the text into the collection."""
        pass

    def delete(self):
        """Delete the collection."""
        pass

    @property
    def text(self):
        """Collection as plain text."""
        if 'remind' in self.path:
            return self._remind.to_vobject(self._abs_path(self.path)).serialize().decode('utf-8')
        return ""

    @classmethod
    def children(cls, path):
        """Yield the children of the collection at local ``path``."""
        children = []
        for filename in cls._remind.get_filesnames():
            children.append(cls(filename.replace(cls._abs_path(path), path)))
        return children

    @classmethod
    def is_node(cls, path):
        """Return ``True`` if relative ``path`` is a node.

        A node is a WebDAV collection whose members are other collections.

        """
        return isdir(cls._abs_path(path))

    @classmethod
    def is_leaf(cls, path):
        """Return ``True`` if relative ``path`` is a leaf.

        A leaf is a WebDAV collection whose members are not collections.

        """
        return isfile(cls._abs_path(path))

    @property
    def last_modified(self):
        """Get the last time the collection has been modified.

        The date is formatted according to rfc1123-5.2.14.

        """
        return strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(getmtime(self._abs_path(self.path))))

    @property
    @contextmanager
    def props(self):
        """Get the collection properties."""
        # On enter
        if 'remind' in self.path:
            yield {'tag': 'VCALENDAR', 'ICAL:calendar-color': '#%06x' % (hash(basename(self.path)) % 0xffffff)}
        else:
            yield {}
        # On exit
