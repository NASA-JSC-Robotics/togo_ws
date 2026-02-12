import argparse
import os
import subprocess
import sys
import getpass
from pathlib import Path
import yaml
import shutil
import re

USER = getpass.getuser()
SUDO_PASSWORD = 'clearpath'
BASE_DIR = Path('/opt/onav')
SCRIPT_DIR = Path(__file__).parent.absolute()

UI_IMAGE_TAR_FILE = BASE_DIR / 'cpr-onav-ui.tar'
BASE_IMAGE_TAR_FILE = BASE_DIR / 'cpr-onav-base.tar'
AUTONOMY_IMAGE_TAR_FILE = BASE_DIR / 'cpr-onav-autonomy.tar'


def run_cmd(cmd, check=True, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, shell=True, text=True, capture_output=True)
    if check and result.returncode != 0:
        print(f'Error executing: {cmd}')
        print(f'Error: {result.stderr.strip()}')
        sys.exit(1)
    return result.stdout.strip()


def run_sudo_cmd(cmd, cwd=None):
    full_cmd = f'echo {SUDO_PASSWORD} | sudo -S {cmd}'
    return run_cmd(full_cmd, cwd=cwd)


def update_onav(new_version=None, onav_config_type='amp'):
    """
    Setup ONav with specified tag/branch or latest tag.

    Args:
        new_version (str): version number to upgrade to
    """

    # load docker images
    if UI_IMAGE_TAR_FILE.exists():
        print('Loading cpr-onav-ui docker image [can take up to 1 min]...')
        output = run_cmd(f'docker load -i {UI_IMAGE_TAR_FILE}')
        print(output)
    else:
        print(f'[ERROR] Missing cpr-onav-ui.tar file at location {BASE_DIR}')
        return

    if BASE_IMAGE_TAR_FILE.exists():
        print('Loading cpr-onav-base docker image [can take up to 2 min] ...')
        output = run_cmd(f'docker load -i {BASE_IMAGE_TAR_FILE}')
        print(output)
    else:
        print(f'[ERROR] Missing cpr-onav-base.tar file at location {BASE_DIR}')
        return

    if AUTONOMY_IMAGE_TAR_FILE.exists():
        print('Loading cpr-onav-autonomy docker image [can take up to 1 min]...')
        output = run_cmd(f'docker load -i {AUTONOMY_IMAGE_TAR_FILE}')
        print(output)
    else:
        print(f'[ERROR] Missing cpr-onav-autonomy.tar file at location {BASE_DIR}')
        return

    latest_version = str(SCRIPT_DIR).split('/')[3]

    # Create new version directory with sudo and set ownership once
    print('Creating new version directory...')
    new_version_dir = BASE_DIR / new_version
    if not new_version_dir.exists():
        run_sudo_cmd(f'mkdir -p {new_version_dir}')
        run_sudo_cmd(f'chown {USER}:docker {new_version_dir}')

    # Copy data directory
    latest_version_data_dir = BASE_DIR / latest_version / 'data'
    new_version_data_dir = BASE_DIR / new_version / 'data'
    if not new_version_data_dir.exists():
        try:
            shutil.copytree(latest_version_data_dir, new_version_data_dir)
            run_sudo_cmd(f'chown -R {USER}:docker {new_version_dir}')
            print(f'Copied /data/ folder from version: {latest_version}')
        except Exception as e:
            print(f"Error copying /data/ folder: {e}")

    # Copy config directory
    latest_version_config_dir = BASE_DIR / latest_version / 'config'
    new_version_config_dir = BASE_DIR / new_version / 'config'
    if not new_version_config_dir.exists():
        try:
            shutil.copytree(latest_version_config_dir, new_version_config_dir)
            run_sudo_cmd(f'chown -R {USER}:docker {new_version_dir}')
            print(f'Copied /config/ folder from version: {latest_version}')
        except Exception as e:
            print(f'Error copying /config/ folder: {e}')

    # Clone the app repository
    new_version_app_dir = BASE_DIR / new_version / 'app'
    if new_version_app_dir.exists():
        print(f'Directory {new_version_app_dir} already exists, skipping unzip')
    else:
        # uncompress app folder
        app_zip_file = BASE_DIR / 'cpr-onav-app.zip'
        app_uncompressed_dir = BASE_DIR / 'app'
        if app_zip_file.exists():
            run_cmd(f'unzip {app_zip_file}')
            run_cmd(f'mv {app_uncompressed_dir} {new_version_dir}')
            print(f'Installed app directory {new_version_app_dir}')
        else:
            print(f'[ERROR] Missing cpr-onav-app.zip file at location {BASE_DIR}')
            return

    # Change ownership
    print(f'Setting ownership to {USER}:docker')
    run_sudo_cmd(f'chown -R {USER}:docker {BASE_DIR}')

    if latest_version == 'ros2' or latest_version == '2.0.0' or latest_version == '2.0.1':
        config_filename = f'outdoornav.yaml.{onav_config_type}'
        default_config_file = BASE_DIR / config_filename
        new_version_config_file = new_version_config_dir / 'outdoornav.yaml'
        if default_config_file.exists():
            run_cmd(f'cp {default_config_file} {new_version_config_file}')
            old_config_env_file = BASE_DIR / new_version / 'config/config.env'
            run_cmd(f'rm {old_config_env_file}')
            print('Installed outdoornav.yaml configuration file. This is now used instead of ./config/config.env')
        else:
            print(f'[ERROR] Missing {config_filename} file at location {BASE_DIR}')
            return

    # Bring down running dockers
    latest_version_app_dir = BASE_DIR / latest_version / 'app'
    print('Stopping OutdoorNav...')
    output = run_cmd('docker compose --profile outdoornav down', cwd=latest_version_app_dir)
    print(output)

    # Starting new upgraded version
    print(f'Starting version {new_version} of OutdoorNav...')
    output = run_cmd('docker compose --profile outdoornav up -d --build', cwd=new_version_app_dir)
    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upgrade ONav application to the specified version')
    parser.add_argument('-v', '--version', help='Specify the version to upgrade to')
    parser.add_argument('-c', '--config', help='Specify the OutdoorNav configuration type: {amp, observer}')
    args = parser.parse_args()

    update_onav(new_version=args.version, onav_config_type=args.config)
