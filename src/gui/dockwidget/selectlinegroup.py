from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDockWidget, QListWidget, QListWidgetItem

from engine.vanishingpoint import Wizard


class SelectLineGroup(QDockWidget):
    def __init__(self, vp_eng, *__args):
        super().__init__(*__args)
        self.listWidget = None
        self.vp_eng = None
        self.reset(vp_eng)

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
        n = self.listWidget.count()
        item = QListWidgetItem('Line Group ' + str(n + 1))
        item.setData(Qt.UserRole, n)
        self.listWidget.addItem(item)
        self.vp_eng.lines.append([])
        self.vp_eng.vpoints.append([])

    @pyqtSlot()
    def item_click(self):
        self.vp_eng.set_current_wizard(Wizard.ADD_LINE)
        self.vp_eng.set_line_group(self.listWidget.currentItem().data(Qt.UserRole))
