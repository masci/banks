# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
import html
import os

import requests
from deprecated import deprecated
from jinja2 import nodes
from jinja2.ext import Extension


@deprecated(version="1.3.0", reason="This extension is deprecated, use {% completion %} instead.")
class HFInferenceEndpointsExtension(Extension):
    """
    `inference_endpoint` can be used to call the Hugging Face Inference Endpoint API
    passing a prompt to get back some content.

    Deprecated:
        This extension is deprecated, use `{% completion %}` instead.

    Example:
        ```jinja
        {% inference_endpoint "write a tweet with positive sentiment", "https://foo.aws.endpoints.huggingface.cloud" %}
        Life is beautiful, full of opportunities & positivity
        ```
    """

    # a set of names that trigger the extension.
    tags = {"inference_endpoint"}  # noqa

    def parse(self, parser):
        # We get the line number of the first token so that we can give
        # that line number to the nodes we create by hand.
        lineno = next(parser.stream).lineno

        # The args passed to the extension:
        # - the prompt text used to generate new text
        args = [parser.parse_expression()]
        # - second param after the comma,  the inference endpoint URL
        parser.stream.skip_if("comma")
        args.append(parser.parse_expression())

        return nodes.Output([self.call_method("_call_endpoint", args)]).set_lineno(lineno)

    def _call_endpoint(self, text, endpoint):
        """
        Helper callback.
        """
        access_token = os.environ.get("HF_ACCESS_TOKEN")
        response = requests.post(
            endpoint, json={"inputs": text}, headers={"Authorization": f"Bearer {access_token}"}, timeout=30
        )
        response_body = response.json()

        if response_body:
            return html.unescape(response_body[0].get("generated_text", ""))
        return ""
