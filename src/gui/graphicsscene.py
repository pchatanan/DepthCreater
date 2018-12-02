from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem

from enum import Enum

from engine.vanishingpoint import Wizard
from gui.dialog import show_input_dialog, show_dialog

LINE_COLORS = [Qt.blue, Qt.red, Qt.green]


class GraphicsScene(QGraphicsScene):
    MODE_IDLE, MODE_PRESS, MODE_DRAW = range(3)

    def __init__(self, vanish_point_eng, widget_context, *__args):
        super().__init__(*__args)
        self.vp_eng = vanish_point_eng
        self.scene_mode = self.MODE_IDLE
        self.orig_point = None
        self.lines = []
        self.item_to_draw = None
        self.points = []
        self.point_labels = []
        self.widget_context = widget_context
        self.vpoints = []
        self.vpoint_labels = []

        self.vp_dict = {
            "x": {
                "vp": None,
                "label": None
            },
            "y": {
                "vp": None,
                "label": None
            },
            "z": {
                "vp": None,
                "label": None
            }
        }

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.views()[0].set_center(event.scenePos())
        if self.scene_mode == self.MODE_IDLE:
            self.orig_point = event.scenePos()
            self.scene_mode = self.MODE_PRESS
            self.lines.append(QGraphicsLineItem())

    def mouseMoveEvent(self, event):
        if self.scene_mode != self.MODE_IDLE:
            self.scene_mode = self.MODE_DRAW
            self.item_to_draw = self.lines[-1]
            self.item_to_draw.setLine(self.orig_point.x(),
                                      self.orig_point.y(),
                                      event.scenePos().x(),
                                      event.scenePos().y())
            self.item_to_draw.setPen(
                QPen(self.get_pen_color(), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.addItem(self.item_to_draw)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        x1 = self.orig_point.x()
        y1 = self.orig_point.y()
        x2 = event.scenePos().x()
        y2 = event.scenePos().y()
        line = (x1, y1, x2, y2)
        graphic_view = self.get_graphic_view()
        if self.scene_mode == self.MODE_DRAW:
            self.vp_eng.add_line(line, self.on_line_added)
            graphic_view.viewport().setCursor(Qt.ArrowCursor)
        elif self.scene_mode == self.MODE_PRESS:
            point = [x1, y1]
            index = graphic_view.coordinate_index

            self.vp_eng.add_coordinate(index, point)
            graphic_view.coordinate_set_callback(point)

            circle_item = QGraphicsEllipseItem(x1 - 5, y1 - 5, 10, 10)
            circle_item.setPen(QPen(self.get_pen_color(), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            circle_item.setBrush(QBrush(Qt.black, Qt.SolidPattern))

            text_item = QGraphicsTextItem()
            text_item.setPos(x1, y1)
            text_item.setPlainText("Point " + str(index + 1))

            if len(self.points) <= index:
                self.points.append(circle_item)
                self.point_labels.append(text_item)
            else:
                self.removeItem(self.points.pop(index))
                self.points.insert(index, circle_item)

                self.removeItem(self.point_labels.pop(index))
                self.point_labels.insert(index, text_item)
            self.addItem(circle_item)
            self.addItem(text_item)
        self.scene_mode = self.MODE_IDLE

    def on_line_added(self, wizard, data=None):
        if wizard == Wizard.ADD_LINE:
            print("Line is added.")
        elif wizard == Wizard.SET_REF_LENGTH:
            axis = self.vp_eng.get_key_from_id()
            text, ok = show_input_dialog(self.widget_context, "Reference Length Input",
                                         "Detected {}-axis: Please input length reference.".format(axis))
            if ok:
                self.vp_eng.set_length(float(text), wizard, self.handle_on_length_set)
        elif wizard == Wizard.MEASURE_ON_PLANE:
            show_dialog("Length calculated",
                        "The length is approximately {}".format(data))
        elif wizard == Wizard.MEASURE_HEIGHT:
            show_dialog("Length calculated",
                        "The length is approximately {:.1f}".format(data))

    def handle_on_length_set(self, wizard):
        if wizard == Wizard.SET_REF_LENGTH:
            axis = self.vp_eng.get_key_from_id()
            show_dialog("Callback",
                        "Reference length in the {}-axis is set.".format(axis))
            print(self.vp_eng.calibration["x"])

    def get_graphic_view(self):
        return self.views()[0]

    def draw_point(self, x, y):
        self.addEllipse(x - 10, y - 10, 20, 20,
                        QPen(self.get_pen_color(), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin),
                        QBrush(Qt.black, Qt.SolidPattern))

    def draw_vp(self, point, index):
        key = self.vp_eng.get_key_from_id(index)
        print("drawing at {} {}".format(point, key))
        x, y = point
        r = 10

        graphic_view = self.get_graphic_view()

        graphic_view.vp_drawn_callback(point, index)
        self.vp_eng.add_vpoint(index, point)

        circle_item = QGraphicsEllipseItem(x - r, y - r, 2 * r, 2 * r)
        circle_item.setPen(QPen(self.get_pen_color(), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        circle_item.setBrush(QBrush(Qt.black, Qt.SolidPattern))

        text_item = QGraphicsTextItem()
        text_item.setPos(x, y)
        text_item.setPlainText("V{}".format(key))

        if self.vp_dict[key]["vp"] is not None:
            self.removeItem(self.vp_dict[key]["vp"])
            self.removeItem(self.vp_dict[key]["label"])

        self.vp_dict[key]["vp"] = circle_item
        self.vp_dict[key]["label"] = text_item
        self.addItem(circle_item)
        self.addItem(text_item)

    def get_pen_color(self):
        if self.vp_eng.current_wizard == Wizard.ADD_LINE:
            return LINE_COLORS[self.vp_eng.get_line_group()]
        elif self.vp_eng.current_wizard == Wizard.ADD_POINT:
            return Qt.white
        elif self.vp_eng.current_wizard == Wizard.SET_REF_LENGTH:
            return Qt.yellow
        else:
            return Qt.black
