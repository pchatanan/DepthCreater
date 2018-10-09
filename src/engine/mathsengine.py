import math
import numpy as np


def reflect_y(point):
    return [point[0], -point[1]]


def line(p1, p2):
    a = (p1[1] - p2[1])
    b = (p2[0] - p1[0])
    c = (p1[0] * p2[1] - p2[0] * p1[1])
    return a, b, -c


def intersection(l1, l2):
    D = l1[0] * l2[1] - l1[1] * l2[0]
    Dx = l1[2] * l2[1] - l1[1] * l2[2]
    Dy = l1[0] * l2[2] - l1[2] * l2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return [x, y]
    else:
        return False


def intersection_mc(l1, l2):
    x = (l2[1] - l1[1]) / (l1[0] - l2[0])
    y = (l1[0] * x) + l1[1]
    return [x, y]


def intersection_matrix(l1, l2):
    x = (l2[:, 1] - l1[:, 1]) / (l1[:, 0] - l2[:, 0])
    y = (l1[:, 0] * x) + l1[:, 1]
    return np.column_stack((x, y))


def calculate_compass_bearing(pointA, pointB):
    normalised_point = np.array(pointB) - np.array(pointA)
    x = normalised_point[0]
    y = normalised_point[1]

    if x == 0:
        if y > 0:
            return 0
        if y < 0:
            return 180
    if y == 0:
        if x > 0:
            return 90
        if x < 0:
            return 270

    angle = math.atan(normalised_point[0] / normalised_point[1])
    degree = angle * 180 / math.pi

    if x > 0 and y > 0:
        return degree
    if x > 0 and y < 0:
        return degree + 180
    if x < 0 and y < 0:
        return degree + 180
    if x < 0 and y > 0:
        return degree + 360

    return angle * 180 / math.pi


def rearrange_point(all_points):
    x_list = [item[0] for item in all_points]
    first_index = x_list.index(min(x_list))
    first_point = all_points.pop(first_index)
    ordered_points = [first_point]

    bearings = []
    for point in all_points:
        bearings.append(calculate_compass_bearing(reflect_y(first_point), reflect_y(point)))

    while len(all_points) != 0:
        min_index = bearings.index(min(bearings))
        ordered_points.append(all_points.pop(min_index))
        bearings.pop(min_index)

    return ordered_points


def define_circle(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    D = np.linalg.det(np.array([
        [x1, y1, 1],
        [x2, y2, 1],
        [x3, y3, 1]
    ]))

    if abs(D) < 1.0e-6:
        return None, None

    Da = np.linalg.det(np.array([
        [-(x1 ** 2 + y1 ** 2), y1, 1],
        [-(x2 ** 2 + y2 ** 2), y2, 1],
        [-(x3 ** 2 + y3 ** 2), y3, 1]
    ]))

    Db = np.linalg.det(np.array([
        [x1, -(x1 ** 2 + y1 ** 2), 1],
        [x2, -(x2 ** 2 + y2 ** 2), 1],
        [x3, -(x3 ** 2 + y3 ** 2), 1]
    ]))

    Dc = np.linalg.det(np.array([
        [x1, y1, -(x1 ** 2 + y1 ** 2)],
        [x2, y2, -(x2 ** 2 + y2 ** 2)],
        [x3, y3, -(x3 ** 2 + y3 ** 2)]
    ]))

    xc = -Da / (2 * D)
    yc = -Db / (2 * D)
    r = (xc ** 2 + yc ** 2 - (Dc / D)) ** 0.5

    return (xc, yc), r


def count_points_in_band(center, radius, threshold, circle_points):
    cx, cy = center
    count = 0
    index = []
    for i in range(circle_points.shape[0]):
        point = circle_points[i, :]
        x = point[0]
        y = point[1]
        dist_from_center = ((x-cx)**2 + (y-cy)**2)**0.5
        if (radius + threshold) > dist_from_center > (radius - threshold):
            count += 1
            index.append(i)
    return count, index

