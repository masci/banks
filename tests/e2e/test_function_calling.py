import platform

import pytest

from banks import Prompt

from .conftest import anthropic_api_key_set, openai_api_key_set


def get_laptop_info():
    """Get information about the user laptop.

    For example, it returns the operating system and version, along with hardware and network specs."""
    return str(platform.uname())


@pytest.mark.e2e
@openai_api_key_set
def test_function_call_openai():
    p = Prompt("""
    {% set response %}
    {% completion model="gpt-3.5-turbo-0125" %}
        {% chat role="user" %}{{ query }}{% endchat %}
        {{ get_laptop_info | tool }}
    {% endcompletion %}
    {% endset %}

    {# the variable 'response' contains the result #}

    {{ response }}
    """)

    res = p.text({"query": "Can you guess the name of my laptop?", "get_laptop_info": get_laptop_info})
    assert res


@pytest.mark.e2e
@anthropic_api_key_set
def test_function_call_anthropic():
    p = Prompt("""
    {% set response %}
    {% completion model="claude-3-5-sonnet-20240620" %}
        {% chat role="user" %}{{ query }}{% endchat %}
        {{ get_laptop_info | tool }}
    {% endcompletion %}
    {% endset %}

    {# the variable 'response' contains the result #}

    {{ response }}
    """)

    res = p.text({"query": "Can you guess the name of my laptop? Use tools.", "get_laptop_info": get_laptop_info})
    assert res
