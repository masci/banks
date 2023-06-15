# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from unittest import mock

from jinja2.loaders import FileSystemLoader, PackageLoader

from banks import env
from banks.loader import MultiLoader


def test_defaults():
    test_loader = MultiLoader()
    assert len(test_loader._loaders) == 2
    loader, prio = test_loader._loaders[0]
    assert type(loader) == PackageLoader
    assert prio == 10
    loader, prio = test_loader._loaders[1]
    assert type(loader) == FileSystemLoader
    assert prio == 20


def test_add_loader():
    test_loader = MultiLoader()

    # add a loader, default priority
    fs_loader = FileSystemLoader("")
    test_loader.add_loader(fs_loader)
    assert test_loader._loaders[2][0] == fs_loader
    assert test_loader._loaders[2][1] == 100

    # add another one with priority
    another_loader = FileSystemLoader("")
    test_loader.add_loader(another_loader, 50)
    assert test_loader._loaders[3][0] == another_loader
    assert test_loader._loaders[3][1] == 50


def test_get_source():
    test_loader = MultiLoader()
    # remove the default loader
    test_loader._loaders = []

    l1 = mock.MagicMock()
    test_loader.add_loader(l1, 50)
    l2 = mock.MagicMock()
    test_loader.add_loader(l2, 20)

    test_loader.get_source(env, "foo")
    l1.get_source.assert_not_called()
    l2.get_source.assert_called_with(env, "foo")
