from __future__ import annotations

import json
from typing import cast

from banks import Prompt
from banks.errors import InvalidPromptError, PromptNotFoundError
from banks.prompt import DEFAULT_VERSION, PromptModel

REDIS_INSTALL_MSG = "redis is not installed. Please install it with `pip install redis`."


class RedisPromptRegistry:
    """A prompt registry that stores prompts in Redis."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        prefix: str = "banks:prompt:",
    ) -> None:
        """
        Initialize the Redis prompt registry.

        Parameters:
            redis_url: Redis connection URL
            prefix: Key prefix for storing prompts in Redis
        """
        try:
            import redis
        except ImportError as e:
            raise ImportError(REDIS_INSTALL_MSG) from e

        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._prefix = prefix

    def _make_key(self, name: str, version: str) -> str:
        """Create Redis key for a prompt."""
        return f"{self._prefix}{name}:{version}"

    def get(self, *, name: str, version: str | None = None) -> Prompt:
        """
        Get a prompt by name and version.

        Parameters:
            name: Name of the prompt
            version: Version of the prompt (optional)

        Returns:
            Prompt instance

        Raises:
            PromptNotFoundError: If prompt doesn't exist
        """
        version = version or DEFAULT_VERSION
        key = self._make_key(name, version)

        data = self._redis.get(key)
        if not data:
            msg = f"Cannot find prompt with name '{name}' and version '{version}'"
            raise PromptNotFoundError(msg)

        prompt_data = json.loads(cast(str, data))
        return Prompt(**prompt_data)

    def set(self, *, prompt: Prompt, overwrite: bool = False) -> None:
        """
        Store a prompt in Redis.

        Parameters:
            prompt: Prompt instance to store
            overwrite: Whether to overwrite existing prompt

        Raises:
            InvalidPromptError: If prompt exists and overwrite=False
        """
        version = prompt.version or DEFAULT_VERSION
        key = self._make_key(prompt.name, version)

        # Check if prompt already exists
        if self._redis.exists(key) and not overwrite:
            msg = f"Prompt with name '{prompt.name}' already exists. Use overwrite=True to overwrite"
            raise InvalidPromptError(msg)

        # Convert prompt to serializable format
        prompt_model = PromptModel.from_prompt(prompt)
        prompt_data = prompt_model.model_dump()

        # Store in Redis
        self._redis.set(key, json.dumps(prompt_data))
