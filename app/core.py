import requests
from http.client import responses
from config import load_config, write_config, APP_NAME
from typing import Optional
import os

# This application is powered by the Unsplash API
# All the photos provided are belong to their owners
# All the photos provided are distributed under the Unsplash License
# Unsplash License: https://unsplash.com/license
# More info about Unsplash API: https://unsplash.com/documentation

# Setting up basic config store parameters
config_filename = os.path.expanduser(f"~/.config/{APP_NAME}/config.json")

# Check if config file exists and create one if not
if not os.path.exists(config_filename) or os.path.isdir(config_filename):
    CONFIG = write_config(config_filename)
else:
    CONFIG = load_config(config_filename)

# Initializing Unsplash API token and URL

API_TOKEN = CONFIG["app"]["unsplash_access_token"]
API_URL = "https://api.unsplash.com/photos/random"

# Initializing downloading parameters
WALLPAPER_DIRECTORY = os.path.expanduser(CONFIG["app"]["download_directory"])
BASE_IMAGE_NAME = CONFIG["app"]["wallpaper_filename"]
DOWNLOADED_FILEPATH = os.path.join(WALLPAPER_DIRECTORY, BASE_IMAGE_NAME)


def set_wallpaper() -> None:
    """Sets new desktop wallpaper."""

    # Executes command to set wallpaper replacing %PATH% with actual downloaded file path
    for command in CONFIG["app"]["execute"]:
        os.system(command=command.replace("%PATH%", DOWNLOADED_FILEPATH))


def save_image(content: bytes) -> None:
    """Saves image locally. Returns downloaded file location"""

    # Set up download directory if not exists
    if not os.path.exists(WALLPAPER_DIRECTORY):
        os.mkdir(WALLPAPER_DIRECTORY)

    # Writing data to the image
    with open(DOWNLOADED_FILEPATH, "wb") as write_image:
        write_image.write(content)


def get_image_url(config: Optional[dict] = None) -> dict:
    """Fetches URL of the image."""

    # Setting up parameters & headers
    headers = {
        "Authorization": f"Client-ID {API_TOKEN}"
    }

    # Setup image config

    params = CONFIG["image"].copy()

    if config:
        params.update(config)

    # Generating response from API
    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code != 200:
        error_msg = f"{response.status_code} - {responses[response.status_code]}"
        if response.status_code == 401:
            error_msg += f"\nUnsplash API Access Token is invalid or not specified.\n" \
                         "To edit, specify or check spelling of the Unsplash API Access Token" \
                         f" update this file {config_filename}\nSee config setup guide here: "
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
            error_msg += f"\nUnsplash API Access Token is invalid or not specified.\n" \
                         "To edit, specify or check spelling of the Unsplash API Access Token" \
                         f" update this file {config_filename}\nSee config setup guide here: "
        raise requests.HTTPError(error_msg)

    return response.content
