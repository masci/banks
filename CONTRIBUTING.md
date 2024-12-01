# Contributing to Banks

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. If you like the project, but just don't have time to contribute
code, that's fine. There are other easy ways to support the project and show your appreciation, which we would also
be very happy about:

- Star the project
- Post about it
- Refer this project in your project's readme
- Mention the project at local meetups and tell your friends/colleagues

## Install Hatch

Assuming you already have Python installed and it's at least on version 3.10, the first step is to install
[Hatch](https://hatch.pypa.io/1.9/). We'll use Hatch to manage the virtual environments that are needed to build the
project, the documentation and to run the tests. Depending on your operating system, there are different ways to
install Hatch:

- `brew install hatch` on Mac
- The [GUI installer](https://hatch.pypa.io/1.9/install/#gui-installer_1) on Windows
- Or just `pip install hatch`

The [official documentation for Hatch](https://hatch.pypa.io/1.9/install/) contains a thorough description of all the
available installation methods.

## Run the tests

With Hatch installed, from the root of the repository running the tests is as simple as:

```sh
$ hatch run test
```

This command will activate the proper virtual environment, sync the required dependencies and invoke
[pytest](https://docs.pytest.org/en/stable/index.html).

To see a recap of the test coverage and specifically which are the lines that are currently not tested, you can run:

```sh
$ hatch run cov
```

## Lint the code

Banks tries to keep a high standard of coding conventions and uses [ruff](https://docs.astral.sh/ruff/) to keep style
and format consistent. [Mypy](https://mypy-lang.org/) is used to static check that types are properly declared
and used consistently across the codebase.

To perform a comprehensive lint check just run:

```sh
$ hatch run lint:all
```

> [!IMPORTANT]
> Lint checks are performed in the CI at every commit you push in a pull request, so we recommend you lint your code
> before pushing it to the remote for faster iterations.

## Improve The Documentation

Any contribution to the documentation is very welcome, whether it's a fix for a typo, a language improvement or a brand
new recipe in the cookbook. To preview the documentation locally, you can run:

```sh
$ hatch run docs serve
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
