from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDockWidget, QListWidget, QListWidgetItem


class SelectLineGroup(QDockWidget):
    def __init__(self, vanish_point_eng, *__args):
        super().__init__(*__args)
        self.listWidget = QListWidget()
        self.vanish_point_eng = vanish_point_eng

        self.add_line_group()
        self.add_line_group()
        self.add_line_group()

        print("Set initial Line Group")
        self.listWidget.item(0).setSelected(True)
        self.listWidget.setFocus()

        self.listWidget.itemClicked.connect(self.item_click)
        self.setWidget(self.listWidget)

    def add_line_group(self):
        n = self.listWidget.count()
        item = QListWidgetItem('Line Group ' + str(n+1))
        item.setData(Qt.UserRole, n)
        self.listWidget.addItem(item)
        self.vanish_point_eng.lines.append([])
        self.vanish_point_eng.vpoints.append([])

    @pyqtSlot()
    def item_click(self):
        self.window().centralWidget().view.set_line_group(self.listWidget.currentItem().data(Qt.UserRole))
        self.vanish_point_eng.set_line_group(self.listWidget.currentItem().data(Qt.UserRole))


