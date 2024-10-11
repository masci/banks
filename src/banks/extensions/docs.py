# This module exists for documentation purpose only


def chat(role: str):  # pylint: disable=W0613
    """
    Text inside `chat` tags will be rendered as JSON strings representing chat messages. Calling `Prompt.chat_messages`
    will return a list of `ChatMessage` instances.

    Example:
        ```jinja
        {% chat role="system" %}
        You are a helpful assistant.
        {% endchat %}

        {% chat role="user" %}
        Hello, how are you?
        {% endchat %}
        ```
    """


def completion(model_name: str):  # pylint: disable=W0613
    """
    `completion` can be used to send to the LLM the content of the block in form of messages.

    The rendered value of the block can be used as is but it's usually more useful to
    assign it to a variable and access it from another section of the prompt.

    Example:
        ```jinja
        {% set response %}
        {% completion model="gpt-3.5-turbo-0125" %}
        {% chat role="user" %}You are a helpful assistant{% endchat %}
        {% endcompletion %}
        {% endset %}

        {# output the response content #}
        {{ response }}
        ```
    """


def generate(model_name: str):  # pylint: disable=W0613
    """
    `generate` can be used to call the LiteLLM API passing the tag text as a prompt and get back some content.

    Example:
        ```jinja
        {% generate "write a tweet with positive sentiment" "gpt-3.5-turbo" %}
        Feeling grateful for all the opportunities that come my way! #positivity #productivity
        ```
    """
