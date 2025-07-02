import os
import sys
import core
import hashlib
from config import AppConfig
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QMessageBox,
    QLineEdit,
    QCheckBox,
    QGraphicsScene,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QImage
from app_ui import Ui_MainWindow


class ImageDownloadWorker(QObject):
    finished = pyqtSignal(str, bytes)  # url, image_data
    error = pyqtSignal(str)

    def __init__(self, query, program_data):
        super().__init__()
        self.query = query
        self.program_data = program_data

    def run(self):
        import core

        try:
            url = core.get_image_url(self.query)
            image_data = core.get_image_as_bytes(url)
            self.finished.emit(url, image_data)
        except Exception as ex:
            self.error.emit(str(ex))


class WallpaperED(QMainWindow):

    def __init__(self, program_data: AppConfig) -> None:
        super(WallpaperED, self).__init__()

        self.__program_data = program_data
        # self.setStyleSheet(stylesheet)

        # Setup UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self)

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
        self.ui.APIComboBox.currentTextChanged.connect(self.loadConfigToGUI)
        self.ui.imageOrientationComboBox.currentTextChanged.connect(
            self.loadConfigToGUI
        )

        for index in range(self.ui.purityLayout.count()):
            item = self.ui.purityLayout.itemAt(index)
            widget: QCheckBox = item.widget()
            widget.checkStateChanged.connect(self.loadConfigToGUI)

        self.loadConfigToGUI()

        # Set current image as None
        self.current_image = None
        self.original_pixmap = None

    def showAPITokenButtonClicked(self):
        if self.ui.apiTokenEdit.echoMode() == QLineEdit.EchoMode.Password:
            self.ui.apiTokenEdit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.ui.apiTokenEdit.setEchoMode(QLineEdit.EchoMode.Password)

    def showErrorMessage(self, title: str, description: str, details: str) -> None:
        """Shows the error message."""

        err_msg = QMessageBox()
        err_msg.setIcon(QMessageBox.Icon.Critical)
        err_msg.setWindowTitle(title)
        err_msg.setText(description)
        err_msg.setDetailedText(details)
        err_msg.exec()

    def getPurityOptions(self):

        options = ""

        for index in range(self.ui.purityLayout.count()):

            item = self.ui.purityLayout.itemAt(index)
            widget: QCheckBox = item.widget()

            options += str(int(widget.isChecked()))

        return options

    def loadConfigToGUI(self, flag=None):

        if flag:
            self.__program_data.selected_api = self.ui.APIComboBox.currentText()
            self.__program_data.image["orientation"] = (
                self.ui.imageOrientationComboBox.currentText()
            )
            self.__program_data.image["purity"] = self.getPurityOptions()
            self.__program_data.write_config()

        self.ui.APIComboBox.setCurrentText(self.__program_data.selected_api)
        self.ui.downloadDirectoryEdit.setText(self.__program_data.download_directory)
        self.ui.apiTokenEdit.setText(
            self.__program_data.apis[self.__program_data.selected_api]["api_token"]
        )

        commands = self.__program_data.execute

        commands = "\n".join(commands)
        self.ui.wallpaperCommandEdit.setText(commands)
        self.ui.imageOrientationComboBox.setCurrentText(
            self.__program_data.image["orientation"]
        )

    def applySettingsButtonClicked(self):

        # Read values from user input
        download_directory = self.ui.downloadDirectoryEdit.text().lstrip()
        api_token = self.ui.apiTokenEdit.text().lstrip()
        wallpaper_commands = self.ui.wallpaperCommandEdit.toPlainText()
        wallpaper_commands = wallpaper_commands.split("\n")
        wallpaper_commands = list(filter(lambda cmd: cmd.lstrip(), wallpaper_commands))

        if download_directory:
            self.__program_data.download_directory = download_directory

        self.__program_data.apis[self.ui.APIComboBox.currentText()][
            "api_token"
        ] = api_token

        if wallpaper_commands:
            self.__program_data.execute = wallpaper_commands

        self.__program_data.write_config()

    def resetSettingsButtonClicked(self):
        self.loadConfigToGUI()

    def getWallpaperButtonClicked(self):
        # Start async download in a thread
        query = self.ui.imageQueryEdit.text().lstrip()

        self.thread = QThread()
        self.worker = ImageDownloadWorker(query, self.__program_data)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)

        # Connect signals
        self.worker.finished.connect(self.on_image_downloaded)
        self.worker.error.connect(self.on_image_download_error)

        # Cleanup for both success and error cases
        self.worker.finished.connect(self.cleanup_thread)
        self.worker.error.connect(self.cleanup_thread)

        self.thread.start()

    def cleanup_thread(self):
        """Clean up thread resources"""
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def on_image_downloaded(self, url, image_data):
        self.current_image = url
        image = QImage().fromData(image_data)
        self.original_pixmap = QPixmap().fromImage(image)
        self.scene.clear()
        self.scene.addPixmap(self.original_pixmap)
        self.scene.setSceneRect(
            0, 0, self.original_pixmap.width(), self.original_pixmap.height()
        )
        self.ui.imageArea.setScene(self.scene)
        self.ui.imageArea.fitInView(
            self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
        )

    def on_image_download_error(self, error_msg):
        self.showErrorMessage(
            title="Error!",
            description="An error occurred while program execution!",
            details=error_msg,
        )
        # Reset current image to prevent using invalid URL
        self.current_image = None

    def setWallpaperButtonClicked(self):

        if self.current_image:
            # Get full image
            try:
                image_data = core.get_image_as_bytes(url=self.current_image)
            except Exception as ex:
                self.showErrorMessage(
                    title="Error!",
                    description="An error occurred while program execution!",
                    details=str(ex),
                )
                return -1

            # Save image and set as wallpaper
            filename = (
                f"{hashlib.sha256(self.current_image.encode("utf-8")).hexdigest()}.jpg"
            )
            filepath = core.save_image(content=image_data, filename=filename)
            core.set_wallpaper(filepath=filepath)


if __name__ == "__main__":

    # Read console args
    args = sys.argv

    # Create application and main window instances
    app = QApplication([])
    main_window = WallpaperED(
        program_data=core.program_data,
    )

    # Show main window if gui mode is enabled,
    # otherwise automatically download and set wallpaper
    main_window.show()
    sys.exit(app.exec())
