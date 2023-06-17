# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import os
from pathlib import Path
from unittest import mock

import pytest

from banks import Prompt, env


def _get_data(name):
    here = Path(os.path.dirname(os.path.abspath(__file__)))
    with open(here / "test_default_templates" / name) as f:
        return f.read()


def test_blog():
    p = Prompt.from_template("blog.jinja")
    assert _get_data("blog.jinja.out") == p.text({"topic": "climate change"})


def test_summarize():
    p = Prompt.from_template("summarize.jinja")
    documents = [
        "A first paragraph talking about AI",
        "A second paragraph talking about climate change",
        "A third paragraph talking about retrogaming",
    ]
    assert _get_data("summarize.jinja.out") == p.text({"documents": documents})


def test_summarize_lemma():
    pytest.importorskip("simplemma")

    p = Prompt.from_template("summarize_lemma.jinja")
    assert _get_data("summarize_lemma.jinja.out") == p.text({"document": "The cats are running"})


def test_generate_tweet():
    p = Prompt.from_template("generate_tweet.jinja")
    env.extensions["banks.extensions.generate.GenerateExtension"]._generate = mock.MagicMock(return_value="foo")

    assert _get_data("generate_tweet.jinja.out") == p.text({"topic": "climate change"})
