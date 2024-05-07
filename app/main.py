import os
import sys
import core
from program_data import ProgramData
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from app_ui import Ui_MainWindow


class WallpaperED(QMainWindow):

    def __init__(self, program_data: ProgramData, gui_mode: bool = False) -> None:
        super(WallpaperED, self).__init__()

        self.__program_data = program_data

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

    def loadConfigToGUI(self):

        self.ui.downloadDirectoryEdit.setText(self.__program_data.get_download_directory())
        self.ui.apiTokenEdit.setText(self.__program_data.get_unsplash_api_token())

        commands = self.__program_data.get_commands()

        commands = "\n".join(commands)
        self.ui.wallpaperCommandEdit.setText(commands)
        self.ui.imageOrientationEdit.setText(self.__program_data.get_image_orientation())
        self.ui.isUpdateAutostartEnabledCheckBox.setChecked(self.__program_data.get_is_autostart_enabled())
        self.ui.autostartSearchQueryEdit.setText(self.__program_data.get_autostart_query())

    def applySettingsButtonClicked(self):

        # Read values from user input
        download_directory = self.ui.downloadDirectoryEdit.text().lstrip()
        api_token = self.ui.apiTokenEdit.text().lstrip()
        wallpaper_commands = self.ui.wallpaperCommandEdit.toPlainText()
        wallpaper_commands = wallpaper_commands.split("\n")
        wallpaper_commands = list(filter(lambda cmd: cmd.lstrip(), wallpaper_commands))

        is_autostart_enabled = self.ui.isUpdateAutostartEnabledCheckBox.isChecked()
        autostart_query = self.ui.autostartSearchQueryEdit.text().lstrip()

        orientation = self.ui.imageOrientationEdit.text().lstrip()

        if download_directory:
            self.__program_data.set_download_direcory(download_directory)

        if api_token:
            self.__program_data.set_unsplash_api_token(api_token)

        if wallpaper_commands:
            self.__program_data.set_commands(wallpaper_commands)

        if orientation:
            self.__program_data.set_image_orientation(orientation)

        self.__program_data.set_is_autostart_enabled(is_autostart_enabled)
        self.__program_data.set_autostart_query(autostart_query)

        core.setAutostartRegistry(create=is_autostart_enabled)

    def autostartRegistry(self, delete: bool = False):

        filename = "wallpaper-ed-autostart.desktop"
        autostart_registry_path = os.path.expanduser(f"~/.config/autostart/{filename}")

        if os.path.exists(autostart_registry_path):
            if delete:
                os.remove(autostart_registry_path)
        else:
            with open(autostart_registry_path, "w") as reg:
                reg.write("""[Desktop Entry]
Comment=Fresh wallpapers every time.
Exec=wallpaper-ed
Type=Application
""")

    def resetSettingsButtonClicked(self):
        self.loadConfigToGUI()

    def getWallpaperButtonClicked(self):

        # Fetch new random image depending on config
        try:
            custom_config = self.__program_data.get_image_kwargs()
            if self.gui_mode:
                user_image_query = self.ui.imageQueryEdit.text().lstrip()
                if user_image_query:
                    custom_config["query"] = user_image_query

            else:
                custom_config["query"] = self.__program_data.get_autostart_query()

            self.current_image = core.get_image_url(config=custom_config)

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
    main_window = WallpaperED(
        program_data=core.program_data,
        gui_mode=gui_mode
    )

    # Show main window if gui mode is enabled,
    # otherwise automatically download and set wallpaper
    if gui_mode:
        main_window.loadConfigToGUI()
        main_window.show()
        sys.exit(app.exec())
    else:
        error = main_window.getWallpaperButtonClicked()
        if not error:
            main_window.setWallpaperButtonClicked()

        app.exit()
