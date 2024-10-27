## Prompt registry (BETA)

The Prompt Registry provides a storage API for managing versioned prompts. It allows you to store and retrieve prompts from different storage backends. Currently, Banks supports two storage implementations:

- Directory-based storage
- Redis-based storage

### Usage

```python
from banks import Prompt
from banks.registries.directory import DirectoryPromptRegistry
from pathlib import Path

# Create a registry
registry = DirectoryPromptRegistry(Path("./prompts"))

# Create and store a prompt
prompt = Prompt(
    text="Write a blog post about {{topic}}",
    name="blog_writer",
    version="1.0",
    metadata={"author": "John Doe"}
)
registry.set(prompt=prompt)

# Retrieve a prompt
retrieved_prompt = registry.get(name="blog_writer", version="1.0")
```

### Directory Registry

The DirectoryPromptRegistry stores prompts as individual files in a directory. Each prompt is saved as a `.jinja` file with the naming pattern `{name}.{version}.jinja`.

```python
# Initialize directory registry
registry = DirectoryPromptRegistry(
    directory_path=Path("./prompts"),
    force_reindex=False  # Set to True to rebuild the index
)
```

### Redis Registry

The RedisPromptRegistry stores prompts in Redis using a key-value structure.

```python
from banks.registries.redis import RedisPromptRegistry

registry = RedisPromptRegistry(
    redis_url="redis://localhost:6379",
    prefix="banks:prompt:"
)
```

### Common Features

Both implementations support:

- Versioning with automatic "0" default version
- Overwrite protection with `overwrite=True` option
- Metadata storage
- Error handling for missing/invalid prompts
