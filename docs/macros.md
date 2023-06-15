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
