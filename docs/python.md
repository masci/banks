
::: banks.prompt.Prompt
    options:
      inherited_members: true

::: banks.prompt.AsyncPrompt

## Default macros

Banks' package comes with default template macros you can use in your prompts.


### `run_prompt`


We can use `run_prompt` in our templates to generate a prompt, send the result to the LLM and get a response.
Take this prompt for example:

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

In this case, Banks will generate internally the prompt text

```
Write a 500-word blog post on climate change

Blog post:
```

but instead of returning it, will send it to the LLM using the `generate` extension under the hood, eventually
returning the final response:

```
Climate change is a phenomenon that has been gaining attention in recent years...
...
```
