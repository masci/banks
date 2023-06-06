# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from banks import env
from banks.loader import MultiLoader


def test_default_loader():
    assert type(env.loader) == MultiLoader
