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
