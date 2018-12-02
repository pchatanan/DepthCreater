from enum import Enum

import cv2
import numpy as np

from engine.opencv_utils import norm_cross, compute_length, compute_homography, get_boundary, wrap_perspective

KEYS = ["x", "y", "z"]


class Wizard(Enum):
    ADD_LINE = 1
    MEASURE_ON_PLANE = 2
    SET_REF_LENGTH = 3
    MEASURE_HEIGHT = 4
    ADD_POINT = 5


class VanishingPointEng:

    def __init__(self, file):
        self.file = file
        self.id = 0
        self.coordinates = []
        self.current_wizard = Wizard.ADD_LINE
        self.calibration = {
            "x": {
                "vp": None,
                "lines": [],
                "ref_line": (),
                "ref_length": ()
            },
            "y": {
                "vp": None,
                "lines": [],
                "ref_line": (),
                "ref_length": ()
            },
            "z": {
                "vp": None,
                "lines": [],
                "ref_line": (),
                "ref_length": ()
            }
        }
        self.img = cv2.imread(file.abspath, 0)
        height, width = self.img.shape
        self.height = height
        self.width = width

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

            key = self.get_key_from_id()
            self.calibration.get(key).get("lines").append([m, c])
            on_line_added(self.current_wizard)
        elif self.current_wizard == Wizard.MEASURE_ON_PLANE:
            legnth = self.measure_on_plane(line)
            on_line_added(self.current_wizard, legnth)
        elif self.current_wizard == Wizard.SET_REF_LENGTH:

            p1 = np.array([x1, y1])
            p2 = np.array([x2, y2])

            min_d = None
            best_key = None
            best_index = None
            for i in range(3):
                key = KEYS[i]
                if self.calibration[key]["vp"] is None:
                    print("Please define vp in the {} direction.".format(key))
                else:
                    vp = np.array(self.calibration[key]["vp"])
                    p3 = vp
                    d = np.linalg.norm(np.cross(p2 - p1, p3 - p1)) / np.linalg.norm(p2 - p1)
                    if best_key is None or d < min_d:
                        min_d = d
                        best_key = key
                        best_index = i

            if best_key is not None and min_d < 70:
                print("{}-axis detected".format(best_key))
                self.calibration[best_key]["ref_line"] = line
                self.set_line_group(best_index)
                data = (line, key)
                on_line_added(self.current_wizard, data)
            elif min_d >= 50:
                print("Please define vp in the drawn direction")
            else:
                print("Please define vp.")
        elif self.current_wizard == Wizard.MEASURE_HEIGHT:
            length = self.measure_height(line)
            on_line_added(self.current_wizard, length)

    def set_line_group(self, id):
        self.id = id

    def get_line_group(self):
        return self.id

    def calculate_vanishing_point(self):
        key = self.get_key_from_id()
        line_list = self.calibration.get(key).get("lines")
        if len(line_list) < 2:
            print('please draw more lines')
            return

        line_list = np.array(line_list)

        ones = np.ones((line_list.shape[0], 1))

        neg_m = (-1) * (line_list[:, 0][:, None])
        b = line_list[:, 1][:, None]

        a = np.concatenate((ones, neg_m), axis=1)
        y, x = np.linalg.lstsq(a, b, rcond=None)[0].flatten()

        # convert to graphics coordinates
        y = self.height - y
        self.calibration[key]["vp"] = (x, y)
        print("vPoint: " + str(x) + ", " + str(y))
        return x, y

    def add_coordinate(self, index, coordinate):
        self.coordinates[index] = coordinate

    def get_coordinates(self):
        return self.coordinates

    def add_vpoint(self, index, vpoint):
        key = self.get_key_from_id(index)
        self.calibration[key]["vp"] = vpoint

    def set_current_wizard(self, wizard):
        self.current_wizard = wizard

    def set_length(self, length, wizard, onLengthSet):
        if wizard == Wizard.SET_REF_LENGTH:
            key = self.get_key_from_id()
            self.calibration[key]["ref_length"] = length
        onLengthSet(wizard)

    def wrap_perspective(self):
        full_image = True
        scale_factor = 1

        x_vp = self.calibration["x"]["vp"]
        y_vp = self.calibration["y"]["vp"]

        x_ref_line = self.calibration["x"]["ref_line"]
        x_ref_length = self.calibration["x"]["ref_length"]
        y_ref_line = self.calibration["y"]["ref_line"]
        y_ref_length = self.calibration["y"]["ref_length"]

        x0, y0 = x_vp
        x1, y1 = y_vp
        m = (y1 - y0) / (x1 - x0)
        c = y1 - m * x1

        vx = np.array([x_vp[0], x_vp[1], 1])
        vy = np.array([y_vp[0], y_vp[1], 1])

        x1 = np.array([x_ref_line[0], x_ref_line[1], 1])
        x2 = np.array([x_ref_line[2], x_ref_line[3], 1])
        xr = x_ref_length * scale_factor

        y1 = np.array([y_ref_line[0], y_ref_line[1], 1])
        y2 = np.array([y_ref_line[2], y_ref_line[3], 1])
        yr = y_ref_length * scale_factor

        H = compute_homography(vx, x1, x2, xr, vy, y1, y2, yr)
        H_inv = np.linalg.inv(H)

        height, width = self.height, self.width

        shift = 0.05 * height
        p1_y = c + shift if c + shift > 0 else 0
        p2_y = m * (width - 1) + c + shift if m * (width - 1) + c + shift > 0 else 0

        if full_image:
            p1 = np.array([0, p1_y, 1])
            p2 = np.array([width - 1, p2_y, 1])
            p3 = np.array([width - 1, height - 1, 1])
            p4 = np.array([0, height - 1, 1])
        else:
            p1 = np.array([26.657, 500.464, 1])
            p2 = np.array([920.766, 258.973, 1])
            p3 = np.array([1418.818, 362.019, 1])
            p4 = np.array([535.924, 949.446, 1])

        boundary = get_boundary(H_inv, (p1, p2, p3, p4))
        dst = wrap_perspective(H, boundary, self.img)
        cv2.imwrite(self.file.get_save_path("wrap"), dst)

    def measure_on_plane(self, line):

        x_vp = self.calibration["x"]["vp"]
        y_vp = self.calibration["y"]["vp"]

        x_ref_line = self.calibration["x"]["ref_line"]
        x_ref_length = self.calibration["x"]["ref_length"]
        y_ref_line = self.calibration["y"]["ref_line"]
        y_ref_length = self.calibration["y"]["ref_length"]

        vx = np.array([x_vp[0], x_vp[1], 1])
        vy = np.array([y_vp[0], y_vp[1], 1])

        x1 = np.array([x_ref_line[0], x_ref_line[1], 1])
        x2 = np.array([x_ref_line[2], x_ref_line[3], 1])
        xr = x_ref_length

        y1 = np.array([y_ref_line[0], y_ref_line[1], 1])
        y2 = np.array([y_ref_line[2], y_ref_line[3], 1])
        yr = y_ref_length

        H = compute_homography(vx, x1, x2, xr, vy, y1, y2, yr)
        H_inv = np.linalg.inv(H)

        # measure
        p5 = np.array([line[0], line[1], 1])
        p6 = np.array([line[2], line[3], 1])
        world_p5 = H_inv.dot(p5)
        world_p5 /= world_p5[-1]
        world_p6 = H_inv.dot(p6)
        world_p6 /= world_p6[-1]
        length = np.linalg.norm(world_p5 - world_p6)
        return length

    def measure_height(self, line):
        x1, y1, x2, y2 = line

        y_vp = self.calibration["y"]["vp"]
        z_vp = self.calibration["z"]["vp"]
        x_vp = self.calibration["x"]["vp"]

        ref_line = self.calibration["z"]["ref_line"]
        ref_length = self.calibration["z"]["ref_length"]

        vx = np.array([x_vp[0], x_vp[1], 1])
        vy = np.array([y_vp[0], y_vp[1], 1])
        vz = np.array([z_vp[0], z_vp[1], 1])

        v_line = norm_cross(vx, vy)

        br = np.array([ref_line[0], ref_line[1], 1])
        tr = np.array([ref_line[2], ref_line[3], 1])
        zr = ref_length

        b1 = np.array([x1, y1, 1])
        t1 = np.array([x2, y2, 1])

        az = compute_length(v_line, vz, br, tr, zr)
        z1 = compute_length(v_line, vz, b1, t1, az)

        return z1

    def get_key_from_id(self, index=None):
        if index is None:
            index = self.id
        return KEYS[index]
