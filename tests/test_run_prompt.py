# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from unittest import mock

from banks import Prompt, env


def test_run_prompt():
    p = Prompt.from_template("run_prompt.jinja")
    env.extensions["banks.extensions.generate.GenerateExtension"]._generate = mock.MagicMock(return_value="foo")

    assert p.text({"topic": "climate change"}) == "\n\nfoo\n"


def test_run_prompt_process():
    p = Prompt.from_template("run_prompt_process.jinja")
    env.extensions["banks.extensions.generate.GenerateExtension"]._generate = mock.MagicMock(return_value="foo bar baz")

    assert p.text({"topic": "climate change"}) == "FOO BAR BAZ"
