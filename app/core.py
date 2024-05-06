import requests
from http.client import responses
# from config import load_config, write_config, APP_NAME

from program_data import ProgramData
from typing import Optional
import os

# This application is powered by the Unsplash API
# All the photos provided are belong to their owners
# All the photos provided are distributed under the Unsplash License
# Unsplash License: https://unsplash.com/license
# More info about Unsplash API: https://unsplash.com/documentation


program_data = ProgramData()
# Check if config file exists and create one if not
if not os.path.exists(program_data.get_config_filename()) or os.path.isdir(program_data.get_config_filename()):
    program_data.write_config()
else:
    program_data.load_config()

# Initializing Unsplash API token and URL
API_TOKEN = program_data.get_unsplash_api_token()
API_URL = program_data.get_unsplash_api_url()

# Initializing downloading parameters
DOWNLOADED_FILEPATH = program_data.get_wallpaper_path()


def set_wallpaper() -> None:
    """Sets new desktop wallpaper."""

    # Executes command to set wallpaper replacing %PATH% with actual downloaded file path
    for command in program_data.get_commands():
        os.system(command=command.replace("%PATH%", DOWNLOADED_FILEPATH))


def save_image(content: bytes) -> None:
    """Saves image locally. Returns downloaded file location"""

    dir_ = program_data.get_download_directory()
    # Set up download directory if not exists
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    # Writing data to the image
    with open(DOWNLOADED_FILEPATH, "wb") as write_image:
        write_image.write(content)


def get_image_url(config: Optional[dict] = {}) -> dict:
    """Fetches URL of the image."""

    # Setting up parameters & headers
    headers = {
        "Authorization": f"Client-ID {API_TOKEN}"
    }

    # Setup image config

    params = program_data.get_image_kwargs()

    if config:
        params.update(config)

    # Generating response from API
    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code != 200:
        error_msg = f"{response.status_code} - {responses[response.status_code]}"
        if response.status_code == 401:
            error_msg += f"\nUnsplash API Access Token is invalid or not specified.\n"
        raise requests.HTTPError(error_msg)

    # Return image url
    return response.json()[0]


def get_image_as_bytes(url: str) -> bytes | None:
    """Parse image from url and returns image data as bytes."""

    # Parse image url
    response = requests.get(url=url)

    # Return content as bytes
    if response.status_code != 200:
        error_msg = f"{response.status_code} - {responses[response.status_code]}"
        if response.status_code == 401:
            error_msg += f"\nUnsplash API Access Token is invalid or not specified.\n"
        raise requests.HTTPError(error_msg)

    return response.content
