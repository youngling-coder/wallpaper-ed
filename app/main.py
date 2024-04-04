#!/usr/bin/python3

import sys
import core
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from app_ui import Ui_MainWindow


class WallpaperED(QMainWindow):
    def __init__(self, gui_mode: bool = False) -> None:
        super(WallpaperED, self).__init__()

        # Flag is responsible for UI rendering
        self.gui_mode = gui_mode

        # Setup UI if gui mode enabled
        if self.gui_mode:
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.ui.setWallpaperButton.setToolTip(
                self.ui.setWallpaperButton.shortcut().toString()
            )
            self.ui.getWallpaperButton.setToolTip(
                self.ui.getWallpaperButton.shortcut().toString()
            )

            # Connect slots to methods
            self.ui.getWallpaperButton.clicked.connect(self.getWallpaperButtonClicked)
            self.ui.setWallpaperButton.clicked.connect(self.setWallpaperButtonClicked)

        # Set current image as None
        self.current_image = None

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

    def getWallpaperButtonClicked(self):

        # Fetch new random image depending on config
        try:
            user_image_query = self.ui.imageQueryEdit.text().lstrip()
            if user_image_query:
                custom_config = core.CONFIG["image"].copy()
                custom_config["query"] = user_image_query
                self.current_image = core.get_image_url(config=custom_config)
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
        main_window.show()
        sys.exit(app.exec())
    else:
        error = main_window.getWallpaperButtonClicked()
        if not error:
            main_window.setWallpaperButtonClicked()

        app.exit()
