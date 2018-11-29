from enum import Enum

import numpy as np

from engine.opencv_utils import norm_cross, compute_length


class Wizard(Enum):
    ADD_LINE = 1
    DEFINE_PLANE = 2
    MEASURE_ON_PLANE = 3
    DEFINE_HEIGHT = 4
    MEASURE_HEIGHT = 5
    ADD_POINT = 6


class VanishingPointEng:

    def __init__(self):
        self.lines = []
        self.height = None
        self.width = None
        self.id = 0
        self.coordinates = []
        self.vpoints = []
        self.x_ref_line = None
        self.x_ref_length = None
        self.y_ref_line = None
        self.y_ref_length = None
        self.z_ref_line = None
        self.z_ref_length = None
        self.current_wizard = Wizard.ADD_LINE
        self.step = 1

    def set_shape(self, shape):
        self.width = shape[0]
        self.height = shape[1]

    def add_line(self, line, on_line_added):
        x1, y1, x2, y2 = line
        if self.current_wizard == Wizard.ADD_LINE:
            # translate to origin at bottom left
            y1 = self.height - y1
            y2 = self.height - y2

            m = (y1 - y2) / (x1 - x2)
            c = y1 - (m * x1)
            self.lines[self.id].append([m, c])
            on_line_added(self.current_wizard, self.step)
        elif self.current_wizard == Wizard.DEFINE_PLANE:
            if self.step == 1:
                self.x_ref_line = line
            if self.step == 2:
                self.y_ref_line = line
            on_line_added(self.current_wizard, self.step)
            self.step += 1
        elif self.current_wizard == Wizard.MEASURE_ON_PLANE:
            self.measure_on_plane(line)
            on_line_added(self.current_wizard, self.step)
        elif self.current_wizard == Wizard.DEFINE_HEIGHT:
            self.z_ref_line = line
            on_line_added(self.current_wizard, self.step)
        elif self.current_wizard == Wizard.MEASURE_HEIGHT:
            self.measure_height(line)
            on_line_added(self.current_wizard, self.step)

    def set_line_group(self, id):
        self.id = id

    def get_line_group(self):
        return self.id

    def calculate_vanishing_point(self):
        if self.id > len(self.lines) - 1:
            print('please select line group')
            return

        lineList = self.lines[self.id]
        if len(lineList) < 2:
            print('please draw more lines')
            return

        lineList = np.array(lineList)

        ones = np.ones((lineList.shape[0], 1))

        neg_m = (-1) * (lineList[:, 0][:, None])
        b = lineList[:, 1][:, None]

        print(ones)
        print(neg_m)

        a = np.concatenate((ones, neg_m), axis=1)

        print('calculating')

        y, x = np.linalg.lstsq(a, b, rcond=None)[0]

        # convert to graphics coordinates
        y = self.height - y

        print(self.vpoints)
        self.vpoints[self.id] = [x[0], y[0]]
        print(self.vpoints)

        print("vPoint: " + str(x) + ", " + str(y))


        return x, y

    def add_coordinate(self, index, coordinate):
        print("setting")
        self.coordinates[index] = coordinate

    def get_coordinates(self):
        return self.coordinates

    def set_current_wizard(self, wizard):
        self.current_wizard = wizard
        self.step = 1

    def set_length(self, length, wizard, step, onLengthSet):
        if wizard == Wizard.DEFINE_PLANE:
            if step == 1:
                self.x_ref_length = length
            elif step == 2:
                self.y_ref_length = length
        elif wizard == Wizard.DEFINE_HEIGHT:
            self.z_ref_length = length
        onLengthSet(wizard, step)

    def measure_on_plane(self, line):
        x1, y1, x2, y2 = line
        x_vp_list = [point[0] for point in self.vpoints]
        indexes = sorted(range(len(x_vp_list)), key=lambda k: x_vp_list[k])

        y_vp = self.vpoints[indexes[0]]
        z_vp = self.vpoints[indexes[1]]
        x_vp = self.vpoints[indexes[2]]

        vx = np.array([x_vp[0], x_vp[1], 1])
        vy = np.array([y_vp[0], y_vp[1], 1])
        vz = np.array([z_vp[0], z_vp[1], 1])

        print("measuring...")

    def measure_height(self, line):
        x1, y1, x2, y2 = line
        x_vp_list = [point[0] for point in self.vpoints]
        indexes = sorted(range(len(x_vp_list)), key=lambda k: x_vp_list[k])

        y_vp = self.vpoints[indexes[0]]
        z_vp = self.vpoints[indexes[1]]
        x_vp = self.vpoints[indexes[2]]

        vx = np.array([x_vp[0], x_vp[1], 1])
        vy = np.array([y_vp[0], y_vp[1], 1])
        vz = np.array([z_vp[0], z_vp[1], 1])

        v_line = norm_cross(vx, vy)

        br = np.array([self.z_ref_line[0], self.z_ref_line[1], 1])
        tr = np.array([self.z_ref_line[2], self.z_ref_line[3], 1])
        zr = self.z_ref_length

        b1 = np.array([x1, y1, 1])
        t1 = np.array([x2, y2, 1])

        az = compute_length(v_line, vz, br, tr, zr)
        z1 = compute_length(v_line, vz, b1, t1, az)

        print(z1)