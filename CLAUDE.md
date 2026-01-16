# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Banks is a Python prompt programming language and templating system for LLM applications. It provides a Jinja2-based template engine with specialized extensions and filters for creating dynamic prompts, managing chat messages, handling multimodal content (images/audio/video/documents), and integrating with various LLM providers through LiteLLM.

## Development Commands

### Testing
- Run tests: `hatch run test`
- Run tests with coverage: `hatch run test-cov` 
- Generate coverage report: `hatch run cov`
- Run e2e tests specifically: `hatch run test tests/e2e/`

### Linting and Type Checking
- Format code: `hatch run lint:fmt`
- Check formatting: `hatch run lint:check`
- Run type checking: `hatch run lint:typing`
- Run pylint: `hatch run lint:lint`
- Run all lint checks: `hatch run lint:all`

### Documentation
- Build docs: `hatch run docs build`
- Serve docs locally: `hatch run docs serve` (available at http://127.0.0.1:8000/)

### Environment Management
- All commands use Hatch environments with automatic dependency management
- Use `uv` as the installer for faster dependency resolution
- Python 3.10+ supported across multiple versions (3.10-3.14)

## Architecture Overview

### Core Components

**Prompt Classes** (`src/banks/prompt.py`):
- `BasePrompt`: Base class with common functionality for template rendering, metadata, versioning, and caching
- `Prompt`: Synchronous prompt rendering with `text()` and `chat_messages()` methods
- `AsyncPrompt`: Asynchronous version for use within asyncio loops (requires `BANKS_ASYNC_ENABLED=true`)
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
- `image`: Convert file paths/URLs to base64-encoded image content blocks
- `audio`: Convert audio files to base64-encoded audio content blocks  
- `video`: Convert video files to base64-encoded video content blocks
- `document`: Convert documents (PDF, TXT, HTML, CSS, XML, CSV, RTF, JS, JSON) to base64-encoded content blocks
- `cache_control`: Add Anthropic cache control metadata to content blocks
- `tool`: Convert Python callables to LLM function call schemas
- `lemmatize`: Text lemmatization using simplemma

### Registry System

**Storage Backends** (`src/banks/registries/`):
- `DirectoryTemplateRegistry`: File system-based prompt storage
- `FileTemplateRegistry`: Single file-based storage  
- `RedisTemplateRegistry`: Redis-backed storage for distributed scenarios
- All registries implement the `PromptRegistry` protocol

### Configuration

**Config System** (`src/banks/config.py`):
- Environment variable-based configuration with `BANKS_` prefix
- `BANKS_ASYNC_ENABLED`: Enable async template rendering
- `BANKS_USER_DATA_PATH`: Custom user data directory

## Key Development Patterns

### Template Rendering Flow
1. Templates parsed by Jinja2 environment with Banks extensions
2. Chat blocks converted to JSON during rendering  
3. `chat_messages()` parses JSON back to `ChatMessage` objects
4. Caching layer prevents re-rendering identical contexts

### Multimodal Content Handling
- Images/audio/video/documents converted to base64 during filter application
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

## Testing Strategy

- Unit tests for individual components in `tests/`
- E2e tests requiring API keys in `tests/e2e/` (marked with `@pytest.mark.e2e`)
- Template examples in `tests/templates/` for integration testing
- Coverage excludes async-specific code paths and deprecated modules

## Key Dependencies

- `jinja2`: Core templating engine
- `pydantic`: Type validation and serialization
- `litellm`: Multi-provider LLM integration (optional)
- `redis`: Redis registry backend (optional)
- `griffe`: Code introspection utilities
- `platformdirs`: Cross-platform data directory handling