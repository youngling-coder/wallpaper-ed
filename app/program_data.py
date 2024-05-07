import json
import os
from typing import Dict, List, AnyStr

APP_NAME = "wallpaper-ed"

BASE_PROGRAM_DATA = {
    "app": {
        "execute": [
            "gsettings set org.gnome.desktop.background picture-uri \"file://%PATH%\"",
            "gsettings set org.gnome.desktop.background picture-uri-dark \"file://%PATH%\""
        ],
        "autostart": {
            "enabled": True,
            "query": ""
        },
        "wallpaper_filename": "unsplash_wallpaper.jpg",
        "download_directory": "~/.local/share/backgrounds/"
    },
    "api": {
        "unsplash_api_token": "",
        "unsplash_api_url": "https://api.unsplash.com/photos/random"
    },
    "image": {
        "orientation": "landscape",
        "count": 1
    }
}



class ProgramData:
    def __init__(self) -> None:
        self.__filename = os.path.expanduser(f"~/.config/{APP_NAME}/config.json")
        self.__config = {}

    def load_config(self) -> None:
        """
        Load the configuration from a file into a dictionary object.

        :param filename: The name of the file to load the configuration from. (AnyStr)
        """
        # Read the configuration from the specified file
        with open(self.__filename) as json_config:
            self.__config = json.load(json_config)

    def write_config(self, config: Dict = {}) -> None:
        """
        Write the existing config dictionary object to a file.

        :param filename: The name of the file to write the configuration to. (AnyStr)
        :param config: The dictionary containing the configuration to write. If None, the current config object will be used.
                       (Optional[Dict])

        If the `config` parameter is not provided, the method will attempt to use the existing config. If the existing
        config is not available, it will use the base config.

        The configuration will be written to the specified file with an indentation of 4 spaces.
        """

        if not config:
            if self.__config:
                config = self.__config
            else:
                config = BASE_PROGRAM_DATA

        # Write the new config to the file
        with open(self.__filename, "w") as json_config:
            json.dump(config, json_config, indent=4)

    def get_commands(self) -> List[AnyStr]:
        return self.__config["app"]["execute"]

    def set_commands(self, __value: List[AnyStr]) -> None:
        self.__config["app"]["execute"] = __value

        self.write_config()

    def get_is_autostart_enabled(self) -> bool:
        return self.__config["app"]["autostart"]["enabled"]

    def set_is_autostart_enabled(self, __value: bool) -> None:
        self.__config["app"]["autostart"]["enabled"] = __value

        self.write_config()

    def get_autostart_query(self) -> AnyStr:
        return self.__config["app"]["autostart"]["query"]

    def set_autostart_query(self, __value: AnyStr) -> None:
        self.__config["app"]["autostart"]["query"] = __value

        self.write_config()

    def get_wallpaper_filename(self) -> AnyStr:
        return self.__config["app"]["wallpaper_filename"]

    def get_download_directory(self) -> AnyStr:
        return os.path.expanduser(self.__config["app"]["download_directory"])

    def set_download_direcory(self, __value: AnyStr) -> None:
        self.__config["app"]["download_directory"] = __value

        self.write_config()

    def get_wallpaper_path(self) -> AnyStr:
        return os.path.join(
            os.path.expanduser(self.__config["app"]["download_directory"]),
            self.get_wallpaper_filename()
        )

    def get_unsplash_api_token(self) -> AnyStr:
        return self.__config["api"]["unsplash_api_token"]

    def set_unsplash_api_token(self, __value: AnyStr) -> None:
        self.__config["api"]["unsplash_api_token"] = __value

        self.write_config()

    def get_image_orientation(self) -> AnyStr:
        return self.__config["image"]["orientation"]

    def set_image_orientation(self, __value: AnyStr) -> None:
        self.__config["image"]["orientation"] = __value

        self.write_config()

    def get_image_kwargs(self) -> Dict:
        """Returns a copy of image attributes as dictionary."""
        return self.__config["image"].copy()

    def get_unsplash_api_url(self) -> AnyStr:
        return self.__config["api"]["unsplash_api_url"]

    def get_config_filename(self) -> str:
        return self.__filename
