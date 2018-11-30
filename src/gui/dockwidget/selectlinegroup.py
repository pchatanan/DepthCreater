from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDockWidget, QListWidget, QListWidgetItem, QWidget, QLabel, QHBoxLayout

from engine.vanishingpoint import Wizard


class LineGroupWidget(QWidget):

    def __init__(self, index, *__args):
        super().__init__(*__args)
        self.index = index
        self.ui_layername = QLabel("Line Group " + str(index + 1))
        self.coordinate_text = QLabel("(-,-)")

        self.hBox0 = QHBoxLayout()
        self.hBox0.addWidget(self.ui_layername)
        self.hBox0.addStretch()
        self.hBox0.addWidget(self.coordinate_text)

        self.setLayout(self.hBox0)

    def set_coordinate(self, coordinate):
        text = ("({:.1f}, {:.1f})".format(coordinate[0], coordinate[1]))
        self.coordinate_text.setText(text)


class SelectLineGroup(QDockWidget):
    def __init__(self, vp_eng, *__args):
        super().__init__(*__args)
        self.listWidget = None
        self.vp_eng = None
        self.reset(vp_eng)

    def addCallback(self):
        self.window().centralWidget().graphics_view.set_on_vp_drawn(self.on_vp_drawn)

    def reset(self, vp_eng):
        self.listWidget = QListWidget()
        self.vp_eng = vp_eng

        self.add_line_group()
        self.add_line_group()
        self.add_line_group()

        self.listWidget.item(0).setSelected(True)
        self.listWidget.setFocus()

        self.listWidget.itemClicked.connect(self.item_click)
        self.setWidget(self.listWidget)

    def add_line_group(self):
        index = self.listWidget.count()
        widget = LineGroupWidget(index)
        item = QListWidgetItem()
        item.setData(Qt.UserRole, index)
        self.listWidget.addItem(item)
        self.listWidget.setItemWidget(item, widget)
        self.vp_eng.lines.append([])
        self.vp_eng.vpoints.append([])
        item.setSizeHint(widget.sizeHint())

    def on_vp_drawn(self, coordinate, row):
        widget = self.listWidget.itemWidget(self.listWidget.item(row))
        widget.set_coordinate(coordinate)

    @pyqtSlot()
    def item_click(self):
        self.vp_eng.set_current_wizard(Wizard.ADD_LINE)
        index = self.listWidget.currentItem().data(Qt.UserRole)
        self.vp_eng.set_line_group(index)
