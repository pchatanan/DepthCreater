import numpy as np
import cv2

COLOR_DICT = {
    "red": (0, 0, 255),
    "blue": (255, 0, 0),
    "green": (0, 255, 0)
}


def norm_cross(a, b):
    cross = np.cross(a, b)
    cross /= np.linalg.norm(cross)
    return cross


def compute_length(l, v, b, t, alpha_or_ref):
    norminator = -np.linalg.norm(np.cross(b, t))
    denorminator = alpha_or_ref * np.dot(l, b) * np.linalg.norm(np.cross(v, t))
    return norminator / denorminator


def compute_scaling_factor(h_inv, p1, p2, ref_dis):
    p1_w = h_inv.dot(p1)
    p1_w /= p1_w[-1]
    p2_w = h_inv.dot(p2)
    p2_w /= p2_w[-1]
    scaling_factor = np.linalg.norm(p1_w - p2_w) / ref_dis
    return scaling_factor


def compute_homography(v1, s_p1, e_p1, ref_p1, v2, s_p2, e_p2, ref_p2):
    v_line = norm_cross(v1, v2)

    h = np.vstack((v1, v2, v_line)).T
    h_inv = np.linalg.inv(h)

    # calibrate x and y
    a1 = compute_scaling_factor(h_inv, s_p1, e_p1, ref_p1)
    a2 = compute_scaling_factor(h_inv, s_p2, e_p2, ref_p2)

    return np.vstack((a1 * v1, a2 * v2, v_line)).T


def get_boundary(h_inv, corners):

    temp = []

    for p in corners:
        temp_p = h_inv.dot(p)
        temp_p /= temp_p[-1]
        temp.append(temp_p.astype(int))

    mat = np.vstack(tuple(temp))
    max = mat.max(axis=0)
    min = mat.min(axis=0)

    return min[1], max[1], min[0], max[0]


def wrap_perspective(h, boundary, src_img):
    min_y, max_y, min_x, max_x = boundary
    idy, idx = np.mgrid[min_y:max_y, min_x:max_x]
    lin_homo_ind = np.array([idx.ravel(), idy.ravel(), np.ones_like(idx).ravel()])
    map_ind = h.dot(lin_homo_ind)
    map_x, map_y = map_ind[:-1] / map_ind[-1]  # ensure homogeneity
    map_x = map_x.reshape(max_y - min_y, max_x - min_x).astype(np.float32)
    map_y = map_y.reshape(max_y - min_y, max_x - min_x).astype(np.float32)
    dst_img = cv2.remap(src_img, np.flip(map_x, axis=1), np.flip(map_y, axis=1), cv2.INTER_LINEAR)
    return dst_img


def draw_point(img, center, color, text):
    radius = 8
    circle_margin = 6

    cv2.circle(img, center, radius, (0, 0, 0), -1)
    cv2.circle(img, center, radius - 3, color, -1)

    middle_left = (center[0] + radius + circle_margin, center[1])
    draw_text(img, text, middle_left, color)


def draw_text(img, text, middle_left, color):
    fontFace = cv2.FONT_HERSHEY_DUPLEX
    fontScale = 1.5
    thickness = 2

    box_padding = 6

    retval, baseLine = cv2.getTextSize(text, fontFace, fontScale, thickness=thickness)
    txt_w, txt_h = retval
    rec_tl = (middle_left[0], middle_left[1] - txt_h // 2 - box_padding)
    rec_br = (rec_tl[0] + txt_w + 2 * box_padding,
              rec_tl[1] + txt_h + 2 * box_padding)
    cv2.rectangle(img, rec_tl, rec_br, color, -1)

    text_anchor = (rec_tl[0] + box_padding, rec_tl[1] + box_padding + txt_h)
    cv2.putText(img, text, text_anchor, fontFace, fontScale, (255, 255, 255), thickness=thickness)


def to_tuple(point):
    return int(round(point[0])), int(round(point[1]))


def draw_line(img, pt1, txt1, pt2, txt2, color, label):
    cv2.line(img, pt1, pt2, color, 3)
    draw_point(img, pt1, color, txt1)
    draw_point(img, pt2, color, txt2)

    if label is not None:
        label_anchor = (((pt1[0] + pt2[0]) // 2) + 10, (pt1[1] + pt2[1]) // 2)
        draw_text(img, label, label_anchor, color)
