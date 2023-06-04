# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from jinja2 import nodes, lexer
from jinja2.ext import Extension
import openai

CHAT_MODELS = [
    "gpt-4",
    "gpt-4-32k",
    "gpt-3.5-turbo",
]
DEFAULT_MODEL = "gpt-3.5-turbo"


class GenerateExtension(Extension):
    # a set of names that trigger the extension.
    tags = {"generate"}

    def parse(self, parser):
        # We get the line number of the first token so that we can give
        # that line number to the nodes we create by hand.
        lineno = next(parser.stream).lineno

        # The args passed to the extension:
        # - the prompt text used to generate new text
        # - (optional) the name of the model use to generate new text
        args = [parser.parse_expression()]

        return nodes.Output([self.call_method('_generate', args)]).set_lineno(lineno)

    def _generate(self, text, model_name=DEFAULT_MODEL):
        """Helper callback."""
        content = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text},
            ],
            temperature=0.5,
        )["choices"][0]["message"]["content"]

        return content
