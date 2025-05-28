import os
import hashlib
import subprocess
import yaml
import re
from datetime import datetime

from .client import get_client


def generate_metadata_header(modified_date=None):
    """
    Generate YAML metadata header as a Jinja comment.
    
    Args:
        modified_date (int): Unix timestamp of when content was last modified
        
    Returns:
        str: YAML metadata header wrapped in Jinja comment
    """
    metadata = {}
    if modified_date is not None:
        metadata['modified_date'] = modified_date
    
    if not metadata:
        return ""

    yaml_content = yaml.dump(metadata, default_flow_style=False).strip()
    return f"{{% comment %}}\n---\n{yaml_content}\n---\n{{% endcomment %}}\n"


def run_djlint(filepath, options=None):
    """Runs djlint on the specified file."""
    command = ["djlint"]
    if options:
        command.extend(options)
    command.append(filepath)

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running djlint: {e}")
        print(f"Stderr: {e.stderr}")
        return e.stderr


def slug_to_pascal(slug_string):
    """
    Convert slug-case string to PascalCase.
    
    Args:
        slug_string (str): String in slug-case format
        
    Returns:
        str: String converted to PascalCase
    """
    components = slug_string.split('-')
    # Capitalize first letter of all components
    return ''.join(word.capitalize() for word in components)


class BaseTemplate:

    def __init__(self, local_path, object):
        self.local_path = local_path
        # full path to the template
        self.filepath = os.path.join(os.environ['WORKING_DIR'], local_path)
        self.object = object
    
    def checksum(self):
        """Calculates the checksum of the local template."""
        content = self.strip_metadata()
        return hashlib.md5(content.encode()).hexdigest()

    def exists(self):
        """Checks if the template exists."""
        return os.path.exists(self.filepath)

    def parse_metadata(self):
        """Parses the metadata from the template within the first comment block."""
        with open(self.filepath, 'r') as f:
            content = f.read()
        # find the first comment block and extract only the YAML content
        match = re.search(r'^{% comment %}\n---\n(.*?)---\n{% endcomment %}\n', content, flags=re.DOTALL)
        if match:
            yaml_content = match.group(1)
            metadata = yaml.safe_load(yaml_content)
        else:
            metadata = {}
        return metadata

    def strip_metadata(self):
        """Strips the metadata from the template."""
        with open(self.filepath, 'r') as f:
            content = f.read()
        content = re.sub(r'^{% comment %}\n---\n.*?---\n{% endcomment %}\n', '', content, flags=re.DOTALL)
        return content

    def lint(self):
        """Lints the template."""
        run_djlint(self.filepath, [
            '--indent', '4', '--reformat', '--max-blank-lines', '1'])

    def remote_checksum(self):
        """Returns the checksum of the remote content."""
        return hashlib.md5(self.remote_content().encode()).hexdigest()
    
    def modified_date(self):
        """Returns the modified date of the template."""
        metadata = self.parse_metadata()
        return metadata['modified_date']
    
    def status(self):
        """Returns the status of the template."""
        if self.exists() is False:
            return 'new'
        if self.checksum() == self.remote_checksum():
            return 'unchanged'
        if self.modified_date() == self.remote_modified_date():
            return 'local changes - pending update'
        return 'conflict'

    def sync(self):
        if self.exists() is False:
            self.write_new(self.remote_content(), modified_date=self.remote_modified_date())
            return {
                'result': 'created',
            }

        # check if the file is up to date
        if self.checksum() == self.remote_checksum():
            return {
                'result': 'unchanged',
            }

        if self.modified_date() == self.remote_modified_date():
            # local has been updated, with no remote changes
            #
            # push updates
            self.lint()
            self.push_updates()
            self.write_new(self.remote_content(), modified_date=self.remote_modified_date())
            return {
                'result': 'updated',
            }

        # changes have been made
        if self.remote_modified_date() > self.modified_date():
            # remote has been updated
            return {
                'result': 'conflict',
            }
 
        assert False, 'unmatched condition'

    def write_new(self, content, modified_date=None):
        """Writes the content to the template if it is new."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        content = generate_metadata_header(modified_date) + content
        with open(self.filepath, 'w') as f:
            f.write(content)


class ComponentTemplate(BaseTemplate):
    """Template component."""

    @classmethod
    def from_component(cls, component):
        """Creates a ComponentTemplate from a component."""
        filename = slug_to_pascal(component['slug'])
        return cls(
            f'components/{filename}/{filename}.jinja', component)

    def remote_modified_date(self):
        """Returns the modified date of the remote template."""
        dt = datetime.fromisoformat(self.object['modified'])
        modified_date = int(dt.timestamp())
        return modified_date

    def remote_content(self):
        """Returns the remote content of the template."""
        return self.object['template_html']

    def push_updates(self):
        """Pushes the updates to the remote template."""
        client, base_url = get_client()
        url = f'{base_url}template_components/{self.object["id"]}/'
        payload = {
            'template_html': self.strip_metadata(),
        }
        updated = client.put(url, json=payload).json()
        self.object = updated
        return updated


class FooterTemplate(BaseTemplate):
    """Footer template."""

    @classmethod
    def from_theme(cls, theme):
        """Creates a ThemeTemplate from a theme."""
        return cls(
            f'layouts/footers/DefaultFooter.jinja', theme)

    def remote_modified_date(self):
        """Returns the modified date of the remote template."""
        dt = datetime.fromisoformat(self.object['footer_template']['modified'])
        modified_date = int(dt.timestamp())
        return modified_date

    def remote_content(self):
        """Returns the remote content of the template."""
        return self.object['footer_template']['content']

    def push_updates(self):
        """Pushes the updates to the remote template."""
        client, base_url = get_client()
        url = f'{base_url}themes/{self.object["id"]}/'
        payload = {
            'footer_template': {
                'content': self.strip_metadata(),
            },
        }
        updated = client.put(url, json=payload).json()
        self.object = updated
        return updated


class HeaderTemplate(BaseTemplate):
    """Header template."""

    @classmethod
    def from_theme(cls, theme):
        """Creates a ThemeTemplate from a theme."""
        return cls(
            f'layouts/headers/DefaultHeader.jinja', theme)

    def remote_modified_date(self):
        """Returns the modified date of the remote template."""
        dt = datetime.fromisoformat(self.object['header_template']['modified'])
        modified_date = int(dt.timestamp())
        return modified_date

    def remote_content(self):
        """Returns the remote content of the template."""
        return self.object['header_template']['content']

    def push_updates(self):
        """Pushes the updates to the remote template."""
        client, base_url = get_client()
        url = f'{base_url}themes/{self.object["id"]}/'
        payload = {
            'header_template': {
                'content': self.strip_metadata(),
            },
        }
        updated = client.put(url, json=payload).json()
        self.object = updated
        return updated


class GlobalCSS(BaseTemplate):
    """Global CSS template."""

    @classmethod
    def from_theme(cls, theme):
        """Creates a ThemeTemplate from a theme."""
        return cls(f'styles/globals.css', theme)

    def remote_modified_date(self):
        """Returns the modified date of the remote template."""
        dt = datetime.fromisoformat(self.object['modified'])
        modified_date = int(dt.timestamp())
        return modified_date

    def remote_content(self):
        """Returns the remote content of the template."""
        return self.object['extra_css']

    def push_updates(self):
        """Pushes the updates to the remote template."""
        client, base_url = get_client()
        url = f'{base_url}themes/{self.object["id"]}/'
        payload = {
            'extra_css': self.strip_metadata(),
        }
        updated = client.put(url, json=payload).json()
        self.object = updated
        return updated


class HeaderCode(BaseTemplate):
    """Header code template."""

    @classmethod
    def from_theme(cls, theme):
        """Creates a ThemeTemplate from a theme."""
        return cls(f'layouts/HeaderCode.jinja', theme)

    def remote_modified_date(self):
        """Returns the modified date of the remote template."""
        dt = datetime.fromisoformat(self.object['modified'])
        modified_date = int(dt.timestamp())
        return modified_date

    def remote_content(self):
        """Returns the remote content of the template."""
        return self.object['header_code']

    def push_updates(self):
        """Pushes the updates to the remote template."""
        client, base_url = get_client()
        url = f'{base_url}themes/{self.object["id"]}/'
        payload = {
            'header_code': self.strip_metadata(),
        }
        updated = client.put(url, json=payload).json()
        self.object = updated
        return updated


class FooterCode(BaseTemplate):
    """Footer code template."""

    @classmethod
    def from_theme(cls, theme):
        """Creates a ThemeTemplate from a theme."""
        return cls(f'layouts/FooterCode.jinja', theme)

    def remote_modified_date(self):
        """Returns the modified date of the remote template."""
        dt = datetime.fromisoformat(self.object['modified'])
        modified_date = int(dt.timestamp())
        return modified_date

    def remote_content(self):
        """Returns the remote content of the template."""
        return self.object['footer_code']

    def push_updates(self):
        """Pushes the updates to the remote template."""
        client, base_url = get_client()
        url = f'{base_url}themes/{self.object["id"]}/'
        payload = {
            'footer_code': self.strip_metadata(),
        }
        updated = client.put(url, json=payload).json()
        self.object = updated
        return updated