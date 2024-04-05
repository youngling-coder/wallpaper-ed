#!/usr/bin/python3

import sys
import core
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from app_ui import Ui_MainWindow


class WallpaperED(QMainWindow):
    def __init__(self, gui_mode: bool = False) -> None:
        super(WallpaperED, self).__init__()

        # Flag is responsible for UI rendering
        self.gui_mode = gui_mode

        # Setup UI if gui mode enabled
        if self.gui_mode:

            # Setup UI
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

            # Setup tooltips for buttons
            self.ui.setWallpaperButton.setToolTip(
                self.ui.setWallpaperButton.shortcut().toString()
            )
            self.ui.getWallpaperButton.setToolTip(
                self.ui.getWallpaperButton.shortcut().toString()
            )
            self.ui.applySettingsButton.setToolTip(
                self.ui.applySettingsButton.shortcut().toString()
            )
            self.ui.resetSettingsButton.setToolTip(
                self.ui.resetSettingsButton.shortcut().toString()
            )
            self.ui.showAPITokenButton.setToolTip(
                self.ui.showAPITokenButton.shortcut().toString()
            )

            # Connect slots to methods
            self.ui.getWallpaperButton.clicked.connect(self.getWallpaperButtonClicked)
            self.ui.setWallpaperButton.clicked.connect(self.setWallpaperButtonClicked)
            self.ui.applySettingsButton.clicked.connect(self.applySettingsButtonClicked)
            self.ui.resetSettingsButton.clicked.connect(self.resetSettingsButtonClicked)
            self.ui.showAPITokenButton.clicked.connect(self.showAPITokenButtonClicked)

        # Set current image as None
        self.current_image = None

    def showAPITokenButtonClicked(self):
        if self.ui.apiTokenEdit.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.apiTokenEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.ui.apiTokenEdit.setEchoMode(QLineEdit.EchoMode.Password)

    def showErrorMessage(self, title: str, description: str, details: str) -> None:
        """Shows the error message."""

        if gui_mode:
            err_msg = QMessageBox()
            err_msg.setIcon(QMessageBox.Icon.Critical)
            err_msg.setWindowTitle(title)
            err_msg.setText(description)
            err_msg.setDetailedText(details)
            err_msg.exec()
        else:
            print(description + "\nDetails:\n" + details)

    def loadConfigToGUI(self, config: dict):
        self.ui.downloadDirectoryEdit.setText(config["app"]["download_directory"])
        self.ui.apiTokenEdit.setText(config["app"]["unsplash_access_token"])

        commands = config["app"]["execute"]

        commands = "\n".join(commands)
        self.ui.wallpaperCommandEdit.setText(commands)
        self.ui.imageOrientationEdit.setText(config["image"]["orientation"])

    def applySettingsButtonClicked(self):

        # Read values from user input
        download_directory = self.ui.downloadDirectoryEdit.text().lstrip()
        api_token = self.ui.apiTokenEdit.text().lstrip()
        wallpaper_commands = self.ui.wallpaperCommandEdit.toPlainText()
        wallpaper_commands = wallpaper_commands.split("\n")
        wallpaper_commands = list(filter(lambda cmd:  cmd.lstrip(), wallpaper_commands))

        orientation = self.ui.imageOrientationEdit.text().lstrip()

        if download_directory:
            core.CONFIG["app"]["download_directory"] = download_directory

        if api_token:
            core.CONFIG["app"]["unsplash_access_token"] = api_token

        if wallpaper_commands:
            core.CONFIG["app"]["execute"] = wallpaper_commands

        if orientation:
            core.CONFIG["image"]["orientation"] = orientation

        # Write new config to the file
        core.write_config(core.config_filename, config=core.CONFIG)

    def resetSettingsButtonClicked(self):
        self.loadConfigToGUI(config=core.CONFIG)

    def getWallpaperButtonClicked(self):

        # Fetch new random image depending on config
        try:
            if self.gui_mode:
                user_image_query = self.ui.imageQueryEdit.text().lstrip()
                if user_image_query:
                    custom_config = core.CONFIG["image"].copy()
                    custom_config["query"] = user_image_query
                    self.current_image = core.get_image_url(config=custom_config)
                else:
                    self.current_image = core.get_image_url()
            else:
                self.current_image = core.get_image_url()

        except Exception as ex:
            self.showErrorMessage(title="Error!",
                                  description="An error occurred while program execution!",
                                  details=str(ex))
            return -1

        if self.gui_mode:
            # Select scaled image for preview
            try:
                image_data = core.get_image_as_bytes(url=self.current_image["urls"]["regular"])
            except Exception as ex:
                self.showErrorMessage(title="Error!",
                                      description="An error occurred while program execution!",
                                      details=str(ex))
                return -1

            # Create pixmap for selected image
            image = QImage().fromData(image_data)
            pixmap = QPixmap().fromImage(image)

            # Generate credits for a photo
            credits_link = f"Captured by <a href=\"{self.current_image["user"]["links"]["html"]}\">\
                            {self.current_image["user"]["name"]}</a>"

            # Show photo with credits
            self.ui.creditsLabel.setText(credits_link)
            self.ui.imageArea.setPixmap(pixmap)

    def setWallpaperButtonClicked(self):

        # Get full image
        try:
            image_data = core.get_image_as_bytes(url=self.current_image["urls"]["full"])
        except Exception as ex:
            self.showErrorMessage(title="Error!",
                                  description="An error occurred while program execution!",
                                  details=str(ex))
            return -1

        # Save image and set as wallpaper
        core.save_image(content=image_data)
        core.set_wallpaper()


if __name__ == "__main__":

    # Read console args
    args = sys.argv

    # Create application and main window instances
    app = QApplication([])
    gui_mode = "--gui" in args
    main_window = WallpaperED(gui_mode=gui_mode)

    # Show main window if gui mode is enabled,
    # otherwise automatically download and set wallpaper
    if gui_mode:
        main_window.loadConfigToGUI(core.CONFIG)
        main_window.show()
        sys.exit(app.exec())
    else:
        error = main_window.getWallpaperButtonClicked()
        if not error:
            main_window.setWallpaperButtonClicked()

        app.exit()
