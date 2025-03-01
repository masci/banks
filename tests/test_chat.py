import pytest
from jinja2 import TemplateSyntaxError

from banks import Prompt


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
