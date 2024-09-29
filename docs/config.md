## Configuration

Banks can smoothly run with defaults, but you can configure the library by changing the `config` object or by
setting the correspondent environment variables.

Example usage:

```python
from banks import config


config.ASYNC_ENABLED = True
```


### ASYNC_ENABLED

|                |                         |
| -------------- | ----------------------- |
| Type:          | `bool` or truthy string |
| Default value: | `False`                 |
| Env var:       | `BANKS_ASYNC_ENABLED`   |

Whether or not to use `asyncio` for prompt rendering and LLM generation. This setting won't speed up your
application, only set it to `True` if you need to integrate Banks into an async codebase.


### USER_DATA_PATH

|                |                        |
| -------------- | ---------------------- |
| Type:          | `Path` or path string  |
| Default value: | depending on OS        |
| Env var:       | `BANKS_USER_DATA_PATH` |

A user-writable folder where Banks will store its data. Banks uses a meaningful default for your operating system, so
change it only if you have to.
