import click
from dotenv import load_dotenv
import os

from .commands.theme import theme

if 'WORKING_DIR' not in os.environ:
    # auto-set the working directory
    os.environ['WORKING_DIR'] = os.getcwd()

dotenv_path = os.path.abspath(
    os.path.join(os.environ['WORKING_DIR'], '.env'))
load_dotenv(dotenv_path=dotenv_path)


@click.group()
@click.version_option(package_name='devhub-cli', prog_name='devhub-cli')
def cli():
    "CLI interface to devhub"

cli.add_command(theme)
