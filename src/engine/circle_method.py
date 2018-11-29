import time
import cv2

from opencv_engine import *
from engine.mathsengine import *
from engine.otsu_method import *
from util.draw_util import draw_line

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)

color_list = [GREEN, BLUE, RED]


def auto_detect_vp(input_file):
    np.random.seed(0)

    # Step1: Extract line segments
    img = cv2.imread(input_file.abspath)
    height, width, channels = img.shape
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    start_time = time.time()

    # Canny edge detection: convert to binary image for Hough Transform
    # Otsu´s Method to determine threshold
    high_thresh = multi_otsu(grey)[0]
    low_thresh = multi_otsu(grey, upper=high_thresh)[0]
    edges = cv2.Canny(grey, low_thresh, high_thresh)

    # (rho,delta)
    rho = 1  # accuracy in pixel
    theta = np.pi / 180  # accuracy 1 degree
    threshold = 50  # number of votes to be considered as lines
    min_line_length = 10
    max_line_gap = 0

    lines = cv2.HoughLinesP(edges,
                            rho=rho,
                            theta=theta,
                            threshold=threshold,
                            minLineLength=min_line_length,
                            maxLineGap=max_line_gap)
    lines = np.array([l[0] for l in lines])

    all_lines_extracted = cv2.cvtColor(edges.copy(), cv2.COLOR_GRAY2RGB)
    draw_line(all_lines_extracted, lines, (0, 255, 255), thick=5)

    # remove horizontal and vertical lines
    lines = lines[(lines[:, 1] != lines[:, 3]) & (lines[:, 0] != lines[:, 2]), :]
    slops = (lines[:, 1] - lines[:, 3]) / (lines[:, 0] - lines[:, 2])
    y_intersects = lines[:, 1] - (slops * lines[:, 0])
    mc_list = np.column_stack((slops, y_intersects))

    total_lines = lines.shape[0]
    print("Number of extracted lines: " + str(total_lines))

    # Step2: Find points on circles
    # define reference point
    ref_x, ref_y = width // 2, height // 2

    ref_m = -1 / mc_list[:, 0]
    ref_c = ref_y - (ref_m * ref_x)
    ref_mc_list = np.column_stack((ref_m, ref_c))

    intersection_points = intersection_matrix(mc_list, ref_mc_list)
    int_intersection_points = np.round(intersection_points).astype(int)

    max_coor = int_intersection_points.max(axis=0)  # [max_x, max_y]
    min_coor = int_intersection_points.min(axis=0)  # [min_x, min_y]

    width_extended = max([width, max_coor[0]]) - min([0, min_coor[0]])
    height_extended = max([height, max_coor[1]]) - min([0, min_coor[1]])
    x_shift = width_extended - width
    y_shift = height_extended - height

    white_image = create_blank(width_extended, height_extended, (255, 255, 255))
    grey_temp = cv2.cvtColor(grey.copy(), cv2.COLOR_GRAY2RGB)
    white_image[y_shift:y_shift + grey_temp.shape[0], x_shift:x_shift + grey_temp.shape[1]] = grey_temp
    points_clustered = white_image.copy()

    for x, y in int_intersection_points:
        x += x_shift
        y += y_shift
        cv2.circle(white_image, (x, y), 4, (0, 255, 0), -1)

    cv2.circle(white_image, (x_shift+ref_x, y_shift+ref_y), 6, (0, 0, 255), -1)
    cv2.imwrite(input_file.get_save_path("points"), white_image)

    # Step3: Extract different circles
    print((width**2+height**2)**0.5)
    diagonal = (width**2+height**2)**0.5
    threshold = round(0.005*diagonal)
    iteration = 1000

    circles_extracted = []

    best_center, best_radius = None, None
    best_count = 0
    index_in_band = None
    line_extracted = cv2.cvtColor(grey.copy(), cv2.COLOR_GRAY2RGB)
    line_left = total_lines
    while line_left/total_lines > 0.25 and len(circles_extracted) < 3:
        n = len(circles_extracted)
        n_points = intersection_points.shape[0]
        print("No. of points: " + str(n_points))
        for i in range(iteration):
            # sample 2 points
            idx = np.random.randint(n_points, size=2)
            selected_points = intersection_points[idx, :]
            center, radius = define_circle(selected_points[0, :], selected_points[1, :], (ref_x, ref_y))
            if center is not None:
                count, indexes = count_points_in_band(center, radius, threshold, intersection_points)
                if count > best_count:
                    best_count = count
                    best_center, best_radius = center, radius
                    index_in_band = indexes
        circles_extracted.append((best_center, best_radius))

        cv2.circle(points_clustered, (int(round(best_center[0] + x_shift)), int(round(best_center[1]+ y_shift))) , int(round(best_radius)), (255, 0, 255),
                   3)
        cv2.circle(points_clustered, (int(round(best_center[0] + x_shift)), int(round(best_center[1]+ y_shift))) , int(round(best_radius + threshold)),
                   (100, 0, 255), 1)
        cv2.circle(points_clustered, (int(round(best_center[0] + x_shift)) , int(round(best_center[1]+ y_shift))) , int(round(best_radius - threshold)),
                   (100, 0, 255), 1)

        # draw lines
        draw_line(line_extracted, lines[index_in_band, :], color_list[n], thick=5)

        for x, y in int_intersection_points[index_in_band, :]:
            x += x_shift
            y += y_shift
            cv2.circle(points_clustered, (x, y), 4, color_list[n], -1)

        # remove points extracted
        intersection_points = np.delete(intersection_points, index_in_band, axis=0)
        lines = np.delete(lines, index_in_band, axis=0)
        int_intersection_points = np.delete(int_intersection_points, index_in_band, axis=0)
        line_left = lines.shape[0]

        print("best_count: " + str(best_count))
        best_center, best_radius = None, None
        best_count = 0
        index_in_band = None

    v_points = []

    for center, radius in circles_extracted:
        ref_to_center = (center[0] - ref_x, center[1] - ref_y)
        v_point = [ref_x + 2 * ref_to_center[0], ref_y + 2 * ref_to_center[1]]
        v_points.append([v_point[0] - x_shift, v_point[1] - y_shift])
        cv2.circle(points_clustered, (int(round(v_point[0])), int(round(v_point[1]))), 5, (255, 120, 100), -1)

        print("center: " + str(center))
        print("radius: " + str(radius))

    end_time = time.time()
    print("Timing: {}".format(end_time - start_time))

    cv2.imwrite(input_file.get_save_path("grey"), grey)
    cv2.imwrite(input_file.get_save_path("edge"), edges)
    cv2.imwrite(input_file.get_save_path("extracted"), all_lines_extracted)
    cv2.imwrite(input_file.get_save_path("clustered"), line_extracted)
    cv2.imwrite(input_file.get_save_path("circle"), points_clustered)

    # init empty list
    ordered_v_points = []

    # this while loop rearranges v points --> [vy, vz, vx]
    while len(v_points) > 0:
        x_list = [e[0] for e in v_points]
        min_x = min(x_list)
        min_index = x_list.index(min_x)
        ordered_v_points.append(v_points.pop(min_index))

    # rotate vx to the first index
    ordered_v_points.insert(0, ordered_v_points.pop())

    return ordered_v_points
