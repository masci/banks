# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from banks.errors import MissingDependencyError

try:
    from simplemma import text_lemmatizer  # type: ignore

    SIMPLEMMA_AVAIL = True
except ImportError:  # pragma: no cover
    SIMPLEMMA_AVAIL = False


def lemmatize(text: str) -> str:
    """
    Compute and return the lemmatization of the input. Language is hardcoded
    to English.

    Example:
        ```jinja
        {{"The dog is running" | lemmatize}}
        "the dog be run"
        ```

    Note:
        Simplemma must be manually installed to use this filter
    """
    if not SIMPLEMMA_AVAIL:
        err_msg = "simplemma is not available, please install it with 'pip install simplemma'"
        raise MissingDependencyError(err_msg)

    words = text_lemmatizer(text, "en")
    return " ".join(words)
