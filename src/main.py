import sys
from gui.mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
