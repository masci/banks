# Welcome to Banks

[Banks](https://en.wikipedia.org/wiki/Arrival_(film)) is the linguist professor who will help you generate meaningful
LLM prompts using a template language that makes sense.

Prompts are instrumental for the success of any LLM application, and Banks focuses around specific areas of their
lifecycle:

- :orange_book: **Templating**: Banks provides tools and functions to build prompts text and chat messages from generic blueprints.
- :tickets: **Versioning and metadata**: Banks supports attaching metadata to prompts to ease their management, and versioning is
first-class citizen.
- :file_cabinet: **Management**: Banks provides ways to store prompts on disk along with their metadata.

Banks is fundamentally [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/intro/) with additional functionalities
specifically designed to work with Large Language Models prompts. Similar to other template languages, Banks takes
in input a generic piece of text called _template_ and gives you back its _rendered_ version, where the generic bits
are replaced by actual data provided by the user and returned in a form that's
suitable for sending to an LLM, like plain text or chat messages.

## Features

Banks currently supports all the [features from Jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/#jinja-filters.truncate)
along with some additions specifically designed to help developers with LLM prompts:

- [Filters](prompt.md#filters): useful to manipulate the prompt text during template rendering.
- [Extensions](prompt.md#extensions): useful to support custom functions (e.g. text generation via LiteLLM).
- [Macros](prompt.md#macros): useful to implement complex logic in the template itself instead of Python code.

The library comes with its own set of features:

- [Template registry](registry.md): storage API for versioned prompts.
- [Configuration](config.md): useful to integrate the library with existing applications.

## Installation

Install the latest version of Banks using `pip`:

```sh
pip install banks
```

Some functionalities require additional dependencies that need to be installed manually:

- `pip install simplemma` is required by the `lemmatize` filter

## Examples

If you like to jump straight to the code:

- See a showcase of basic examples [here](examples.md).
- Check out the Cookbook:
  - :blue_book: [In-prompt chat completion](https://github.com/masci/banks/blob/main/cookbook/in_prompt_completion.ipynb)
  - :blue_book: [Prompt caching with Anthropic](https://github.com/masci/banks/blob/main/cookbook/Prompt_Caching_with_Anthropic.ipynb)
  - :blue_book: [Prompt versioning](https://github.com/masci/banks/blob/main/cookbook/Prompt_Versioning.ipynb)

## License

`banks` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
