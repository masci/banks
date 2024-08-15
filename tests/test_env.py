# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import PackageLoader

from banks import env


def test_default_loader():
    assert type(env.loader) is PackageLoader
