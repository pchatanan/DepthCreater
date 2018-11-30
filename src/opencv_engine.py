import numpy as np


def calculate_vanishing_point(line_list):
    if len(line_list) < 2:
        print('please draw more lines')
        return
    line_list = np.array(line_list)

    ones = np.ones((line_list.shape[0], 1))

    neg_m = (-1) * (line_list[:, 0][:, None])
    b = line_list[:, 1][:, None]
    a = np.concatenate((ones, neg_m), axis=1)

    solution = np.linalg.lstsq(a, b, rcond=None)
    y, x = solution[0]
    residual = solution[1]

    # convert to graphics coordinates
    # y = height - y

    return x, y, residual


def compute_error(clusters):
    sum = 0
    for i in range(len(clusters)):
        x, y, residuals = calculate_vanishing_point(clusters[i])
        if i == (len(clusters) - 1):
            sum += (10 * len(clusters[i]))
        else:
            sum += (residuals[0] / (len(clusters[i])))
    return sum


def compute_edge(m1, c1, width, height):
    right_edge = m1 * width + c1
    if (c1 > 0) and (c1 <= height):
        ye1 = c1
        xe1 = 0
        if right_edge <= 0:
            ye2 = 0
            xe2 = -c1 / m1
        elif (right_edge > 0) and (right_edge <= height):
            xe2 = width
            ye2 = (m1 * width) + c1
        else:
            ye2 = height
            xe2 = (height - c1) / m1
    elif c1 <= 0:
        ye1 = 0
        xe1 = -c1 / m1
        if (right_edge > 0) and (right_edge <= height):
            xe2 = width
            ye2 = (m1 * width) + c1
        else:
            ye2 = height
            xe2 = (height - c1) / m1
    else:
        xe1 = width
        ye1 = (m1 * width) + c1
        ye2 = height
        xe2 = (height - c1) / m1

    return [xe1, ye1, xe2, ye2]


def create_blank(width, height, rgb_color=(0, 0, 0)):
    """Create new image(numpy array) filled with certain color in RGB"""
    # Create black blank image
    image = np.zeros((height, width, 3), np.uint8)

    # Since OpenCV uses BGR, convert the color first
    color = tuple(reversed(rgb_color))
    # Fill image with color
    image[:] = color

    return image


def sort_point_list(points):
    x_vp_list = [point[0] for point in points]
    indexes = sorted(range(len(x_vp_list)), key=lambda k: x_vp_list[k])
    temp = [points[index] for index in indexes]
    return temp
