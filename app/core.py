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
    """Fetches URL of the image from the selected API."""
    api_name = program_data.selected_api
    api_config = program_data.apis.get(api_name)
    
    if not api_config:
        raise ValueError(f"No API config found for '{api_name}'")

    orientation = program_data.image.get("orientation")
    purity = program_data.image.get("purity")

    if not orientation or not purity:
        raise ValueError("Missing orientation or purity in program_data.image")

    if api_name == "wallhaven":
        ratio = program_data.orientation_ratios.get(orientation)
        if not ratio:
            raise ValueError(f"No ratio found for orientation '{orientation}'")

        url = (
            f"{api_config['api_url']}?apikey={api_config['api_token']}"
            f"&ratios={ratio}&q={query}&purity={purity}&seed={seed()}"
        )

        response = requests.get(url)

        if response.status_code != 200:
            raise requests.HTTPError(
                f"{response.status_code} - {responses.get(response.status_code, 'Unknown error')}"
            )

        data = response.json().get("data", [])
        if not data:
            raise ValueError("No image data returned from Wallhaven")

        return random.choice(data)["path"]

    elif api_name == "unsplash":
        url = (
            f"{api_config['api_url']}?client_id={api_config['api_token']}"
            f"&orientation={orientation}&query={query}"
        )

        response = requests.get(url)

        if response.status_code != 200:
            raise requests.HTTPError(
                f"{response.status_code} - {responses.get(response.status_code, 'Unknown error')}"
            )

        data = response.json()
        return data.get("urls", {}).get("full")

    else:
        raise ValueError(f"Unsupported API selected: {api_name}")

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
