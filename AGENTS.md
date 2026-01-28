# AGENTS.md

This file provides guidance to AI coding assistants when working with code in this repository.

## Project Overview

Banks is a Python prompt programming language and templating system for LLM applications. It provides a Jinja2-based template engine with specialized extensions and filters for creating dynamic prompts, managing chat messages, handling multimodal content (images/audio/video/documents), and integrating with various LLM providers through LiteLLM.

## Quick Reference

```bash
# Most common commands
hatch run test                    # Run unit tests
hatch run lint:all                # Run all linting checks
hatch run lint:fmt                # Auto-format code
hatch run test tests/test_foo.py  # Run specific test file
```

## Development Commands

### Testing
- Run tests: `hatch run test`
- Run tests with coverage: `hatch run test-cov`
- Generate coverage report: `hatch run cov`
- Run specific test file: `hatch run test tests/test_foo.py`
- Run e2e tests: `hatch run test tests/e2e/` (requires API keys)

### Linting and Type Checking
- Format code: `hatch run lint:fmt`
- Auto-fix lint issues: `hatch run lint:fix`
- Check formatting: `hatch run lint:check`
- Run type checking: `hatch run lint:typing`
- Run pylint: `hatch run lint:lint`
- Run all lint checks: `hatch run lint:all`

### Documentation
- Build docs: `hatch run docs build`
- Serve docs locally: `hatch run docs serve` (available at http://127.0.0.1:8000/)

### Environment Management
- All commands use Hatch environments with automatic dependency management
- Uses `uv` as the installer for faster dependency resolution
- Python 3.9+ supported (tested on 3.10-3.14)

## Architecture Overview

### Core Components

**Prompt Classes** (`src/banks/prompt.py`):
- `BasePrompt`: Base class with template rendering, metadata, versioning, and caching
- `Prompt`: Synchronous prompt rendering with `text()` and `chat_messages()` methods
- `AsyncPrompt`: Asynchronous version (requires `BANKS_ASYNC_ENABLED=true`)
- `PromptRegistry`: Protocol interface for prompt storage backends

**Type System** (`src/banks/types.py`):
- `ChatMessage`: Core chat message structure with role and content
- `ContentBlock`: Handles different content types (text, image_url, audio, video, document) with optional cache control
- `Tool`: Function calling support with automatic schema generation from Python callables
- `CacheControl`: Anthropic-style prompt caching metadata

**Template Environment** (`src/banks/env.py`):
- Global Jinja2 environment with Banks-specific extensions and filters
- Async support detection and configuration
- Custom template loader integration

**Error Types** (`src/banks/errors.py`):
- `MissingDependencyError`: Optional dependencies not installed
- `AsyncError`: Asyncio support misconfiguration
- `CanaryWordError`: Canary word leaked (prompt injection detection)
- `PromptNotFoundError`: Prompt not found in registry
- `InvalidPromptError`: Invalid prompt format
- `LLMError`: LLM provider errors

### Extensions System

**Chat Extension** (`src/banks/extensions/chat.py`):
- `{% chat role="..." %}...{% endchat %}` blocks for structured message creation
- Automatic conversion to `ChatMessage` objects during rendering

**Completion Extension** (`src/banks/extensions/completion.py`):
- `{% completion model="..." %}...{% endcompletion %}` for in-prompt LLM calls
- Integrated with LiteLLM for multi-provider support
- Function calling support within completion blocks

### Filters System

**Core Filters** (`src/banks/filters/`):
- `image`: Convert file paths/URLs/bytes to base64-encoded image content blocks
- `audio`: Convert audio files to base64-encoded audio content blocks
- `video`: Convert video files to base64-encoded video content blocks
- `document`: Convert documents (PDF, TXT, HTML, CSS, XML, CSV, RTF, JS, JSON) to base64-encoded content blocks
- `cache_control`: Add Anthropic cache control metadata to content blocks
- `tool`: Convert Python callables to LLM function call schemas
- `lemmatize`: Text lemmatization using simplemma

**Filter Pattern**: Filters wrap content in `<content_block>` tags and are only useful within `{% chat %}` blocks.

### Registry System

**Storage Backends** (`src/banks/registries/`):
- `DirectoryTemplateRegistry`: File system-based prompt storage
- `FileTemplateRegistry`: Single file-based storage
- `RedisTemplateRegistry`: Redis-backed storage for distributed scenarios
- All registries implement the `PromptRegistry` protocol

### Caching System

**Render Cache** (`src/banks/cache.py`):
- `RenderCache`: Protocol interface for caching rendered prompts
- `DefaultCache`: In-memory cache using pickle-serialized context as key
- Prevents re-rendering identical template + context combinations

### Configuration

**Config System** (`src/banks/config.py`):
- Environment variable-based configuration with `BANKS_` prefix
- `BANKS_ASYNC_ENABLED`: Enable async template rendering (must be set before import)
- `BANKS_USER_DATA_PATH`: Custom user data directory

## Key Development Patterns

### Template Rendering Flow
1. Templates parsed by Jinja2 environment with Banks extensions
2. Chat blocks converted to JSON during rendering
3. `chat_messages()` parses JSON back to `ChatMessage` objects
4. Caching layer prevents re-rendering identical contexts

### Multimodal Content Handling
- Images/audio/video/documents converted to base64 during filter application
- Filters accept file paths, URLs, or raw bytes
- Content blocks maintain type safety and metadata
- Cache control integrated at content block level

### Function Calling Integration
- Python functions automatically converted to LLM schemas via introspection
- Docstring parsing for parameter descriptions
- Type annotations converted to JSON Schema

### Async Support Architecture
- Global environment state requires async decision at import time
- `BANKS_ASYNC_ENABLED` must be set before importing banks modules
- `AsyncPrompt` provides `await`-able rendering methods

## Testing

### Test Markers
- `@pytest.mark.e2e`: End-to-end tests requiring external services
- `@pytest.mark.redis`: Tests requiring a running Redis instance

### Required Environment Variables for E2E Tests
- `OPENAI_API_KEY`: For OpenAI-based tests
- `ANTHROPIC_API_KEY`: For Anthropic-based tests

### Test Data
- Test fixtures in `tests/data/` (images, audio, video, PDFs)
- Template examples in `tests/templates/`

### Running Specific Tests
```bash
hatch run test tests/test_image.py        # Single file
hatch run test tests/test_image.py::test_name  # Single test
hatch run test -k "image"                 # Tests matching pattern
```

## Code Style

### Formatting
- Line length: 120 characters
- Use ruff for formatting and linting
- Imports sorted with `banks` as first-party

### Type Hints
- All public functions should have type annotations
- Use `from __future__ import annotations` for forward references
- MyPy strict mode enforced

### Conventions
- SPDX license headers in all source files
- Docstrings for public APIs
- Relative imports banned (use absolute `from banks.x import y`)

## Public API

The main exports from `banks` package:
```python
from banks import Prompt, AsyncPrompt, ChatMessage, config, env
```

## Dependencies

**Core (required)**:
- `jinja2`: Core templating engine
- `pydantic`: Type validation and serialization
- `griffe`: Code introspection utilities
- `platformdirs`: Cross-platform data directory handling
- `filetype`: File type detection for multimodal content
- `deprecated`: Deprecation decorators

**Optional**:
- `litellm`: Multi-provider LLM integration (`banks[all]`)
- `redis`: Redis registry backend (`banks[all]`)
- `simplemma`: Lemmatization filter (dev dependency)

## CI/CD

- **test.yml**: Runs tests on Python 3.10-3.14
- **docs.yml**: Builds and deploys documentation
- **release.yml**: Handles package releases

## PR Guidelines

Follow conventional commit prefixes for PR titles:
- `fix:` - Bug fixes
- `feat:` - New features
- `chore:` - Maintenance
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
