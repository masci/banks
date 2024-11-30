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

    The rendered value of the block can be assigned to a variable and accessed from another section of the prompt.

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
