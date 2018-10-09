import numpy as np


class VanishingPointEng:

    def __init__(self, height, width):
        self.lines = []
        self.height = height
        self.width = width
        self.id = -1
        self.coordinates = []
        self.vpoints = []

    def add_line(self, id, x1, y1, x2, y2):
        # translate to origin at bottom left
        y1 = self.height - y1
        y2 = self.height - y2

        m = (y1 - y2) / (x1 - x2)
        c = y1 - (m * x1)
        self.lines[id].append([m, c])
        print(self.lines)

    def set_line_group(self, id):
        self.id = id

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

        self.vpoints[self.id] = [x[0], y[0]]

        print("vPoint: " + str(x) + ", " + str(y))

        return x, y

    def add_coordinate(self, index, coordinate):
        print("setting")
        self.coordinates[index] = coordinate

    def get_coordinates(self):
        return self.coordinates
