# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import Optional

from .config import async_enabled
from .env import env
from .errors import AsyncError
from .utils import generate_canary_word


class BasePrompt:
    def __init__(self, text: str, canary_word: Optional[str] = None) -> None:
        """
        Prompt constructor.

        Parameters:
            text: The template text
            canary_word: The string to use for the `{{canary_word}}` extension. If `None`, a default string will be
                generated

        """
        self._template = env.from_string(text)
        self.defaults = {"canary_word": canary_word or generate_canary_word()}

    def _get_context(self, data: Optional[dict]) -> dict:
        if data is None:
            return self.defaults
        return data | self.defaults

    def canary_leaked(self, text: str) -> bool:
        """
        Returns whether the canary word is present in `text`, signalling the prompt might have leaked.
        """
        return self.defaults["canary_word"] in text

    @classmethod
    def from_template(cls, name: str) -> "BasePrompt":
        """
        Create a prompt instance from a template.

        Prompt templates can be really long and at some point you might want to store them on files. To avoid the
        boilerplate code to read a file and pass the content as strings to the constructor, `Prompt`s can be
        initialized by just passing the name of the template file, provided that the file is stored in a folder called
        `templates` in the current path:

        ```
        .
        └── templates
            └── foo.jinja
        ```

        The code would be the following:

        ```py
        from banks import Prompt

        p = Prompt.from_template("foo.jinja")
        prompt_text = p.text(data={"foo": "bar"})
        ```

        !!! warning
            Banks comes with its own set of default templates (see below) which takes precedence over the
            ones loaded from the filesystem, so be sure to use different names for your custom
            templates

        Parameters:
            name: The name of the template.

        Returns:
            A new `Prompt` instance.
        """
        p = cls("")
        p._template = env.get_template(name)
        return p


class Prompt(BasePrompt):
    """
    The `Prompt` class is the only thing you need to know about Banks on the Python side. The class can be
    initialized with a string variable containing the prompt template text, then you can invoke the method `text`
    on your instance to pass the data needed to render the template and get back the final prompt.

    A quick example:
    ```py
    from banks import Prompt


    p = Prompt("Write a 500-word blog post on {{ topic }}.")
    my_topic = "retrogame computing"
    print(p.text({"topic": my_topic}))
    ```
    """

    def text(self, data: Optional[dict] = None) -> str:
        """
        Render the prompt using variables present in `data`

        Parameters:
            data: A dictionary containing the context variables.
        """
        data = self._get_context(data)
        return self._template.render(data)


class AsyncPrompt(BasePrompt):
    """
    Banks provides async support through the machinery [provided by Jinja](https://jinja.palletsprojects.com/en/3.0.x/api/#async-support)

    Since the Jinja environment is a global state in banks, the library can work either with or
    without async support, and this must be known before importing anything.

    If the application using banks runs within an `asyncio` loop, you can do two things
    to optimize banks' execution:

    1. Set the environment variable `BANKS_ASYNC_ENABLED=true`.
    2. Use the `AsyncPrompt` class that has an awaitable `run` method.

    For example, let's render a prompt that contains some calls to the `generate` extension. Those calls
    will be heavily I/O bound, so other tasks can take advantage and advance while the prompt is being
    rendered.

    Example:
    ```python
    # Enable async support before importing from banks
    import os

    os.environ["BANKS_ASYNC_ENABLED"] = "true"

    # Show logs to see what's happening at runtime
    import logging

    logging.basicConfig(level=logging.INFO)

    import asyncio
    from banks import AsyncPrompt

    prompt_template = \"\"\"
    Generate a tweet about the topic '{{ topic }}' with a positive sentiment.

    Examples:
    - {% generate "write a tweet with a positive sentiment", "gpt-3.5-turbo" %}
    - {% generate "write a tweet with a sad sentiment", "gpt-3.5-turbo" %}
    - {% generate "write a tweet with a neutral sentiment", "gpt-3.5-turbo" %}

    \"\"\"

    async def task(task_id: int, sleep_time: int):
        logging.info(f"Task {task_id} is running.")
        await asyncio.sleep(sleep_time)
        logging.info(f"Task {task_id} done.")


    async def main():
        p = AsyncPrompt(prompt_template)
        # Schedule the prompt rendering along with two executions of 'task', one sleeping for 10 seconds
        # and one sleeping for 1 second
        results = await asyncio.gather(p.text({"topic": "AI frameworks"}), task(1, 10), task(2, 1))
        print("All tasks done, rendered prompt:")
        print(results[0])


    asyncio.run(main())
    ```
    """

    def __init__(self, text: str) -> None:
        super().__init__(text)

        if not async_enabled:
            msg = "Async is not enabled. Please set the environment variable 'BANKS_ASYNC_ENABLED=on' and try again."
            raise AsyncError(msg)

    async def text(self, data: Optional[dict] = None) -> str:
        data = self._get_context(data)
        result: str = await self._template.render_async(data)
        return result
