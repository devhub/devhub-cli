import os
import json
from importlib.metadata import version

import click

from ..utils.client import get_client
from ..utils.templates import (
    ComponentTemplate, HeaderTemplate, FooterTemplate, GlobalCSS,
    HeaderCode, FooterCode)


def get_all_components():
    """Get all components from the server."""
    client, base_url = get_client()
    r = client.get(f'{base_url}template_components/')
    content = r.json()
    for component in content['objects']:
        template = ComponentTemplate.from_component(component)
        yield template


def get_registry():
    """Get the registry of templates."""
    registry = []
    # theme templates
    registry.extend(
        get_theme_templates())
    # template components
    registry.extend(
        get_all_components())
    registry.sort(key=lambda x: x.local_path)
    return registry


def get_site():
    """Get the site from the server."""
    client, base_url = get_client()
    r = client.get(f'{base_url}sites/{os.environ["DEVHUB_SITE_ID"]}')
    return r.json()


def get_theme():
    """Get the theme from the server."""
    site = get_site()
    theme_id = site['theme_id']

    client, base_url = get_client()
    r = client.get(f'{base_url}themes/{theme_id}')
    return r.json()


def get_theme_templates():
    """Get the theme templates from the server."""
    theme = get_theme()
    templates = []
    templates.append(HeaderTemplate.from_theme(theme))
    templates.append(FooterTemplate.from_theme(theme))
    templates.append(GlobalCSS.from_theme(theme))
    templates.append(HeaderCode.from_theme(theme))
    templates.append(FooterCode.from_theme(theme))
    return templates


@click.group()
def theme():
    pass


def init_env():
    """Initialize environment configuration."""

    # Check if .env file already exists
    env_path = os.path.join(os.environ['WORKING_DIR'], '.env')

    if os.path.exists(env_path):
        click.echo(click.style(f'.env file already exists at {env_path}', fg='yellow'))
        return
    
    # Prompt for environment variables
    api_key = click.prompt('DEVHUB_API_KEY', default='', show_default=False)
    api_secret = click.prompt('DEVHUB_API_SECRET', default='', show_default=False)
    base_url = click.prompt('DEVHUB_BASE_URL (example: https://yourbrand.cloudfrontend.net)', default='', show_default=False)
    site_id = click.prompt('DEVHUB_SITE_ID', default='', show_default=False)
    
    # Create .env file content
    env_content = []
    
    if api_key:
        env_content.append(f"DEVHUB_API_KEY='{api_key}'")
    else:
        env_content.append("# DEVHUB_API_KEY = ''")
    
    if api_secret:
        env_content.append(f"DEVHUB_API_SECRET='{api_secret}'")
    else:
        env_content.append("# DEVHUB_API_SECRET = ''")
    
    if base_url:
        env_content.append(f"DEVHUB_BASE_URL = '{base_url}'")
    else:
        env_content.append("# DEVHUB_BASE_URL =")
    
    if site_id:
        env_content.append(f"DEVHUB_SITE_ID = {site_id}")
    else:
        env_content.append("# DEVHUB_SITE_ID =")
    
    # Write to .env file
    with open(env_path, 'w') as f:
        f.write('\n'.join(env_content) + '\n')
    
    click.echo(click.style(f'Environment configuration written to {env_path}', fg='green'))


def init_gitignore():

    # Create .gitignore file
    gitignore_path = os.path.join(os.environ['WORKING_DIR'], '.gitignore')
    gitignore_content = [
        '# Environment variables',
        '.env',
        '',
        '# Python',
        '__pycache__/',
        '*.py[cod]',
        '*$py.class',
        '*.so',
        '.Python',
        'build/',
        'develop-eggs/',
        'dist/',
        'downloads/',
        'eggs/',
        '.eggs/',
        'lib/',
        'lib64/',
        'parts/',
        'sdist/',
        'var/',
        'wheels/',
        '*.egg-info/',
        '.installed.cfg',
        '*.egg',
        'MANIFEST',
        '',
        '# Virtual environments',
        'venv/',
        'env/',
        'ENV/',
        '',
        '# IDE',
        '.vscode/',
        '.idea/',
        '*.swp',
        '*.swo',
        '*~',
        '',
        '# OS',
        '.DS_Store',
        'Thumbs.db',
        '',
        '# Logs',
        '*.log',
    ]
    
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, 'w') as f:
            f.write('\n'.join(gitignore_content) + '\n')
        click.echo(click.style(f'Created .gitignore at {gitignore_path}', fg='green'))
    else:
        click.echo(click.style(f'.gitignore already exists at {gitignore_path}', fg='yellow'))


def init_config():
    """Initialize devhub.conf.json file."""

    # Create devhub.conf.json file
    config_path = os.path.join(os.environ['WORKING_DIR'], 'devhub.conf.json')
    
    try:
        current_version = version('devhub-cli')
    except:
        current_version = "unknown"
    
    config_content = {
        "config_cli_version": current_version,
        "theme": {}
    }
    
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            json.dump(config_content, f, indent=2)
        click.echo(click.style(f'Created devhub.conf.json at {config_path}', fg='green'))
    else:
        click.echo(click.style(f'devhub.conf.json already exists at {config_path}', fg='yellow'))


@theme.command()
def init():
    """Initialize theme environment configuration."""
    click.echo(click.style('Initializing DevHub environment configuration...', fg='green'))

    init_env()
    init_gitignore()
    init_config()


@theme.command()
def list():
    """List all templates."""
    registry = get_registry()
    for template in registry:
        click.echo(f'{template.local_path}')


@theme.command()
def status():
    """Status of all components."""
    any_changes = False

    registry = get_registry()
    for template in registry:
        status = template.status()
        if status in ['unchanged']:
            continue
        any_changes = True
        click.echo(f'{template.local_path}... {template.status()}')
    if any_changes is False:
        click.echo('Up to date')


@theme.command()
@click.argument('components', nargs=-1)
def sync(components):
    """Syncs the components to the local theme directory."""
    any_changes = False

    registry = get_registry()
    for template in registry:
        if components and template.local_path not in components:
            # skip if the component is not in the list of components to sync
            continue
        sync_result = template.sync()
        if sync_result['result'] in ['unchanged']:
            continue
        any_changes = True

        if sync_result['result'] == 'conflict':
            click.echo(f'Syncing {template.local_path}... conflict!!!')
        elif sync_result['result'] == 'created':
            click.echo(f'Syncing {template.local_path}... added')
        elif sync_result['result'] == 'updated':
            click.echo(f'Syncing {template.local_path}... updates pushed')

    if any_changes is False:
        click.echo('Up to date')
