
::: banks.prompt.Prompt
    options:
      inherited_members: true

::: banks.prompt.AsyncPrompt

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
