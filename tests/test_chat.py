import pytest
from jinja2 import TemplateSyntaxError

from banks import Prompt
from banks.extensions.chat import _ContentBlockParser
from banks.types import CacheControl, ContentBlock, ContentBlockType


def test_wrong_tag():
    with pytest.raises(TemplateSyntaxError):
        Prompt("{% chat %}{% endchat %}")


def test_wrong_tag_params():
    with pytest.raises(TemplateSyntaxError):
        Prompt('{% chat foo="bar" %}{% endchat %}')


def test_wrong_role_type():
    with pytest.raises(TemplateSyntaxError):
        Prompt('{% chat role="does not exist" %}{% endchat %}')


def test_content_block_parser_init():
    p = _ContentBlockParser()
    assert p._parse_block_content is False
    assert p._content_blocks == []


def test_content_block_parser_single_with_cache_control():
    p = _ContentBlockParser()
    p.feed(
        '<content_block_txt>{"type":"text","cache_control":{"type":"ephemeral"},"text":"foo","source":null}</content_block_txt>'
    )
    assert p.content == [
        ContentBlock(type=ContentBlockType.text, cache_control=CacheControl(type="ephemeral"), text="foo", source=None)
    ]


def test_content_block_parser_single_no_cache_control():
    p = _ContentBlockParser()
    p.feed('<content_block_txt>{"type":"text","cache_control":null,"text":"foo","source":null}</content_block_txt>')
    assert p.content == "foo"


def test_content_block_parser_multiple():
    p = _ContentBlockParser()
    p.feed(
        '<content_block_txt>{"type":"text","cache_control":null,"text":"foo","source":null}</content_block_txt>'
        '<content_block_txt>{"type":"text","cache_control":null,"text":"bar","source":null}</content_block_txt>'
    )
    assert p.content == [
        ContentBlock(type=ContentBlockType.text, cache_control=None, text="foo", source=None),
        ContentBlock(type=ContentBlockType.text, cache_control=None, text="bar", source=None),
    ]


def test_content_block_parser_other_tags():
    p = _ContentBlockParser()
    p.feed("<some_tag>FOO</some_tag>")
    assert p.content == "FOO"
