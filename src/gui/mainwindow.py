from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QMainWindow, QMenu, QAction

from engine.circle_method import auto_detect_vp
from engine.fix_perspective import FixPerspective
from engine.mathsengine import rearrange_point
from engine.vrml_creator import VrmlCreator
from gui.centralwidget import CentralWidget
from gui.dockwidget.selectinitcoor import SelectInitCoordinate
from gui.dockwidget.selectlinegroup import SelectLineGroup
from util.filemanager import FileManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.statusBar().showMessage('Ready')
        screen_rect = QtWidgets.QDesktopWidget().screenGeometry(screen=-1)
        self.width = 1600
        self.height = 900
        self.left = screen_rect.width() / 2 - self.width / 2
        self.top = screen_rect.height() / 2 - self.height / 2
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('DepthCreator')

        self.line_group_dock = None
        self.init_coor_dock = None

        self.input_file = FileManager("building.jpg")
        self.central_widget = CentralWidget(self.input_file.base, self.load_new_image, flags=None)
        self.setCentralWidget(self.central_widget)

        # menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        addMenu = menubar.addMenu('Add')
        calMenu = menubar.addMenu('Calculate')

        # file Menu
        impMenu = QMenu('Import', self)
        impAct = QAction('Import mail', self)
        impMenu.addAction(impAct)

        newAct = QAction(QIcon('res/icon/open-folder-outline.png'), 'Open', self)
        newAct.triggered.connect(self.central_widget.open_file_name_dialog)

        # add Menu
        addLineGroupAct = QAction(QIcon('tick.png'), 'Add Line Group', self)
        addLineGroupAct.triggered.connect(self.line_group_dock.add_line_group)
        addMenu.addAction(addLineGroupAct)

        # calculate Menu

        autoDetectVPointAct = QAction(QIcon('tick.png'), 'Detect VPoints', self)
        autoDetectVPointAct.triggered.connect(self.detect_vpoints)
        calMenu.addAction(autoDetectVPointAct)

        vanishingPntAct = QAction(QIcon('tick.png'), 'Vanishing Point', self)
        vanishingPntAct.triggered.connect(self.draw_vanishing_point)
        calMenu.addAction(vanishingPntAct)

        fixPerspectiveAct = QAction(QIcon('tick.png'), 'Fix Perspective', self)
        fixPerspectiveAct.triggered.connect(self.fix_perspective)
        calMenu.addAction(fixPerspectiveAct)

        extractThreeSidesAct = QAction(QIcon('tick.png'), 'Extract 3 sides', self)
        extractThreeSidesAct.triggered.connect(self.extract_three_side)
        calMenu.addAction(extractThreeSidesAct)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(newAct)

        fileMenu.addAction(newAct)
        fileMenu.addMenu(impMenu)

        self.show()
        self.showMaximized()

    def draw_vanishing_point(self):
        x, y = self.vanish_point_eng.calculate_vanishing_point()
        self.central_widget.draw_point(x, y)

    def fix_perspective(self):
        points = self.vanish_point_eng.get_coordinates()
        engine = FixPerspective(self.input_file.base, "output\\image_out.png", rearrange_point(points), 400, 400)
        engine.show()

    def extract_three_side(self):
        points = self.vanish_point_eng.get_coordinates()
        self.init_coor_dock.extract_side("XY", points[0], points[1])
        self.init_coor_dock.extract_side("XZ", points[1], points[2])
        self.init_coor_dock.extract_side("YZ", points[0], points[2])
        vrml_creator = VrmlCreator(self.input_file.name, 4, 4, 4)
        vrml_creator.create()

    def detect_vpoints(self):
        vpoints = auto_detect_vp(self.input_file, 2)
        ordered_vpoints = []

        while len(vpoints) > 0:
            x_list = [e[0] for e in vpoints]
            min_x = min(x_list)
            min_index = x_list.index(min_x)
            ordered_vpoints.append(vpoints.pop(min_index))

        ordered_vpoints.insert(0, ordered_vpoints.pop())

        self.vanish_point_eng.vpoints = ordered_vpoints
        for vp in ordered_vpoints:
            self.central_widget.draw_point(vp[0], vp[1])

    def load_new_image(self, vanish_point_eng):
        self.vanish_point_eng = vanish_point_eng
        if self.line_group_dock is not None:
            self.removeDockWidget(self.line_group_dock)
        if self.init_coor_dock is not None:
            self.removeDockWidget(self.init_coor_dock)
        self.line_group_dock = SelectLineGroup(self.vanish_point_eng, "Line Group (Title)", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.line_group_dock)
        self.init_coor_dock = SelectInitCoordinate(self.vanish_point_eng, "Input Coordinate (Title)", self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.init_coor_dock)


