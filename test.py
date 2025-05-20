import sys
import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QAction, QColor, QShortcut, QKeySequence, QImage
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QGraphicsTextItem, QGraphicsPixmapItem

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)
        
        background_color = QColor(3, 5, 15)

        # Create a central widget and set it as the main window's central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a QGraphicsView and set it as the central widget
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        #layout.setSpacing(0)
        self.view = QGraphicsView(self)
        self.view.setBackgroundBrush(background_color)
        layout.addWidget(self.view)

        # Create a QGraphicsScene
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        # Create a QAction to open an image
        open_action = QAction("Open Image", self)
        open_action.triggered.connect(self.openImage)
        self.menuBar().addAction(open_action)

        self.grouped_images = {}  # Dictionary to store images in groups
        self.group_names = []  # List to store group names
        self.current_group_index = 0  # Index of the currently selected group
        self.current_image_index = 0  # Index of the currently displayed image within the group

        text_item = QGraphicsTextItem("Alice")

        font = text_item.font()
        font.setPointSize(150)  # Adjust the font size as needed
        text_item.setFont(font)

        text_item.setDefaultTextColor(Qt.GlobalColor.red)

        text_item.setPos(100, 100)

        self.scene.addItem(text_item)

        self.setShortcuts()
    
    def setShortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_F11), self, self.toggleFullScreen)

        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.nextImage)

        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.previousImage)

        QShortcut(QKeySequence(Qt.Key.Key_Up), self, self.switchGroupUp)

        QShortcut(QKeySequence(Qt.Key.Key_Down), self, self.switchGroupDown)

    def openImage(self):
        folder_dialog = QFileDialog.getExistingDirectory(self, "Open Directory")
    
        if folder_dialog:
            self.grouped_images, self.group_names = self.collectGroupedImages(folder_dialog)
            self.current_group_index = 0  # Reset the current group index
            self.current_image_index = 0  # Reset the current image index within the group
            
            if self.group_names:
                self.displayImage()

    def collectGroupedImages(self, directory):
        grouped_images = {}
        group_names = []
        for root, _, files in os.walk(directory):
            # Determine the group name (folder name)
            group_name = os.path.basename(root)
            if group_name not in grouped_images:
                grouped_images[group_name] = []
                group_names.append(group_name)
            
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif')):
                    image_path = os.path.join(root, filename)
                    grouped_images[group_name].append(image_path)
        return grouped_images, group_names

    def switchGroupUp(self):
        if self.group_names:
            self.current_group_index = (self.current_group_index - 1) % len(self.group_names)
            self.current_image_index = 0  # Reset the current image index within the new group
            self.displayImage()

    def switchGroupDown(self):
        if self.group_names:
            self.current_group_index = (self.current_group_index + 1) % len(self.group_names)
            self.current_image_index = 0  # Reset the current image index within the new group
            self.displayImage()

    def nextImage(self):
        if self.group_names:
            current_group_name = self.group_names[self.current_group_index]
            current_group = self.grouped_images.get(current_group_name, [])
            if current_group:
                self.current_image_index = (self.current_image_index + 1) % len(current_group)
                self.displayImage()

    def previousImage(self):
        if self.group_names:
            current_group_name = self.group_names[self.current_group_index]
            current_group = self.grouped_images.get(current_group_name, [])
            if current_group:
                self.current_image_index = (self.current_image_index - 1) % len(current_group)
                self.displayImage()

    def displayImage(self):
        #self.timer.start(self.new_delay * 1000)
        if self.group_names:
            current_group_name = self.group_names[self.current_group_index]
            current_group = self.grouped_images.get(current_group_name, [])
            if current_group:
                image_path = current_group[self.current_image_index]
                image = QImage(image_path)
                pixmap = QPixmap(image)
                pixmap_item = QGraphicsPixmapItem(pixmap)

                self.scene.clear()
                self.scene.addItem(pixmap_item)

                self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())

                self.view.setScene(self.scene)
                self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.menuBar().show()
        else:
            self.showFullScreen()
            self.menuBar().hide()

def main():
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

