Banks is fundamentally [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/intro/) with additional functionalities
specifically designed to work with Large Language Models prompts. Same as Jinja2, Banks takes in input a generic piece
of text called _template_ and gives you back its _rendered_ version, where the generic bits are replaced by actual data.

```
┌─────────────────────┐                               ┌─────────────────────┐
│                     │       ┌─────────────┐         │                     │
│                     │       │             │         │                     │
│       Template      │──────▶│    Banks    │────────▶│       Prompt        │
│                     │       │             │         │                     │
│                     │       └─────────────┘         │                     │
└─────────────────────┘              ▲                └─────────────────────┘
                                     │
                                     │
                           ┌───────────────────┐
                           │                   │
                           │     User data     │
                           │                   │
                           └───────────────────┘
```