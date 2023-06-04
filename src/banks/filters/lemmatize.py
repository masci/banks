# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from simplemma import text_lemmatizer


def lemmatize(text: str) -> str:
    words = text_lemmatizer(text, "en")
    return " ".join(words)
