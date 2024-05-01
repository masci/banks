## Filters

Filters are Python functions that are called during the rendering of a certain tag. For example, if a prompt template
contains the tag:

```jinja
{{ 'hello' | upper }}
```

a Python function named `upper` (in this case provided by Jinja) will be called passing the string 'hello' as a
parameter, and its return value will replace the tag in the final text:

```python
from banks import Prompt

p = Prompt("{{ 'hello' | upper }}")
p.text()  ## outputs 'HELLO'
```

In addition to all the [builtin filters](https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-builtin-filters)
provided by Jinja, Banks supports the following ones, specific for prompt engineering.


::: banks.filters.lemmatize.lemmatize

## Extensions

Extensions are custom functions that can be used to add new tags to the template engine.
Banks supports the following ones, specific for prompt engineering.

::: banks.extensions.generate
    options:
        show_root_heading: false

### `{{canary_word}}`

Insert into the prompt a canary word that can be checked later with `Prompt.canary_leaked()`
to ensure the original prompt was not leaked.

## Macros

Macros are a way to implement complex logic in the template itself, think about defining functions but using Jinja
code instead of Python. Banks provides a set of macros out of the box that are useful in prompt engineering,
for example to generate a prompt and call OpenAI on-the-fly, during the template rendering.
In order to use Banks' macros, you have to import them in your templates, see the examples below.

<h2 class="doc-heading"><code>run_prompt</code></h2>

Similar to `generate`, `run_prompt` will call OpenAI passing the whole block content as the input. The block
content can in turn contain Jinja tags, which makes this macro very powerful. In the example below, during
the template rendering the value of `{{ topic }}` will be processed before sending the resulting block to
`run_prompt`.

```jinja
{% from "banks_macros.jinja" import run_prompt with context %}

{% call run_prompt() %}
Write a 500-word blog post on {{ topic }}
{% endcall %}
```

When the rendering is done, the entire `call` block will be replaced with OpenAI's response.
