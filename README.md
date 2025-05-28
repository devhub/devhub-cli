# devhub

[![PyPI](https://img.shields.io/pypi/v/devhub.svg)](https://pypi.org/project/devhub-cli/)
[![Changelog](https://img.shields.io/github/v/release/devhub/devhub-cli?include_prereleases&label=changelog)](https://github.com/devhub/devhub-cli/releases)
[![Tests](https://github.com/devhub/devhub-cli/actions/workflows/test.yml/badge.svg)](https://github.com/devhub/devhub-cli/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/devhub/devhub-cli/blob/master/LICENSE)

CLI interface to devhub

## Installation

Install this tool using `pip`:
```bash
pip install devhub-cli
```

Or just install and execute via `uvx`

```
uvx devhub-cli
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

Via `uvx`
```
uvx devhub-cli
```

## Theme Commands

The DevHub CLI provides powerful theme management capabilities for synchronizing and managing your DevHub theme components locally.

### Initial Setup

Before using theme commands, you need to initialize your environment:

```bash
devhub theme init
```

This command will:
- Create a `.env` file with your DevHub API credentials
- Generate a `.gitignore` file with appropriate exclusions
- Create a `devhub.conf.json` configuration file

You'll be prompted to enter:
- `DEVHUB_API_KEY` - Your OAuth1 API key
- `DEVHUB_API_SECRET` - Your OAuth1 API secret  
- `DEVHUB_BASE_URL` - Your DevHub instance URL (e.g., https://yourbrand.cloudfrontend.net)
- `DEVHUB_SITE_ID` - Your site identifier

### Available Commands

#### `devhub theme list`
Lists all available theme templates and components that can be synchronized.

```bash
devhub theme list
```

#### `devhub theme status`
Shows the synchronization status of all theme components, indicating which files have changes compared to the remote version.

```bash
devhub theme status
```

#### `devhub theme sync`
Synchronizes theme components from your DevHub instance to local files.

```bash
# Sync all components
devhub theme sync

# Sync specific components only
devhub theme sync layouts/headers/DefaultHeader.html components/HeroSection/HeroSection.jinja
```

The sync command will:
- Download theme files (CSS, headers, footers, localization) to the `layouts/` directory
- Download template components to the `components/` directory as `.jinja` files
- Format templates using `djlint` with 2-space indentation
- Convert component names from slug-case to PascalCase (e.g., `hero-section` → `HeroSection.jinja`)
- Perform checksum comparison to detect conflicts between local and remote changes

### Project Structure

After initialization and synchronization, your project structure will look like:

```
your-project/
├── .env                    # Environment variables (not committed)
├── .gitignore             # Git exclusions
├── devhub.conf.json       # CLI configuration
├── layouts/               # Theme templates (headers, footers, CSS)
│   ├── headers/DefaultHeader.jinja
│   ├── footers/DefaultFooter.jinja
├── styles/               # CSS styles
│   └── globals.css
└── components/            # Template components
    ├── HeroSection/HeroSection.jinja
    ├── ProductCard/ProductCard.jinja
    └── NavigationMenu/NavigationMenu.jinja
```

### Authentication & Environment

The CLI uses OAuth1 authentication to connect to your DevHub instance. All sensitive credentials are stored in the `.env` file, which should never be committed to version control.

Required environment variables:
- `DEVHUB_API_KEY` - OAuth1 API key
- `DEVHUB_API_SECRET` - OAuth1 API secret
- `DEVHUB_BASE_URL` - Base URL for DevHub API
- `DEVHUB_SITE_ID` - Site identifier

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd devhub-cli
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

## CLI template

CLI click template based on https://github.com/simonw/click-app
