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

::: banks.filters.tool.tool
    options:
        show_root_full_path: false
        show_symbol_type_heading: false
        show_signature_annotations: false
        heading_level: 3

::: banks.filters.cache_control.cache_control
    options:
        show_root_full_path: false
        show_symbol_type_heading: false
        show_signature_annotations: false
        heading_level: 3

::: banks.filters.image.image
    options:
        show_root_full_path: false
        show_symbol_type_heading: false
        show_signature_annotations: false
        heading_level: 3

::: banks.filters.lemmatize.lemmatize
    options:
        show_root_full_path: false
        show_symbol_type_heading: false
        show_signature_annotations: false
        heading_level: 3

## Extensions

Extensions are custom functions that can be used to add new tags to the template engine.
Banks supports the following ones, specific for prompt engineering.

::: banks.extensions.docs.chat
    options:
        show_root_full_path: false
        show_symbol_type_heading: false
        show_signature_annotations: false
        heading_level: 3

::: banks.extensions.docs.completion
    options:
        show_root_full_path: false
        show_symbol_type_heading: false
        show_signature_annotations: false
        heading_level: 3

### `canary_word`

Insert into the prompt a canary word that can be checked later with `Prompt.canary_leaked()`
to ensure the original prompt was not leaked.

Example:
    ```python
    from banks import Prompt

    p = Prompt("{{canary_word}}Hello, World!")
    p.text()  ## outputs 'BANKS[5f0bbba4]Hello, World!'
    ```

## Macros

Macros are a way to implement complex logic in the template itself, think about defining functions but using Jinja
code instead of Python. Banks provides a set of macros out of the box that are useful in prompt engineering,
for example to generate a prompt and call OpenAI on-the-fly, during the template rendering.
Before using Banks' macros, you have to import them in your templates, see the examples below.
