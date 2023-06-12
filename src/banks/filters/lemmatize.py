# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from banks.errors import MissingDependencyError

try:
    from simplemma import text_lemmatizer

    simplemma_avail = True
except ImportError:
    simplemma_avail = False


def lemmatize(text: str) -> str:
    if not simplemma_avail:
        err_msg = "simplemma is not available, please install it with 'pip install simplemma'"
        raise MissingDependencyError(err_msg)

    words = text_lemmatizer(text, "en")
    return " ".join(words)
