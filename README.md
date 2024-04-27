# banks

[![PyPI - Version](https://img.shields.io/pypi/v/banks.svg)](https://pypi.org/project/banks)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/banks.svg)](https://pypi.org/project/banks)

[![PyPI Release](https://github.com/masci/banks/actions/workflows/release.yml/badge.svg)](https://github.com/masci/banks/actions/workflows/release.yml)
[![test](https://github.com/masci/banks/actions/workflows/test.yml/badge.svg)](https://github.com/masci/banks/actions/workflows/test.yml)
[![docs](https://github.com/masci/banks/actions/workflows/docs.yml/badge.svg)](https://github.com/masci/banks/actions/workflows/docs.yml)

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/)

[Banks](https://en.wikipedia.org/wiki/Arrival_(film)) is the linguist professor who will help you generate meaningful
LLM prompts using a template language that makes sense. If you're still using `f-strings` for the job, keep reading.

Docs are available [here](https://masci.github.io/banks/).

-----

**Table of Contents**

- [banks](#banks)
  - [Installation](#installation)
  - [Examples](#examples)
    - [Generate a blog writing prompt](#generate-a-blog-writing-prompt)
    - [Generate a summarizer prompt](#generate-a-summarizer-prompt)
    - [Lemmatize text while processing a template](#lemmatize-text-while-processing-a-template)
    - [Use a LLM to generate a text while rendering a prompt](#use-a-llm-to-generate-a-text-while-rendering-a-prompt)
    - [Go meta: create a prompt and `generate` its response](#go-meta-create-a-prompt-and-generate-its-response)
    - [Go meta(meta): process a LLM response](#go-metameta-process-a-llm-response)
    - [Reuse templates from files](#reuse-templates-from-files)
    - [Async support](#async-support)
  - [License](#license)

## Installation

```console
pip install banks
```

## Examples

### Generate a blog writing prompt

Given a generic template to instruct an LLM to generate a blog article, we
use Banks to generate the actual prompt on our topic of choice, "retrogame computing":

```py
from banks import Prompt


p = Prompt("Write a 500-word blog post on {{ topic }}.\n\nBlog post:")
topic = "retrogame computing"
print(p.text({"topic": topic}))
```

This will print the following text, that can be pasted directly into Chat-GPT:

```txt
Write a 500-word blog post on retrogame computing.

Blog post:
```

### Generate a summarizer prompt

Instead of hardcoding the content to summarize in the prompt itself, we can generate it
starting from a generic one:


```py
from banks import Prompt


prompt_template = """
Summarize the following documents:
{% for document in documents %}
{{ document }}
{% endfor %}
Summary:
"""

# In a real-world scenario, these would be loaded as external resources from files or network
documents = [
    "A first paragraph talking about AI",
    "A second paragraph talking about climate change",
    "A third paragraph talking about retrogaming"
]

p = Prompt(prompt_template)
print(p.text({"documents": documents}))
```

The resulting prompt:

```txt
Summarize the following documents:

A first paragraph talking about AI

A second paragraph talking about climate change

A third paragraph talking about retrogaming

Summary:
```

### Lemmatize text while processing a template

Banks comes with predefined filters you can use to process data before generating the
prompt. Say you want to use a lemmatizer on a document before summarizing it, first
you need to install `simplemma`:

```sh
pip install simplemma
```

then you can use the `lemmatize` filter in your templates like this:

```py
from banks import Prompt


prompt_template = """
Summarize the following document:
{{ document | lemmatize }}
Summary:
"""

p = Prompt(prompt_template)
print(p.text({"document": "The cats are running"}))
```

the output would be:

```txt
Summarize the following document:
the cat be run
Summary:
```

### Use a LLM to generate a text while rendering a prompt

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

> [!TIP]
> The `generate` extension uses [LiteLLM](https://github.com/BerriAI/litellm) under the hood, and provided you have the
> proper environment variables set, you can use any model from the supported [model providers](https://docs.litellm.ai/docs/providers).

### Go meta: create a prompt and `generate` its response

We can leverage Jinja's macro system to generate a prompt, send the result to OpenAI and get a response.
Let's bring back the blog writing example:

```py
from banks import Prompt

prompt_template = """
{% from "banks_macros.jinja" import run_prompt with context %}

{%- call run_prompt() -%}
Write a 500-word blog post on {{ topic }}

Blog post:
{%- endcall -%}
"""

p = Prompt(prompt_template)
print(p.text({"topic": "climate change"}))
```

The snippet above won't print the prompt, instead will generate the prompt text

```
Write a 500-word blog post on climate change

Blog post:
```

and will send it to OpenAI using the `generate` extension, eventually returning its response:

```
Climate change is a phenomenon that has been gaining attention in recent years...
...
```

### Go meta(meta): process a LLM response

When generating a response from a prompt template, we can take a step further and
post-process the LLM response by assinging it to a variable and applying filters
to it:

```py
from banks import Prompt

prompt_template = """
{% from "banks_macros.jinja" import run_prompt with context %}

{%- set prompt_result %}
{%- call run_prompt() -%}
Write a 500-word blog post on {{ topic }}

Blog post:
{%- endcall -%}
{%- endset %}

{# nothing is returned at this point: the variable 'prompt_result' contains the result #}

{# let's use the prompt_result variable now #}
{{ prompt_result | upper }}
"""

p = Prompt(prompt_template)
print(p.text({"topic": "climate change"}))
```

The final answer from the LLM will be printed, this time all in uppercase.

### Reuse templates from files

We can get the same result as the previous example loading the prompt template from file
instead of hardcoding it into the Python code. For convenience, Banks comes with a few
default templates distributed the package. We can load those templates from file like this:

```py
from banks import Prompt


p = Prompt.from_template("blog.jinja")
topic = "retrogame computing"
print(p.text({"topic": topic}))
```

### Async support

To run banks within an `asyncio` loop you have to do two things:
1. set the environment variable `BANKS_ASYNC_ENABLED=true`.
2. use the `AsyncPrompt` class that has an awaitable `run` method.

Example:
```python
from banks import AsyncPrompt

async def main():
    p = AsyncPrompt.from_template("blog.jinja")
    result = await p.text({"topic": "AI frameworks"})
    print(result)

asyncio.run(main())
```

## License

`banks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
