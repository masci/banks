# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
class MissingDependencyError(Exception):
    pass


class AsyncError(Exception):
    pass


class CanaryWordError(Exception):
    pass
