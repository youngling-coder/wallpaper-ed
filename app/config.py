import json

APP_NAME = "wallpaper-ed"
# Base config
BASE_CONFIG = {
    "app": {
        "execute": [
            "gsettings set org.gnome.desktop.background picture-uri \"file://%PATH%\"",
            "gsettings set org.gnome.desktop.background picture-uri-dark \"file://%PATH%\""
        ],
        "wallpaper_filename": "unsplash_wallpaper.jpg",
        "download_directory": "~/.local/share/backgrounds/",
        "unsplash_access_token": "YOUR_TOKEN"
    },
    "image": {
        "orientation": "landscape",
        "count": 1
    }
}


def load_config(filename: str):
    """Load config from file as a dict object."""

    # Reading config from file specified
    with open(filename) as json_config:
        config = json.load(json_config)

    return config


def write_config(filename: str):
    """Write existing config dict object to file."""

    # Write new config to the file
    with open(filename, "w") as json_config:
        json.dump(BASE_CONFIG, json_config, indent=4)

    return BASE_CONFIG
