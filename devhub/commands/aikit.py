import os
import tempfile
import zipfile
import shutil
from urllib.request import urlretrieve

import click


@click.group()
def aikit():
    """AI toolkit commands for DevHub."""
    pass


@aikit.command()
def init(toolkit_url='https://github.com/devhub/devhub-cli-ai-toolkit/archive/refs/heads/main.zip'):
    """Initialize AI toolkit by downloading and extracting toolkit files."""
    
    working_dir = os.environ.get('WORKING_DIR', os.getcwd())
    
    click.echo(f'Downloading AI toolkit... {toolkit_url}')
    
    # Create temporary file for download
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # Download the zip file
        urlretrieve(toolkit_url, temp_filename)
        click.echo('Download completed.')
        
        # Extract the zip file
        click.echo('Extracting toolkit files...')
        
        with zipfile.ZipFile(temp_filename, 'r') as zip_ref:
            # Get all file names in the zip
            all_files = zip_ref.namelist()
            
            # Filter files that are in the devhub-cli-ai-toolkit-main directory
            toolkit_files = [f for f in all_files if f.startswith('devhub-cli-ai-toolkit-main/') and f != 'devhub-cli-ai-toolkit-main/']
            
            extracted_count = 0
            skipped_count = 0
            
            for file_path in toolkit_files:
                # Remove the root directory prefix
                relative_path = file_path[len('devhub-cli-ai-toolkit-main/'):]
                
                # Skip empty relative paths or directories
                if not relative_path or file_path.endswith('/'):
                    continue
                
                target_path = os.path.join(working_dir, relative_path)
                
                # Check if file already exists
                if os.path.exists(target_path):
                    click.echo(f'Skipping existing file: {relative_path}')
                    skipped_count += 1
                    continue
                
                # Create directory if it doesn't exist
                target_dir = os.path.dirname(target_path)
                if target_dir:
                    os.makedirs(target_dir, exist_ok=True)
                
                # Extract file
                with zip_ref.open(file_path) as source, open(target_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                click.echo(f'Extracted: {relative_path}')
                extracted_count += 1
        
        click.echo(click.style(f'AI toolkit initialization completed!', fg='green'))
        click.echo(f'Extracted {extracted_count} files, skipped {skipped_count} existing files.')
        
    except Exception as e:
        click.echo(click.style(f'Error during AI toolkit initialization: {str(e)}', fg='red'))
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)