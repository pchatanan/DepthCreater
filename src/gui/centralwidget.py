from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QWidget

from engine.vanishingpoint import VanishingPointEng
from gui.grapgicsview import GraphicsView
from gui.graphicsscene import GraphicsScene
from util.filemanager import FileManager


class CentralWidget(QWidget):
    def __init__(self, img_path, load_new_image, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        self.view = GraphicsView(self)
        self.img_path = img_path
        self.load_new_image = load_new_image
        self.load_image(file_name=self.img_path)

        import_image_button = QPushButton("Import Image")
        import_image_button.setToolTip('Select an image to be editted')
        import_image_button.clicked.connect(self.on_click)
        add_button = QPushButton("Add line")
        add_button.clicked.connect(self.on_add_click)
        cancel_button = QPushButton("Cancel")
        add_point_button = QPushButton("Add point")
        add_point_button.clicked.connect(self.on_add_point_click)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(import_image_button, alignment=Qt.AlignCenter)
        hbox.addWidget(cancel_button, alignment=Qt.AlignCenter)
        hbox.addWidget(add_button, alignment=Qt.AlignCenter)
        hbox.addWidget(add_point_button, alignment=Qt.AlignCenter)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.view)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.show()

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Select an image", "",
                                                   "Images (*.png *.jpg);;All Files (*)", options=options)
        if file_name:
            self.window().input_file = FileManager(file_name)
            self.img_path = self.window().input_file.name
            self.load_image(file_name=self.img_path)

    def load_image(self, file_name):
        pixMap = QPixmap(file_name)
        self.vanish_point_eng = VanishingPointEng(pixMap.height(), pixMap.width())
        self.load_new_image(self.vanish_point_eng)
        self.scene = GraphicsScene(self.vanish_point_eng)
        print(pixMap.size())
        self.scene.addPixmap(pixMap)
        self.view.setScene(self.scene)
        print('Openning: ' + file_name)

    @pyqtSlot()
    def on_click(self):
        self.open_file_name_dialog()

    @pyqtSlot()
    def on_add_click(self):
        self.window().line_group_dock.add_line_group()
        self.view.viewport().setCursor(Qt.CrossCursor)

    @pyqtSlot()
    def on_add_point_click(self):
        self.window().init_coor_dock.add_layer()

    def draw_point(self, x, y):
        self.scene.draw_point(x, y)