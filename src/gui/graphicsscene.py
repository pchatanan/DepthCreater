from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsTextItem

from enum import Enum

from engine.vanishingpoint import Wizard
from gui.dialog import show_input_dialog, show_dialog

LINE_COLORS = [Qt.blue, Qt.red, Qt.green]


class Component(Enum):
    LINE = 1
    POINT = 2


class GraphicsScene(QGraphicsScene):
    MODE_IDLE, MODE_PRESS, MODE_DRAW = range(3)

    def __init__(self, vanish_point_eng, widget_context, *__args):
        super().__init__(*__args)
        self.vanish_point_eng = vanish_point_eng
        self.scene_mode = self.MODE_IDLE
        self.orig_point = None
        self.lines = []
        self.item_to_draw = None
        self.points = []
        self.point_labels = []
        self.widget_context = widget_context

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
                QPen(self.get_pen_color(Component.LINE), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
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
            #  TODO: specify what to do with the line here
            self.vanish_point_eng.add_line(line, self.on_line_added)
            graphic_view.viewport().setCursor(Qt.ArrowCursor)
        elif self.scene_mode == self.MODE_PRESS:
            index = graphic_view.coordinate_index
            print("clicked!! at " + str(index))
            self.vanish_point_eng.add_coordinate(index, [x1, y1])
            graphic_view.coordinate_set_callback([x1, y1])

            circle_item = QGraphicsEllipseItem(x1 - 5, y1 - 5, 10, 10)
            circle_item.setPen(QPen(self.get_pen_color(Component.LINE), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
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

    def on_line_added(self, wizard, step):
        if wizard == Wizard.ADD_LINE:
            print("Line is added.")
        elif wizard == Wizard.DEFINE_PLANE:
            text, ok = show_input_dialog(self.widget_context, "Length Input", "Please input " + "x" if step == 1 else "y" + " length reference.")
            if ok:
                self.vanish_point_eng.set_length(float(text), wizard, step, self.handle_on_length_set)
        elif wizard == Wizard.DEFINE_HEIGHT:
            text, ok = show_input_dialog(self.widget_context, "Length Input", "Please input height reference.")
            if ok:
                self.vanish_point_eng.set_length(float(text), wizard, step, self.handle_on_length_set)

    def handle_on_length_set(self, wizard, step):
        if wizard == Wizard.DEFINE_PLANE:
            if step == 1:
                show_dialog("Define a plane: Step 2",
                            "Draw a line in the y-direction and specify its length.")
            if step == 2:
                show_dialog("End of define plane wizard",
                            "Your XY-plane is set.")
        elif wizard == Wizard.DEFINE_HEIGHT:
            show_dialog("End of define height wizard",
                        "Height is set.")

    def get_graphic_view(self):
        return self.views()[0]

    def draw_point(self, x, y):
        self.addEllipse(x - 10, y - 10, 20, 20,
                        QPen(self.get_pen_color(Component.LINE), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin),
                        QBrush(Qt.black, Qt.SolidPattern))

    def get_pen_color(self, component):
        if component == Component.LINE:
            return LINE_COLORS[self.vanish_point_eng.get_line_group()]
        elif component == Component.POINT:
            return None
