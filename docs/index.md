# Welcome to Banks

[Banks](https://en.wikipedia.org/wiki/Arrival_(film)) is the linguist professor who will help you generate meaningful
LLM prompts using a template language that makes sense.

Banks is fundamentally [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/intro/) with additional functionalities
specifically designed to work with Large Language Models prompts. Similar to other template languages, Banks takes
in input a generic piece of text called _template_ and gives you back its _rendered_ version, where the generic bits
are replaced by actual data provided by the user.

## Features

* Banks currently supports all the features from Jinja2, see [Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/#jinja-filters.truncate).
* [Filters](prompt.md#filters): useful to manipulate the text during template rendering.
* [Extensions](prompt.md#extensions): useful to support custom functions (e.g. text generation via OpenAI).
* [Macros](prompt.md#macros): useful to implement complex logic in the template itself instead of Python code.

## Installation

Install the latest version of Banks using `pip`:

```sh
pip install banks
```

### Optional dependencies

Some functionalities require additional dependencies that need to be installed manually:

- `pip install simplemma` is required by the `lemmatize` filter

## License

`banks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
