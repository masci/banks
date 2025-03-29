**Table of Contents**

- [Create a blog writing prompt](#create-a-blog-writing-prompt)
- [Create a summarizer prompt](#create-a-summarizer-prompt)
- [Lemmatize text while processing a template](#lemmatize-text-while-processing-a-template)
- [Use a LLM to generate a text while rendering a prompt](#use-a-llm-to-generate-a-text-while-rendering-a-prompt)
- [Render a prompt template as chat messages](#render-a-prompt-template-as-chat-messages)
- [Use prompt caching from Anthropic](#use-prompt-caching-from-anthropic)
- [Reuse templates from registries](#reuse-templates-from-registries)
- [Async support](#async-support)
- [Function calling directly from the prompt](#function-calling-directly-from-the-prompt)
- [Add images to the prompt for vision models](#add-images-to-the-prompt-for-vision-models)


## Create a blog writing prompt

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

The same prompt can be written in form of chat messages:
```py
prompt_text = """{% chat role="system" %}
I want you to act as a title generator for written pieces.
{% endchat %}

{% chat role="user" %}
Write a 500-word blog post on {{ topic }}.

Blog post:
{% endchat %}"""

p = Prompt(prompt_text)
print(p.chat_messages({"topic":"prompt engineering"}))
```

This will output the following:
```txt
[
  ChatMessage(role='system', content='I want you to act as a title generator for written pieces.\n'),
  ChatMessage(role='user', content='Write a 500-word blog post on .\n\nBlog post:\n')
]
```

## Create a summarizer prompt

Instead of hardcoding the content to summarize in the prompt itself, we can inject it
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

## Lemmatize text while processing a template

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

## Use a LLM to generate a text while rendering a prompt

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

## Render a prompt template as chat messages

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

## Use prompt caching from Anthropic

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

## Reuse templates from registries

We can get the same result as the previous example loading the prompt template from a registry
instead of hardcoding it into the Python code. For convenience, Banks comes with a few registry types
you can use to store your templates. For example, the `DirectoryTemplateRegistry` can load templates
from a directory in the file system. Suppose you have a folder called `templates` in the current path,
and the folder contains a file called `blog.jinja`. You can load the prompt template like this:

```py
from banks.registries import directory

populated_dir="./templates/"
registry = directory.DirectoryTemplateRegistry(populated_dir)
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

## Function calling directly from the prompt

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

## Add images to the prompt for vision models

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
