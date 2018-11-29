from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QWidget

from engine.vanishingpoint import VanishingPointEng
from gui.grapgicsview import GraphicsView
from gui.graphicsscene import GraphicsScene
from util.filemanager import FileManager


class CentralWidget(QWidget):
    def __init__(self, img_path, on_image_loaded, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        # init graphics view and empty scene
        self.graphics_view = GraphicsView(self)
        self.graphics_scene = None

        # init data and engine
        self.vanish_point_eng = None
        self.img_path = img_path

        # load startup image
        self.on_image_loaded = on_image_loaded
        self.load_image(self.img_path)

        # manage GUI
        add_button = QPushButton("Add line")
        add_button.clicked.connect(self.on_add_click)
        cancel_button = QPushButton("Cancel")
        add_point_button = QPushButton("Add point")
        add_point_button.clicked.connect(self.on_add_point_click)

        bottom_buttons_view = QHBoxLayout()
        bottom_buttons_view.addStretch(1)
        bottom_buttons_view.addWidget(cancel_button, alignment=Qt.AlignCenter)
        bottom_buttons_view.addWidget(add_button, alignment=Qt.AlignCenter)
        bottom_buttons_view.addWidget(add_point_button, alignment=Qt.AlignCenter)
        bottom_buttons_view.addStretch(1)

        v_box = QVBoxLayout()
        v_box.addWidget(self.graphics_view)
        v_box.addLayout(bottom_buttons_view)

        self.setLayout(v_box)
        self.show()

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "Select an image", "",
                                                   "Images (*.png *.jpg);;All Files (*)", options=options)
        if file_name:
            self.window().input_file = FileManager(file_name)
            self.img_path = self.window().input_file.abspath
            self.load_image(self.img_path)

    def load_image(self, file_name):
        print('Opening: ' + file_name)
        pix_map = QPixmap(file_name)
        image_shape = (pix_map.width(), pix_map.height())
        # reset engine
        self.vanish_point_eng = VanishingPointEng()
        self.vanish_point_eng.set_shape(image_shape)
        self.graphics_scene = GraphicsScene(self.vanish_point_eng, self)
        self.graphics_scene.addPixmap(pix_map)
        self.graphics_view.setScene(self.graphics_scene)
        self.on_image_loaded(self.vanish_point_eng)

    @pyqtSlot()
    def on_add_click(self):
        self.window().line_group_dock.add_line_group()
        self.graphics_view.viewport().setCursor(Qt.CrossCursor)

    @pyqtSlot()
    def on_add_point_click(self):
        self.window().point_dock.add_layer()

    def draw_point(self, x, y):
        self.graphics_scene.draw_point(x, y)

    def get_graphics_scene(self):
        return self.graphics_scene
