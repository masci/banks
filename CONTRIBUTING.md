# Contributing to Banks

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. If you like the project, but just don't have time to contribute
code, that's fine. There are other easy ways to support the project and show your appreciation, which we would also
be very happy about:

- Star the project
- Post about it
- Refer this project in your project's readme
- Mention the project at local meetups and tell your friends/colleagues

## Setup

Assuming you already have Python installed (version 3.10 or later), the recommended way to work on this project is
with [uv](https://docs.astral.sh/uv/). Install `uv` following the
[official instructions](https://docs.astral.sh/uv/getting-started/installation/), then install all development
dependencies with:

```sh
$ uv sync --extra dev
```

## Run the tests

With `uv` installed, from the root of the repository running the tests is as simple as:

```sh
$ uv run pytest tests
```

This command will use the virtual environment managed by `uv`, sync the required dependencies and invoke
[pytest](https://docs.pytest.org/en/stable/index.html).

To see a recap of the test coverage and specifically which are the lines that are currently not tested, you can run:

```sh
$ uv run pytest --cov --cov-report=xml tests && uv run coverage combine && uv run coverage report -m
```

## Lint the code

Banks tries to keep a high standard of coding conventions and uses [ruff](https://docs.astral.sh/ruff/) to keep style
and format consistent. [Mypy](https://mypy-lang.org/) is used to static check that types are properly declared
and used consistently across the codebase.

To perform a comprehensive lint check just run:

```sh
$ uv run ruff format --check && uv run ruff check . && uv run mypy --install-types --non-interactive src/banks && uv run pylint src/banks
```

To auto-format the code:

```sh
$ uv run ruff format
```

> [!IMPORTANT]
> Lint checks are performed in the CI at every commit you push in a pull request, so we recommend you lint your code
> before pushing it to the remote for faster iterations.

## Improve The Documentation

Any contribution to the documentation is very welcome, whether it's a fix for a typo, a language improvement or a brand
new recipe in the cookbook. To preview the documentation locally, you can run:

```sh
$ uv run mkdocs serve
```

and open the browser at the URL `http://127.0.0.1:8000/`. The documentation is built with
[mkdocs](https://www.mkdocs.org/) and [mkdocstrings](https://mkdocstrings.github.io/).

## Styleguides
### PR titles

We use PR titles to compile the project changelog, so we encourage you to follow the
[conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) specification and use one of these prefixes:

- `fix:`
- `feat:`
- `chore:`
- `docs:`
- `refactor:`
- `test:`

For example, a PR title might look like this: [feat: Add Redis prompt registry](https://github.com/masci/banks/pull/21)

<!-- omit in toc -->
## Attribution
This guide is based on the [contributing.md](https://contributing.md/generator)!
