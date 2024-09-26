# Remind, Abook, Taskwarrior Storage backend for Radicale
#
# Copyright (C) 2013-2024  Jochen Sprickerhof
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Remind, Abook, Taskwarrior Storage backend for Radicale."""

from collections.abc import Iterable, Iterator, Mapping
from colorsys import hsv_to_rgb
from os.path import basename, dirname, expanduser, join
from time import gmtime, strftime
from typing import Callable, ContextManager, overload
from zoneinfo import ZoneInfo

from abook import Abook

from icstask import IcsTask

from radicale import config
from radicale import item as radicale_item
from radicale import types
from radicale.item import Item
from radicale.log import logger
from radicale.pathutils import sanitize_path
from radicale.storage import BaseCollection, BaseStorage

from remind import Remind

from vobject.base import Component


class MinCollection(BaseCollection):
    def __init__(self, path: str) -> None:
        self._path = sanitize_path(path).strip("/")

    @property
    def path(self) -> str:
        """The sanitized path of the collection without leading or
        trailing ``/``."""
        return self._path

    # fmt: off
    @overload
    def get_meta(self, key: None = None) -> Mapping[str, str]: ...

    @overload
    def get_meta(self, key: str) -> None | str: ...

    def get_meta(self, key: None | str = None
                 ) -> None | Mapping[str, str] | str:
        """Get metadata value for collection.

        Return the value of the property ``key``. If ``key`` is ``None`` return
        a dict with all properties

        """
    # fmt: on
        return None if key else {}

    def get_multi(self, hrefs: Iterable[str]
                  ) -> Iterable[tuple[str, None | radicale_item.Item]]:
        """Fetch multiple items.

        It's not required to return the requested items in the correct order.
        Duplicated hrefs can be ignored.

        Returns tuples with the href and the item or None if the item doesn't
        exist.

        """
        return ()


class Collection(BaseCollection):
    uid_cache: dict[str, str] = {}

    """Collection stored in adapters for Remind, Abook, Taskwarrior."""

    def __init__(self, path: str, filename: str, adapter: Abook | IcsTask | Remind) -> None:
        self._path = sanitize_path(path).strip("/")
        self.filename = filename
        self.adapter = adapter

    @property
    def path(self) -> str:
        """The sanitized path of the collection without leading or
        trailing ``/``."""
        return self._path

    # fmt: off
    def get_multi(self, hrefs: Iterable[str]
                  ) -> Iterable[tuple[str, None | radicale_item.Item]]:
        """Fetch multiple items.

        It's not required to return the requested items in the correct order.
        Duplicated hrefs can be ignored.

        Returns tuples with the href and the item or None if the item doesn't
        exist.

        """
    # fmt: on
        hrefs = [Collection.uid_cache.get(href, href) for href in hrefs]
        return (
            (x[0], self._convert(x))
            for x in self.adapter.to_vobjects(self.filename, hrefs)
        )

    def get_all(self) -> Iterable[radicale_item.Item]:
        """Fetch all items."""
        return (self._convert(x) for x in self.adapter.to_vobjects(self.filename))

    def _list(self) -> Iterable[str]:
        """List collection items."""
        yield from self.adapter.get_uids(self.filename)

    def _convert(self, elem: tuple[str, Component, str]) -> radicale_item.Item:
        """Fetch a single item."""
        return Item(
            collection=self,
            vobject_item=elem[1],
            href=elem[0],
            last_modified=self.last_modified,
            etag=elem[2],
        )

    def _get(self, href: str) -> radicale_item.Item:
        """Fetch a single item."""
        item, etag = self.adapter.to_vobject_etag(self.filename, href)
        return self._convert((href, item, etag))

    def has_uid(self, uid: str) -> bool:
        """Check if a UID exists in the collection."""
        return uid in self.adapter.get_uids()

    # fmt: off
    def upload(self, href: str, item: radicale_item.Item) -> (
            radicale_item.Item):
        """Upload a new or replace an existing item."""
    # fmt: on
        href = Collection.uid_cache.get(href, href)
        if href in self.adapter.get_uids(self.filename):
            uid = self.adapter.replace_vobject(href, item.vobject_item, self.filename)
        else:
            uid = self.adapter.append_vobject(item.vobject_item, self.filename)
            Collection.uid_cache[href] = uid
        try:
            return self._get(uid)
        except KeyError as error:
            logger.warning(
                "Unable to find uploaded event, maybe increase remind_lookahead_month"
            )
            raise ValueError(f"Failed to store item {href} in collection {self.path}: {error}") from error

    def delete(self, href: None | str = None) -> None:
        """Delete an item.

        When ``href`` is ``None``, delete the collection.

        """
        if not href:
            raise NotImplementedError
        href = Collection.uid_cache.get(href, href)

        self.adapter.remove(href, self.filename)

    def _get_color(self) -> str:
        files = self.adapter.get_filesnames()
        index = files.index(self.filename)
        rgb = hsv_to_rgb(index / len(files), 0.5, 0.9)
        red, green, blue = (int(255 * x) for x in rgb)
        return f"#{red:02x}{green:02x}{blue:02x}"

    # fmt: off
    @overload
    def get_meta(self, key: None = None) -> Mapping[str, str]: ...

    @overload
    def get_meta(self, key: str) -> None | str: ...

    def get_meta(self, key: None | str = None
                 ) -> Mapping[str, str] | str | None:
        """Get metadata value for collection.

        Return the value of the property ``key``. If ``key`` is ``None`` return
        a dict with all properties

        """
    # fmt: on
        meta = self.adapter.get_meta()
        meta["D:displayname"] = basename(self.path)
        meta["ICAL:calendar-color"] = self._get_color()
        return meta.get(key) if key else meta

    def set_meta(self, props: Mapping[str, str]) -> None:
        """Set metadata values for collection.

        ``props`` a dict with values for properties.

        """

    @property
    def last_modified(self) -> str:
        """Get the HTTP-datetime of when the collection was modified."""
        return strftime(
            "%a, %d %b %Y %H:%M:%S +0000", gmtime(self.adapter.last_modified())
        )


class Storage(BaseStorage):
    def __init__(self, configuration: "config.Configuration") -> None:
        """Initialize BaseStorage.

        ``configuration`` see ``radicale.config`` module.
        The ``configuration`` must not change during the lifetime of
        this object, it is kept as an internal reference.

        """
        super().__init__(configuration)
        self.adapters: list[Abook | IcsTask | Remind] = []
        self.filesystem_folder = expanduser(configuration.get("storage", "filesystem_folder"))

        if "remind_file" in configuration.options("storage"):
            zone = None
            if "remind_timezone" in configuration.options("storage"):
                zone = ZoneInfo(configuration.get("storage", "remind_timezone"))
            month = 15
            if "remind_lookahead_month" in configuration.options("storage"):
                month = configuration.get("storage", "remind_lookahead_month")
            self.adapters.append(Remind(configuration.get("storage", "remind_file"), zone, month=month))

        if "abook_file" in configuration.options("storage"):
            self.adapters.append(Abook(configuration.get("storage", "abook_file")))

        if "task_folder" in configuration.options("storage"):
            task_folder = configuration.get("storage", "task_folder")
            task_projects = []
            if "task_projects" in configuration.options("storage"):
                task_projects = configuration.get("storage", "task_projects").split(",")
            task_start = True
            if "task_start" in configuration.options("storage"):
                task_start = configuration.get("storage", "task_start")
            self.adapters.append(IcsTask(task_folder, task_projects=task_projects, start_task=task_start))

    # fmt: off
    def discover(
            self, path: str, depth: str = "0",
            child_context_manager:
            Callable[[str, str | None ], ContextManager[None]] | None = None,
            user_groups: set[str] = set([])) -> Iterable[types.CollectionOrItem]:
        """Discover a list of collections under the given ``path``.

        ``path`` is sanitized.

        If ``depth`` is "0", only the actual object under ``path`` is
        returned.

        If ``depth`` is anything but "0", it is considered as "1" and direct
        children are included in the result.

        The root collection "/" must always exist.

        """
    # fmt: on
        if path.count("/") < 3:
            yield MinCollection(path)

            if depth != "0":
                for adapter in self.adapters:
                    for filename in adapter.get_filesnames():
                        yield Collection(
                            filename.replace(self.filesystem_folder, ""),
                            filename,
                            adapter,
                        )
            return

        filename = join(self.filesystem_folder, dirname(path).strip("/"))
        collection = None

        for adapter in self.adapters:
            if filename in adapter.get_filesnames():
                collection = Collection(path, filename, adapter)
                break

        if not collection:
            return

        if path.endswith("/"):
            yield collection

            if depth != "0":
                for uid in collection._list():
                    yield collection._get(uid)
            return

        if basename(path) in collection._list():
            yield collection._get(basename(path))
            return

    # fmt: off
    def move(self, item: radicale_item.Item, to_collection: BaseCollection,
             to_href: str) -> None:
        """Move an object.

        ``item`` is the item to move.

        ``to_collection`` is the target collection.

        ``to_href`` is the target name in ``to_collection``. An item with the
        same name might already exist.

        """
    # fmt: on
        if not isinstance(item.collection, Collection) or not isinstance(to_collection, Collection):
            raise NotImplementedError

        if item.collection.path == to_collection.path and item.href == to_href:
            return

        to_collection.adapter.move_vobject(
            to_href, item.collection.filename, to_collection.filename
        )

    @types.contextmanager
    def acquire_lock(self, mode: str, user: str = "") -> Iterator[None]:
        """Set a context manager to lock the whole storage.

        ``mode`` must either be "r" for shared access or "w" for exclusive
        access.

        ``user`` is the name of the logged in user or empty.

        """
        yield

    def verify(self) -> bool:
        """Check the storage for errors."""
        return True
