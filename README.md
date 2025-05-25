# devhub

[![PyPI](https://img.shields.io/pypi/v/devhub.svg)](https://pypi.org/project/devhub/)
[![Changelog](https://img.shields.io/github/v/release/devhub/devhub?include_prereleases&label=changelog)](https://github.com/devhub/devhub/releases)
[![Tests](https://github.com/devhub/devhub/actions/workflows/test.yml/badge.svg)](https://github.com/devhub/devhub/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/devhub/devhub/blob/master/LICENSE)

CLI interface to devhub

## Installation

Install this tool using `pip`:
```bash
pip install devhub
```
## Usage

For help, run:
```bash
devhub --help
```
You can also use:
```bash
python -m devhub --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd devhub
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
