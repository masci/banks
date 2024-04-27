## Async support

Banks provides async support thanks to the underlying machinery [provided by Jinja](https://jinja.palletsprojects.com/en/3.0.x/api/#async-support)

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

prompt_template = """
Generate a tweet about the topic '{{ topic }}' with a positive sentiment.

Examples:
- {% generate "write a tweet with a positive sentiment", "gpt-3.5-turbo" %}
- {% generate "write a tweet with a sad sentiment", "gpt-3.5-turbo" %}
- {% generate "write a tweet with a neutral sentiment", "gpt-3.5-turbo" %}

"""


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