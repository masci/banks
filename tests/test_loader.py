# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from unittest import mock

from banks import env
from banks.loader import MultiLoader

from jinja2.loaders import PackageLoader, FileSystemLoader


def test_defaults():
    l = MultiLoader()
    assert len(l._loaders) == 1
    loader, prio = l._loaders[0]
    assert type(loader) == PackageLoader
    assert prio == 1


def test_add_loader():
    l = MultiLoader()

    # add a loader, default priority
    test_loader = FileSystemLoader("")
    l.add_loader(test_loader)
    assert l._loaders[1][0] == test_loader
    assert l._loaders[1][1] == 100

    # add another one with priority
    another_loader = FileSystemLoader("")
    l.add_loader(another_loader, 50)
    assert l._loaders[2][0] == another_loader
    assert l._loaders[2][1] == 50


def test_get_source():
    l = MultiLoader()
    # remove the default loader
    l._loaders = []

    l1 = mock.MagicMock()
    l.add_loader(l1, 50)
    l2 = mock.MagicMock()
    l.add_loader(l2, 20)

    l.get_source(env, "foo")
    l1.get_source.assert_not_called()
    l2.get_source.assert_called_with(env, "foo")
