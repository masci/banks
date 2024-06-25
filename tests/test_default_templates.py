# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import os
from pathlib import Path
from unittest import mock

import pytest

from banks import env
from banks.registries import DirectoryTemplateRegistry


@pytest.fixture
def registry(tmp_path):
    for fp in (Path(__file__).parent / "templates").iterdir():
        with open(tmp_path / fp.name, "w") as f:
            f.write(fp.read_text())

    return DirectoryTemplateRegistry(tmp_path)


def _get_data(name):
    here = Path(os.path.dirname(os.path.abspath(__file__)))
    with open(here / "test_default_templates" / name) as f:
        return f.read()


def test_blog(registry):
    p = registry.get(name="blog")
    assert _get_data("blog.jinja.out") == p.text({"topic": "climate change"})


def test_summarize(registry):
    p = registry.get(name="summarize")
    documents = [
        "A first paragraph talking about AI",
        "A second paragraph talking about climate change",
        "A third paragraph talking about retrogaming",
    ]
    assert _get_data("summarize.jinja.out") == p.text({"documents": documents})


def test_summarize_lemma(registry):
    pytest.importorskip("simplemma")

    p = registry.get(name="summarize_lemma")
    assert _get_data("summarize_lemma.jinja.out") == p.text({"document": "The cats are running"})


def test_generate_tweet(registry):
    p = registry.get(name="generate_tweet")
    ext_name = "banks.extensions.generate.GenerateExtension"
    env.extensions[ext_name]._generate = mock.MagicMock(return_value="foo")  # type:ignore

    assert _get_data("generate_tweet.jinja.out") == p.text({"topic": "climate change"})
