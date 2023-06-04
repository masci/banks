# banks

[![PyPI - Version](https://img.shields.io/pypi/v/banks.svg)](https://pypi.org/project/banks)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/banks.svg)](https://pypi.org/project/banks)

Banks is a Python library to generate LLM prompts using a template language.

-----

**Table of Contents**

- [banks](#banks)
  - [Installation](#installation)
  - [Examples](#examples)
    - [Generate a blog writing prompt](#generate-a-blog-writing-prompt)
    - [Reuse templates from files](#reuse-templates-from-files)
    - [Generate a summarizer prompt](#generate-a-summarizer-prompt)
    - [Lemmatize text while processing a template](#lemmatize-text-while-processing-a-template)
    - [Use a LLM to generate a text while rendering a prompt](#use-a-llm-to-generate-a-text-while-rendering-a-prompt)
  - [License](#license)

## Installation

```console
pip install banks
```

## Examples

### Generate a blog writing prompt

Given a generic template to instruct an LLM to generate a blog article, we
use Banks to generate the actual prompt on our topic of choice, "Retrogame computing":

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

### Generate a summarizer prompt

Instead of hardcoding the content to summarize in the prompt itself, we can generate it
starting from a generic one:


```py
from banks import Prompt


prompt_template = """
Summarize the following documents:
{% for document in documents %}
{{document}}
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
prompt. Say you want to use a lemmatizer on a document you want to summarize:

```py
from banks import Prompt


prompt_template = """
Summarize the following document:
{{document | lemmatize}}
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

## License

`banks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
