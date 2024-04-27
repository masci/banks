## Async support

To run banks within an `asyncio` loop you have to do two things:
1. set the environment variable `BANKS_ASYNC_ENABLED=true`.
2. use the `AsyncPrompt` class that has an awaitable `run` method.

Example:
```python
from banks import AsyncPrompt

async def main():
    p = AsyncPrompt.from_template("blog.jinja")
    result = await p.text({"topic": "AI frameworks"})
    print(result)

asyncio.run(main())
```