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

-----

**Table of Contents**

- [banks](#banks)
  - [Installation](#installation)
  - [Features](#features)
  - [Cookbooks](#cookbooks)
  - [Examples](#examples)
    - [:point\_right: Use a LLM to generate a text while rendering a prompt](#point_right-use-a-llm-to-generate-a-text-while-rendering-a-prompt)
    - [:point\_right: Render a prompt template as chat messages](#point_right-render-a-prompt-template-as-chat-messages)
    - [:point\_right: Use prompt caching from Anthropic](#point_right-use-prompt-caching-from-anthropic)
  - [Reuse templates from registries](#reuse-templates-from-registries)
  - [Async support](#async-support)
  - [License](#license)

## Installation

```console
pip install banks
```

## Features

Prompts are instrumental for the success of any LLM application, and Banks focuses around specific areas of their
lifecycle:
- :orange_book: **Templating**: Banks provides tools and functions to build prompts text and chat messages from generic blueprints.
- :tickets: **Versioning and metadata**: Banks supports attaching metadata to prompts to ease their management, and versioning is
first-class citizen.
- :file_cabinet: **Management**: Banks provides ways to store prompts on disk along with their metadata.

## Cookbooks

- :blue_book: [In-prompt chat completion](https://github.com/masci/banks/blob/main/cookbooks/in_prompt_completion.ipynb)
- :blue_book: [Prompt caching with Anthropic](./cookbooks/Prompt_Caching_with_Anthropic.ipynb)
- :blue_book: [Prompt versioning](./cookbooks/Prompt_Versioning.ipynb)

## Examples

For a more extensive set of code examples, [see the documentation page](https://masci.github.io/banks/examples/).

### :point_right: Use a LLM to generate a text while rendering a prompt

Sometimes it might be useful to ask another LLM to generate examples for you in a
few-shot prompt. Provided you have a valid OpenAI API key stored in an env var
called `OPENAI_API_KEY` you can ask Banks to do something like this (note we can
annotate the prompt using comments - anything within `{# ... #}` will be removed
from the final prompt):

```py
from banks import Prompt


prompt_template = """
Generate a tweet about the topic {{ topic }} with a positive sentiment.

{#
    This is for illustration purposes only, there are better and cheaper ways
    to generate examples for a few-shots prompt.
#}
Examples:
{% for number in range(3) %}
- {% generate "write a tweet with positive sentiment" "gpt-3.5-turbo" %}
{% endfor %}
"""

p = Prompt(prompt_template)
print(p.text({"topic": "climate change"}))
```

The output would be something similar to the following:
```txt
Generate a tweet about the topic climate change with a positive sentiment.


Examples:

- "Feeling grateful for the amazing capabilities of #GPT3.5Turbo! It's making my work so much easier and efficient. Thank you, technology!" #positivity #innovation

- "Feeling grateful for all the opportunities that come my way! With #GPT3.5Turbo, I am able to accomplish tasks faster and more efficiently. #positivity #productivity"

- "Feeling grateful for all the wonderful opportunities and experiences that life has to offer! #positivity #gratitude #blessed #gpt3.5turbo"
```

If you paste Banks' output into ChatGPT you would get something like this:
```txt
Climate change is a pressing global issue, but together we can create positive change! Let's embrace renewable energy, protect our planet, and build a sustainable future for generations to come. 🌍💚 #ClimateAction #PositiveFuture
```

> [!IMPORTANT]
> The `generate` extension uses [LiteLLM](https://github.com/BerriAI/litellm) under the hood, and provided you have the
> proper environment variables set, you can use any model from the supported [model providers](https://docs.litellm.ai/docs/providers).

> [!NOTE]
> Banks uses a cache to avoid generating text again for the same template with the same context. By default
> the cache is in-memory but it can be customized.

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

## License

`banks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
