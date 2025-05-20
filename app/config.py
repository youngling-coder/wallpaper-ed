import json
import os

APP_NAME = "wallpaper-ed"


class AppConfig:
    def __init__(self):
        self.config_filename = os.path.expanduser(f"~/.config/{APP_NAME}/config.json")

        self.execute: list = [
            "gsettings set org.gnome.desktop.background picture-uri \"file://%PATH%\"",
            "gsettings set org.gnome.desktop.background picture-uri-dark \"file://%PATH%\""
        ]
        self.selected_api = "unsplash"
        
        self.apis: dict = {
            "unsplash": {
                "api_token": "",
                "api_url": "https://api.unsplash.com/photos/random"
            },
            "wallhaven": {
                "api_token": "",
                "api_url": "https://wallhaven.cc/api/v1/search"
            },
        }
        self.download_directory: str = "~/.local/share/backgrounds"
        self.image: dict = {
            "orientation": "landscape",
            "count": 1,
            "purity": "100"
        }
        self.orientation_ratios = {
            "landscape": "16x9,3x2,2x1,4x3,18x10,18x9,21x9",
            "squarish": "1x1",
            "portrait": "9x16,1x2,2x3,3x4,10x18,9x18,9x21"
        }


    def write_config(self):
        with open(self.config_filename, "w") as config_file:
            json.dump(self.__dict__, config_file)

        
    def load_config(self):
        with open(self.config_filename, "r") as config_file:
            self.__dict__ = json.load(config_file)
