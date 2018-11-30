from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QDesktopWidget

from engine.circle_method import auto_detect_vp
from engine.fix_perspective import FixPerspective
from engine.mathsengine import rearrange_point
from engine.vanishingpoint import Wizard
from engine.vrml_creator import VrmlCreator
from gui.centralwidget import CentralWidget
from gui.dialog import show_dialog
from gui.dockwidget.selectinitcoor import SelectInitCoordinate
from gui.dockwidget.selectlinegroup import SelectLineGroup
from opencv_engine import sort_point_list
from util.filemanager import FileManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.statusBar().showMessage('Ready')
        screen_rect = QDesktopWidget().screenGeometry(screen=-1)
        self.width = 1600
        self.height = 900
        self.left = screen_rect.width() / 2 - self.width / 2
        self.top = screen_rect.height() / 2 - self.height / 2
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle('DepthCreator')

        self.vp_eng = None

        self.line_group_dock = None
        self.point_dock = None

        self.input_file = FileManager("./sample_images/building.jpg")
        self.central_widget = CentralWidget(self.input_file.abspath, self.on_image_loaded, flags=None)
        self.setCentralWidget(self.central_widget)

        self.line_group_dock.addCallback()

        # main menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        add_menu = menu_bar.addMenu('Add')
        cal_menu = menu_bar.addMenu('Calculate')
        wizard_menu = menu_bar.addMenu('Wizard')

        # file_menu
        open_submenu = QMenu('Open', self)
        open_img_act = QAction(QIcon('res/icon/open-folder.png'), 'Image', self)
        open_img_act.triggered.connect(self.central_widget.open_file_name_dialog)
        open_submenu.addAction(open_img_act)
        file_menu.addMenu(open_submenu)

        # add_menu
        add_line_group_act = QAction(QIcon('tick.png'), 'Add Line Group', self)
        add_line_group_act.triggered.connect(self.window().line_group_dock.add_line_group)
        add_menu.addAction(add_line_group_act)

        # calculate Menu
        auto_detect_v_point_act = QAction(QIcon('res/icon/cube.png'), 'Detect Vanishing Points', self)
        auto_detect_v_point_act.triggered.connect(self.detect_v_points)
        cal_menu.addAction(auto_detect_v_point_act)

        calculate_intersection_act = QAction(QIcon('res/icon/intersection.png'), 'Calculate Intersection', self)
        calculate_intersection_act.triggered.connect(self.draw_vanishing_point)
        cal_menu.addAction(calculate_intersection_act)

        # wizard_menu
        define_plane_act = QAction(QIcon('tick.png'), 'Define a plane', self)
        define_plane_act.triggered.connect(self.define_plane)
        wizard_menu.addAction(define_plane_act)

        define_height_act = QAction(QIcon('tick.png'), 'Set height reference', self)
        define_height_act.triggered.connect(self.define_height)
        wizard_menu.addAction(define_height_act)

        measure_on_plane = QAction(QIcon('tick.png'), 'Measure on plane', self)
        measure_on_plane.triggered.connect(self.measure_plane)
        wizard_menu.addAction(measure_on_plane)

        measure_height_act = QAction(QIcon('tick.png'), 'Measure height', self)
        measure_height_act.triggered.connect(self.measure_height)
        wizard_menu.addAction(measure_height_act)



        fixPerspectiveAct = QAction(QIcon('tick.png'), 'Fix Perspective', self)
        fixPerspectiveAct.triggered.connect(self.fix_perspective)
        cal_menu.addAction(fixPerspectiveAct)

        extractThreeSidesAct = QAction(QIcon('tick.png'), 'Extract 3 sides', self)
        extractThreeSidesAct.triggered.connect(self.extract_three_side)
        cal_menu.addAction(extractThreeSidesAct)

        # toolbar
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(open_img_act)
        self.toolbar.addAction(auto_detect_v_point_act)
        self.toolbar.addAction(calculate_intersection_act)

        self.show()
        self.showMaximized()

    def draw_vanishing_point(self):
        point = self.vp_eng.calculate_vanishing_point()
        self.central_widget.draw_point(point)

    def fix_perspective(self):
        points = self.vp_eng.get_coordinates()
        engine = FixPerspective(self.input_file.base, "output\\image_out.png", rearrange_point(points), 400, 400)
        engine.show()

    def extract_three_side(self):
        points = self.vp_eng.get_coordinates()
        self.point_dock.extract_side("XY", points[0], points[1])
        self.point_dock.extract_side("XZ", points[1], points[2])
        self.point_dock.extract_side("YZ", points[0], points[2])
        vrml_creator = VrmlCreator(self.input_file.name, 4, 4, 4)
        vrml_creator.create()

    def detect_v_points(self):
        v_points = auto_detect_vp(self.input_file)
        for index, vp in enumerate(v_points):
            self.central_widget.draw_point(vp, index)

    def define_plane(self):
        show_dialog("Define a plane: Step 1",
                    "Draw a line in the x-direction and specify its length.",
                    on_button_clicked=self.define_plane_step_1)

    def define_plane_step_1(self, i):
        print(i.text() + " is clicked.")
        if i.text() == "OK":
            self.vp_eng.set_current_wizard(Wizard.DEFINE_PLANE)
            print("wait for line")

    def define_height(self):
        show_dialog("Set height reference",
                    "Draw a line and specify height reference.",
                    on_button_clicked=self.handle_define_height)

    def handle_define_height(self, button_clicked):
        if button_clicked.text() == "OK":
            self.vp_eng.set_current_wizard(Wizard.DEFINE_HEIGHT)

    def measure_plane(self):
        show_dialog("Measure length on plane",
                    "Draw a line to measure length on the define plane.",
                    on_button_clicked=self.handle_measure_plane)

    def handle_measure_plane(self, button_clicked):
        print(button_clicked.text() + " is clicked.")
        if button_clicked.text() == "OK":
            self.vp_eng.set_current_wizard(Wizard.MEASURE_ON_PLANE)
            print("wait for measure line")

    def measure_height(self):
        show_dialog("Measure height",
                    "Draw a line to measure height with respect to the defined plane.",
                    on_button_clicked=self.handle_measure_height)

    def handle_measure_height(self, button_clicked):
        print(button_clicked.text() + " is clicked.")
        if button_clicked.text() == "OK":
            self.vp_eng.set_current_wizard(Wizard.MEASURE_HEIGHT)
            print("wait for measure height line")

    def on_image_loaded(self, vp_eng):
        self.vp_eng = vp_eng
        # init line group dock
        if self.line_group_dock is not None:
            self.line_group_dock.reset(vp_eng)
        else:
            self.line_group_dock = SelectLineGroup(self.vp_eng, "Line Group (Title)", self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.line_group_dock)
        # point dock
        if self.point_dock is not None:
            self.point_dock.reset(vp_eng)
        else:
            self.point_dock = SelectInitCoordinate(self.vp_eng, "Input Coordinate (Title)", self)
            self.addDockWidget(Qt.RightDockWidgetArea, self.point_dock)




