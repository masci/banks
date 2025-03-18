# banks

[![PyPI - Version](https://img.shields.io/pypi/v/banks.svg)](https://pypi.org/project/banks)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/banks.svg)](https://pypi.org/project/banks)
[![Coverage Status](https://coveralls.io/repos/github/masci/banks/badge.svg?branch=main)](https://coveralls.io/github/masci/banks?branch=main)

[![PyPI Release](https://github.com/masci/banks/actions/workflows/release.yml/badge.svg)](https://github.com/masci/banks/actions/workflows/release.yml)
[![test](https://github.com/masci/banks/actions/workflows/test.yml/badge.svg)](https://github.com/masci/banks/actions/workflows/test.yml)
[![docs](https://github.com/masci/banks/actions/workflows/docs.yml/badge.svg)](https://github.com/masci/banks/actions/workflows/docs.yml)

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

[Banks](https://en.wikipedia.org/wiki/Arrival_(film)) is the linguist professor who will help you generate meaningful
LLM prompts using a template language that makes sense. If you're still using `f-strings` for the job, keep reading.

Docs are available [here](https://masci.github.io/banks/).

![Banks Logo](./assets/banks.png)

-----

**Table of Contents**

- [banks](#banks)
  - [Installation](#installation)
  - [Features](#features)
  - [Cookbook](#cookbook)
  - [Examples](#examples)
    - [:point\_right: Render a prompt template as chat messages](#point_right-render-a-prompt-template-as-chat-messages)
    - [:point\_right: Add images to the prompt for vision models](#point_right-add-images-to-the-prompt-for-vision-models)
    - [:point\_right: Use a LLM to generate a text while rendering a prompt](#point_right-use-a-llm-to-generate-a-text-while-rendering-a-prompt)
    - [:point\_right: Function calling directly from the prompt](#point_right-function-calling-directly-from-the-prompt)
    - [:point\_right: Use prompt caching from Anthropic](#point_right-use-prompt-caching-from-anthropic)
  - [Reuse templates from registries](#reuse-templates-from-registries)
  - [Async support](#async-support)
  - [Contributing](#contributing)
  - [License](#license)

## Installation

```console
pip install banks

# install optional deps; litellm, redis
pip install "banks[all]"
```

## Features

Prompts are instrumental for the success of any LLM application, and Banks focuses around specific areas of their
lifecycle:
- :orange_book: **Templating**: Banks provides tools and functions to build prompts text and chat messages from generic blueprints.
- :tickets: **Versioning and metadata**: Banks supports attaching metadata to prompts to ease their management, and versioning is
first-class citizen.
- :file_cabinet: **Management**: Banks provides ways to store prompts on disk along with their metadata.

## Cookbook

- :blue_book: [In-prompt chat completion](./cookbook/in_prompt_completion.ipynb)
- :blue_book: [Prompt caching with Anthropic](./cookbook/Prompt_Caching_with_Anthropic.ipynb)
- :blue_book: [Prompt versioning](./cookbook/Prompt_Versioning.ipynb)

## Examples

For a more extensive set of code examples, [see the documentation page](https://masci.github.io/banks/examples/).

### :point_right: Render a prompt template as chat messages

You'll find yourself feeding an LLM a list of chat messages instead of plain text
more often than not. Banks will help you remove the boilerplate by defining the
messages already at the prompt level.

```py
from banks import Prompt


prompt_template = """
{% chat role="system" %}
You are a {{ persona }}.
{% endchat %}

{% chat role="user" %}
Hello, how are you?
{% endchat %}
"""

p = Prompt(prompt_template)
print(p.chat_messages({"persona": "helpful assistant"}))

# Output:
# [
#   ChatMessage(role='system', content='You are a helpful assistant.\n'),
#   ChatMessage(role='user', content='Hello, how are you?\n')
# ]
```

### :point_right: Add images to the prompt for vision models

If you're working with a multimodal model, you can include images directly in the prompt,
and Banks will do the job needed to upload them when rendering the chat messages:

```py
import litellm

from banks import Prompt

prompt_template = """
{% chat role="user" %}
Guess where is this place.
{{ picture | image }}
{%- endchat %}
"""

pic_url = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/CorcianoMar302024_01.jpg/1079px-CorcianoMar302024_01.jpg"
)
# Alternatively, load the image from disk
# pic_url = "/Users/massi/Downloads/CorcianoMar302024_01.jpg"

p = Prompt(prompt_template)
as_dict = [msg.model_dump(exclude_none=True) for msg in p.chat_messages({"picture": pic_url})]
r = litellm.completion(model="gpt-4-vision-preview", messages=as_dict)

print(r.choices[0].message.content)
```

### :point_right: Use a LLM to generate a text while rendering a prompt

Sometimes it might be useful to ask another LLM to generate examples for you in a
few-shots prompt. Provided you have a valid OpenAI API key stored in an env var
called `OPENAI_API_KEY` you can ask Banks to do something like this (note we can
annotate the prompt using comments - anything within `{# ... #}` will be removed
from the final prompt):

```py
from banks import Prompt


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
print(p.text({"topic": "climate change"}))
```

The output would be something similar to the following:
```txt
Generate a tweet about the topic climate change with a positive sentiment.
Examples:
- "Feeling grateful for the sunshine today! 🌞 #thankful #blessed"
- "Just had a great workout and feeling so energized! 💪 #fitness #healthyliving"
- "Spent the day with loved ones and my heart is so full. 💕 #familytime #grateful"
```

> [!IMPORTANT]
> The `completion` extension uses [LiteLLM](https://github.com/BerriAI/litellm) under the hood, and provided you have the
> proper environment variables set, you can use any model from the supported [model providers](https://docs.litellm.ai/docs/providers).

> [!NOTE]
> Banks uses a cache to avoid generating text again for the same template with the same context. By default
> the cache is in-memory but it can be customized.

### :point_right: Function calling directly from the prompt

Banks provides a filter `tool` that can be used to convert a callable passed to a prompt into an LLM function call.
Docstrings are used to describe the tool and its arguments, and during prompt rendering Banks will perform all the LLM
roundtrips needed in case the model wants to use a tool within a `{% completion %}` block. For example:

```py
import platform

from banks import Prompt


def get_laptop_info():
    """Get information about the user laptop.

    For example, it returns the operating system and version, along with hardware and network specs."""
    return str(platform.uname())


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

print(p.text({"query": "Can you guess the name of my laptop?", "get_laptop_info": get_laptop_info}))
# Output:
# Based on the information provided, the name of your laptop is likely "MacGiver."
```

### :point_right: Use prompt caching from Anthropic

Several inference providers support prompt caching to save time and costs, and Anthropic in particular offers
fine-grained control over the parts of the prompt that we want to cache. With Banks this is as simple as
using a template filter:

```py
prompt_template = """
{% chat role="user" %}
Analyze this book:

{# Only this part of the chat message (the book content) will be cached #}
{{ book | cache_control("ephemeral") }}

What is the title of this book? Only output the title.
{% endchat %}
"""

p = Prompt(prompt_template)
print(p.chat_messages({"book":"This is a short book!"}))

# Output:
# [
#   ChatMessage(role='user', content=[
#      ContentBlock(type='text', text='Analyze this book:\n\n'),
#      ContentBlock(type='text', cache_control=CacheControl(type='ephemeral'), text='This is a short book!'),
#      ContentBlock(type='text', text='\n\nWhat is the title of this book? Only output the title.\n')
#   ])
# ]
```

The output of `p.chat_messages()` can be fed to the Anthropic client directly.

## Reuse templates from registries

We can get the same result as the previous example loading the prompt template from a registry
instead of hardcoding it into the Python code. For convenience, Banks comes with a few registry types
you can use to store your templates. For example, the `DirectoryTemplateRegistry` can load templates
from a directory in the file system. Suppose you have a folder called `templates` in the current path,
and the folder contains a file called `blog.jinja`. You can load the prompt template like this:

```py
from banks import Prompt
from banks.registries import DirectoryTemplateRegistry

registry = DirectoryTemplateRegistry(populated_dir)
prompt = registry.get(name="blog")

print(prompt.text({"topic": "retrogame computing"}))
```

## Async support

To run banks within an `asyncio` loop you have to do two things:
1. set the environment variable `BANKS_ASYNC_ENABLED=true`.
2. use the `AsyncPrompt` class that has an awaitable `run` method.

Example:
```python
from banks import AsyncPrompt

async def main():
    p = AsyncPrompt("Write a blog article about the topic {{ topic }}")
    result = await p.text({"topic": "AI frameworks"})
    print(result)

asyncio.run(main())
```

## Contributing

Contributions are very welcome, the [CONTRIBUTING.md](CONTRIBUTING.md) file contains all the details
about how to do it.

## License

`banks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
