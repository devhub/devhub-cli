import os
import json
import tempfile
from unittest.mock import patch

from click.testing import CliRunner
from devhub.cli import cli
from devhub.commands.theme import init_config


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("devhub-cli, version ")


def test_init_config_creates_new_file():
    """Test that init_config creates a new devhub.conf.json file when it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, 'devhub.conf.json')
        
        with patch.dict(os.environ, {'WORKING_DIR': temp_dir}):
            with patch('devhub.commands.theme.version', return_value='1.0.0'):
                init_config()
        
        assert os.path.exists(config_path)
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        assert config_data['config_cli_version'] == '1.0.0'
        assert config_data['theme'] == {}


def test_init_config_handles_existing_file():
    """Test that init_config doesn't overwrite existing devhub.conf.json file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, 'devhub.conf.json')
        
        # Create existing config file
        existing_config = {
            "config_cli_version": "0.5.0",
            "theme": {"existing": "data"}
        }
        with open(config_path, 'w') as f:
            json.dump(existing_config, f)
        
        with patch.dict(os.environ, {'WORKING_DIR': temp_dir}):
            with patch('devhub.commands.theme.version', return_value='1.0.0'):
                init_config()
        
        # File should still exist with original content
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        assert config_data == existing_config


def test_init_config_handles_version_error():
    """Test that init_config handles pkg_resources error gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = os.path.join(temp_dir, 'devhub.conf.json')
        
        with patch.dict(os.environ, {'WORKING_DIR': temp_dir}):
            with patch('devhub.commands.theme.version', side_effect=Exception("Package not found")):
                init_config()
        
        assert os.path.exists(config_path)
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        assert config_data['config_cli_version'] == 'unknown'
        assert config_data['theme'] == {}
