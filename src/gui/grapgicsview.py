from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QCursor


class GraphicsView(QGraphicsView):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.center_x = self.viewport().size().width() / 2
        self.center_y = self.viewport().size().height() / 2
        self.offset_x = 0
        self.offset_y = 0
        self.line_group = 0
        self.coordinate_index = 0
        self.coordinate_set_callback = None
        self.ctrl_pressed = False

    def set_coordinate_index(self, index, callback):
        self.coordinate_index = index
        self.coordinate_set_callback = callback
        print("Coordinate Index " + str(index) + " is selected.")

    def set_line_group(self, num):
        self.line_group = num
        print("Line Group " + str(num + 1) + " is selected.")

    def mousePressEvent(self, event):
        self.cam_x = event.pos().x()
        self.cam_y = event.pos().y()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        x = event.pos().x()
        y = event.pos().y()

        if x > self.viewport().size().width():
            self.offset_x = x - self.viewport().size().width()
            QCursor().setPos(event.globalPos().x() - self.offset_x, event.globalPos().y())
        if y > self.viewport().size().height():
            self.offset_y = y - self.viewport().size().height()
            QCursor().setPos(event.globalPos().x(), event.globalPos().y() - self.offset_y)
        if x < 0:
            self.offset_x = x
            QCursor().setPos(event.globalPos().x() - self.offset_x, event.globalPos().y())
        if y < 0:
            self.offset_y = y
            QCursor().setPos(event.globalPos().x(), event.globalPos().y() - self.offset_y)
        if x > self.viewport().size().width() or y > self.viewport().size().height() or x < 0 or y < 0:
            self.set_center_on()

    def set_center_on(self):
        self.center_x += self.offset_x
        self.center_y += self.offset_y
        self.centerOn(self.center_x, self.center_y)

    def set_center(self, scene_pos):
        s = self.viewport().size().width() - self.cam_x
        t = self.viewport().size().height() - self.cam_y
        u = (self.viewport().size().width() / 2) - s
        v = (self.viewport().size().height() / 2) - t
        self.center_x = scene_pos.x() - u
        self.center_y = scene_pos.y() - v
        pass

    def wheelEvent(self, event):
        super().wheelEvent(event)
        if self.ctrl_pressed:
            # Zoom Factor
            zoom_in_factor = 1.1
            zoom_out_factor = 1 / zoom_in_factor

            # Set Anchors
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.setResizeAnchor(QGraphicsView.NoAnchor)

            # Save the scene pos
            old_pos = self.mapToScene(event.pos())

            # Zoom
            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor
            self.scale(zoom_factor, zoom_factor)

            # Get the new position
            new_pos = self.mapToScene(event.pos())

            # Move scene to old position
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = True

    def keyReleaseEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False
