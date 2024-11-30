import pytest

from banks import Prompt

from .conftest import anthropic_api_key_set, openai_api_key_set


@pytest.mark.e2e
@openai_api_key_set
def test_completion_openai():
    prompt_template = """
    {% set examples %}
    {% completion model="gpt-3.5-turbo-0125" %}
      {% chat role="system" %}You are a helpful assistant{% endchat %}
      {% chat role="user" %}Generate a bullet list of 3 tweets with a positive sentiment.{% endchat %}
    {% endcompletion %}
    {% endset %}

    {# output the response content #}
    Generate a tweet about the topic {{ topic }} with a positive sentiment.
    Examples:
    {{ examples }}
    """

    p = Prompt(prompt_template)
    assert "Generate a tweet about the topic LLM" in p.text({"topic": "LLM"})


@pytest.mark.e2e
@anthropic_api_key_set
def test_completion_anthropic():
    prompt_template = """
    {% set examples %}
    {% completion model="claude-3-haiku-20240307" %}
      {% chat role="system" %}You are a helpful assistant{% endchat %}
      {% chat role="user" %}Generate a bullet list of 3 tweets with a positive sentiment.{% endchat %}
    {% endcompletion %}
    {% endset %}

    {# output the response content #}
    Generate a tweet about the topic {{ topic }} with a positive sentiment.
    Examples:
    {{ examples }}
    """

    p = Prompt(prompt_template)
    assert "Generate a tweet about the topic LLM" in p.text({"topic": "LLM"})
