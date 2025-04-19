from typing import cast

import pytest
from jinja2 import TemplateSyntaxError

from banks import Prompt
from banks.types import ContentBlock


def test_wrong_tag():
    with pytest.raises(TemplateSyntaxError):
        Prompt("{% chat %}{% endchat %}")


def test_wrong_tag_params():
    with pytest.raises(TemplateSyntaxError):
        Prompt('{% chat foo="bar" %}{% endchat %}')


def test_wrong_role_type():
    with pytest.raises(TemplateSyntaxError):
        Prompt('{% chat role="does not exist" %}{% endchat %}')


def test_blocks():
    p = Prompt('{% chat role="user" %}Tell me what you see: {{ picture | image }}{% endchat %}')
    messages = p.chat_messages({"picture": "http://foo.bar"})
    assert len(messages) == 1
    content = messages[0].content
    assert len(content) == 2
    assert content[0].type == "text"  # type: ignore
    assert content[1].type == "image_url"  # type: ignore


def test_blocks_newlines():
    p = Prompt("""{% chat role="system" %}
Some instructions:

1. Do this.
2. Then this.
3. Finally, that.
{% endchat %}""")
    messages = p.chat_messages()
    assert len(messages) == 1
    assert len(messages[0].content) == 1


def test_blocks_complex(data_path):
    p = Prompt("""
{% chat role="system" %}
Given a list of images and text from each image, please answer the question to the best of your ability.
{% endchat %}

{% chat role="user" %}
{% for image_path, text in images_and_texts %}
Here is some text: {{ text }}
And here is an image:
{{ image_path | image }}
{% endfor %}
{% endchat %}
    """)

    messages = p.chat_messages(
        {
            "images_and_texts": [
                (str(data_path / "1x1.png"), "This is the first page of the document"),
                (str(data_path / "1x1.png"), "This is the second page of the document"),
            ]
        }
    )
    assert len(messages) == 2

    blocks = cast(list[ContentBlock], messages[0].content)
    assert len(blocks) == 1
    assert blocks[0].type == "text"

    blocks = cast(list[ContentBlock], messages[1].content)
    assert len(blocks) == 4
    assert blocks[0].type == "text"
    assert blocks[1].type == "image_url"
    assert blocks[2].type == "text"
    assert blocks[3].type == "image_url"
