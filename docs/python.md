## Basic usage

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

## Loading templates from files

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

## Default templates

Banks' package comes with the following prompt templates ready to be used:

- `banks_macros.jinja`
- `generate_tweet.jinja`
- `run_prompt_process.jinja`
- `summarize_lemma.jinja`
- `blog.jinja`
- `run_prompt.jinja`
- `summarize.jinja`

If Banks is properly installed, something like `Prompt.from_template("blog.jinja")` should always work out of the box.