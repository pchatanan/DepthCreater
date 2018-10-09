import cv2


def draw_line(img, end_points, color=(0, 0, 255), thick=2):
    for x1, y1, x2, y2 in end_points:
        cv2.line(img, (x1, y1), (x2, y2), color, thick)
