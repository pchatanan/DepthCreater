from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDockWidget, QListWidget, QListWidgetItem, QLineEdit, QFormLayout, QLabel, QVBoxLayout, \
    QWidget, QHBoxLayout, QPushButton, QCheckBox

from engine.fix_perspective import FixPerspective
from engine.mathsengine import line, intersection, calculate_compass_bearing, reflect_y, rearrange_point


class LayerWidget(QWidget):

    def __init__(self, index, point_selected, *__args):
        super().__init__(*__args)
        self.index = index
        self.point_selected = point_selected
        self.ui_layername = QLabel("Point " + str(index + 1))
        self.coordinate_text = QLabel("(-,-)")
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(lambda: self.checkbox_changed(self.checkbox))

        self.x_edit = QLineEdit()
        self.x_edit.setFixedWidth(60)
        self.y_edit = QLineEdit()
        self.y_edit.setFixedWidth(60)
        self.z_edit = QLineEdit()
        self.z_edit.setFixedWidth(60)

        x_label = QLabel("x")
        y_label = QLabel("y")
        z_label = QLabel("z")

        self.hBox0 = QHBoxLayout()
        self.hBox0.addWidget(self.ui_layername)
        self.hBox0.addStretch()
        self.hBox0.addWidget(self.coordinate_text)
        self.hBox0.addWidget(self.checkbox)

        self.hBox = QHBoxLayout()
        self.hBox.addWidget(x_label)
        self.hBox.addWidget(self.x_edit)
        self.hBox.addWidget(y_label)
        self.hBox.addWidget(self.y_edit)
        self.hBox.addWidget(z_label)
        self.hBox.addWidget(self.z_edit)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.hBox0)
        self.main_layout.addLayout(self.hBox)

        self.setLayout(self.main_layout)

    def set_coordinate(self, coordinate):
        self.coordinate_text.setText("(" + str(coordinate[0]) + ", " + str(coordinate[1]) + ")")

    def checkbox_changed(self, checkbox):
        if checkbox.isChecked():
            self.point_selected.append(self.index)
        else:
            self.point_selected.remove(self.index)


class SelectInitCoordinate(QDockWidget):
    def __init__(self, vanish_point_eng, *__args):
        super().__init__(*__args)
        self.vanish_point_eng = vanish_point_eng

        self.point_selected = []
        # point0 = self.vanish_point_eng.coordinates[self.point_selected[0]]
        # point1 = self.vanish_point_eng.coordinates[self.point_selected[1]]

        # set UI
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.item_click)
        self.xy_button = QPushButton("Use XY")
        self.xy_button.clicked.connect(lambda: self.extract_side("XY", self.vanish_point_eng.coordinates[self.point_selected[0]], self.vanish_point_eng.coordinates[self.point_selected[1]]))
        self.xz_button = QPushButton("Use XZ")
        self.xz_button.clicked.connect(lambda: self.extract_side("XZ", self.vanish_point_eng.coordinates[self.point_selected[0]], self.vanish_point_eng.coordinates[self.point_selected[1]]))
        self.yz_button = QPushButton("Use YZ")
        self.yz_button.clicked.connect(lambda: self.extract_side("YZ", self.vanish_point_eng.coordinates[self.point_selected[0]], self.vanish_point_eng.coordinates[self.point_selected[1]]))
        self.hBox = QHBoxLayout()
        self.hBox.addWidget(self.xy_button)
        self.hBox.addWidget(self.xz_button)
        self.hBox.addWidget(self.yz_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addLayout(self.hBox)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        self.setWidget(self.main_widget)

        self.add_layer()
        self.add_layer()
        self.add_layer()

    def add_layer(self):
        index = self.list_widget.count()
        widget = LayerWidget(index, self.point_selected)
        item = QListWidgetItem()
        item.setData(Qt.UserRole, index)
        self.list_widget.insertItem(index, item)
        self.list_widget.setItemWidget(item, widget)
        self.vanish_point_eng.coordinates.append([0, 0])
        item.setSizeHint(widget.sizeHint())

    def setText(self, coordinate):
        widget = self.list_widget.itemWidget(self.list_widget.currentItem())
        widget.set_coordinate(coordinate)

    def extract_side(self, axis, point0, point1):
        xvpoint = self.vanish_point_eng.vpoints[0]
        yvpoint = self.vanish_point_eng.vpoints[1]
        zvpoint = self.vanish_point_eng.vpoints[2]

        basename = self.window().input_file.name

        if axis == "XY":
            vpoint1 = xvpoint
            vpoint2 = yvpoint
            img_out = "output/" + basename + "/" + basename + "(top).png"
        elif axis == "XZ":
            vpoint1 = xvpoint
            vpoint2 = zvpoint
            img_out = "output/" + basename + "/" + basename + "(right).png"
        elif axis == "YZ":
            vpoint1 = yvpoint
            vpoint2 = zvpoint
            img_out = "output/" + basename + "/" + basename + "(left).png"

        L1 = line(point0, vpoint1)
        L2 = line(point1, vpoint2)
        R1 = [round(i) for i in intersection(L1, L2)]
        if R1:
            print("Intersection 1 detected:", R1)
        else:
            print("No single intersection point detected")

        L1 = line(point0, vpoint2)
        L2 = line(point1, vpoint1)
        R2 = [round(i) for i in intersection(L1, L2)]
        if R1:
            print("Intersection 2 detected:", R2)
        else:
            print("No single intersection point detected")

        all_points = [point0, point1, R1, R2]
        ordered_points = rearrange_point(all_points)

        engine = FixPerspective(self.window().input_file.base, img_out, ordered_points, 400,
                                400)
        engine.show()

    @pyqtSlot()
    def item_click(self):
        self.window().centralWidget().view.set_coordinate_index(self.list_widget.currentItem().data(Qt.UserRole),
                                                                self.setText)
