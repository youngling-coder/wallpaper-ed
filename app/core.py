import requests
from http.client import responses
from config import AppConfig
import random
import string
import os


program_data = AppConfig()
available_apis = program_data.apis.keys()


# Check if config file exists and create one if not
if not os.path.exists(program_data.config_filename) or os.path.isdir(program_data.config_filename):
    program_data.write_config()
else:
    program_data.load_config()

# Initializing Unsplash API token and URL

def seed(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def set_wallpaper(filepath: str) -> None:
    """Sets new desktop wallpaper."""

    # Executes command to set wallpaper replacing %PATH% with actual downloaded file path
    for command in program_data.execute:
        command = command.replace("%PATH%", filepath)
        os.system(command=command)


def save_image(content: bytes, filename: str = "wallpaper.jpg") -> None:
    """Saves image locally. Returns downloaded file location"""

    dir_ = os.path.expanduser(program_data.download_directory)
    # Set up download directory if not exists
    if not os.path.exists(dir_):
        os.mkdir(dir_)

    # Writing data to the image
    filepath = os.path.join(dir_, filename)
    with open(filepath, "wb") as write_image:
        write_image.write(content)

    return filepath


def get_image_url(query: str) -> str:
    """Fetches URL of the image."""

    api_config = program_data.apis[program_data.selected_api]
    base_url = api_config["api_url"]

    match program_data.selected_api:
        case "wallhaven":
            base_url += f"?apikey={api_config["api_token"]}"
            base_url += f"&ratios={program_data.orientation_ratios[program_data.image["orientation"]]}"
            base_url += f"&q={query}"
            base_url += f"&purity={program_data.image["purity"]}"
            base_url += f"&seed={seed()}"


            # Generating response from API
            response = requests.get(base_url)
            data = response.json()["data"]
            url = random.choice(data)["path"]

        case "unsplash":
            base_url += f"?client_id={api_config["api_token"]}"
            base_url += f"&orientation={program_data.image["orientation"]}"
            base_url += f"&query={query}"


            response = requests.get(base_url)
            data = response.json()
            url = data["urls"]["full"]


    if response.status_code != 200:
        error_msg = f"{response.status_code} - {responses[response.status_code]}"
        if response.status_code == 401:
            error_msg += f"API Access Token is invalid or not specified.\n"
        raise requests.HTTPError(error_msg)

    # Return image url
    return url


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
