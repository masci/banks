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
