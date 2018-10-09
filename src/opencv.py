from opencv_engine import *
import cv2
import numpy as np
import collections
import math


n_cluster = 1

red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
purple = (204, 0, 153)
light_blue = (255, 255, 0)
orange = (255, 102, 0)
pink = (255, 102, 255)
black = (0, 0, 0)
clustering_color = [green, light_blue, red, pink]

filename = 'draw'
img = cv2.imread(filename + '.jpg')
height, width, channels = img.shape
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150, apertureSize=3)  # convert to binary image for Hough Transform

# (rho,delta)
rho_accuracy = 1
delta_accuracy = np.pi / 360  # 0.5 degree
# threshold: minimum length of line that should be detected
threshold = 200
minLineLength = 200
maxLineGap = 15

point_lines = cv2.HoughLinesP(edges, rho_accuracy, delta_accuracy, threshold, minLineLength, maxLineGap)
print("Number of lines extracted (including horizontal and vertical): " + str(len(point_lines)))

# initialise cluster
# This step removes horizontal and vertical lines
equation_lines = []
edge_points = []
for i in range(len(point_lines)):
    x11, y11, x12, y12 = point_lines[i][0]
    # if it is a vertical line
    if x11 == x12:
        m1 = np.inf
        c1 = np.nan
    # if it is a horizontal line
    elif y11 == y12:
        m1 = 0
        c1 = y11
    else:
        m1 = (y11 - y12) / (x11 - x12)
        c1 = y11 - m1 * x11
        edges = compute_edge(m1, c1, width, height)
        edge_points.append(edges)
        # if m1 > 0:
        #     cv2.line(img, (int(round(xe1)), int(round(ye1))), (int(round(xe2)), int(round(ye2))), black, 3)
        # else:
        #     cv2.line(img, (int(round(xe1)), int(round(ye1))), (int(round(xe2)), int(round(ye2))), red, 3)
        equation_lines.append([m1, c1])

n = len(equation_lines)
initial_n = n
print("Number of lines extracted (excludingh horizontal and vertical): " + str(n))

# Merge Alignment
reduce_until = 0.4
final_n = int(reduce_until*initial_n)
while len(equation_lines) > final_n:
    dist_matrix = [[sum([(i - j)*(i - j) for i, j in zip(line1, line2)]) for line1 in edge_points] for line2 in edge_points]
    dist_matrix = np.array(dist_matrix)
    max_x, max_y = np.unravel_index(dist_matrix.argmax(), dist_matrix.shape)
    np.fill_diagonal(dist_matrix, dist_matrix[max_x, max_y])
    min_x, min_y = np.unravel_index(dist_matrix.argmin(), dist_matrix.shape)

    if min_x < min_y:
        line_edge2 = edge_points.pop(min_y)
        line_edge1 = edge_points.pop(min_x)
        m2, c2 = equation_lines.pop(min_y)
        m1, c1 = equation_lines.pop(min_x)
    else:
        line_edge1 = edge_points.pop(min_x)
        line_edge2 = edge_points.pop(min_y)
        m1, c1 = equation_lines.pop(min_x)
        m2, c2 = equation_lines.pop(min_y)

    if m1+m2 == 0:
        pass
    else:
        if m1 == m2:
            m3 = m1
            c3 = (c1+c2)/2
        else:
            m3 = ((math.sqrt((1+(m1*m1))*(1+(m2*m2)))+(m1*m2)-1)/(m1+m2))
            x_intercept = (c2-c1)/(m1-m2)
            y_intercept = (m1*x_intercept) + c1
            c3 = y_intercept - (m3*x_intercept)
        equation_lines.append([m3, c3])
        edges = compute_edge(m3, c3, width, height)
        edge_points.append(edges)

n = len(equation_lines)
print(n)
#
#
# xe1, ye1, xe2, ye2 = edge_points[min_x]
# cv2.line(img, (int(round(xe1)), int(round(ye1))), (int(round(xe2)), int(round(ye2))), black, 3)
# xe1, ye1, xe2, ye2 = edge_points[min_y]
# cv2.line(img, (int(round(xe1)), int(round(ye1))), (int(round(xe2)), int(round(ye2))), red, 3)
# xe1, ye1, xe2, ye2 = edge_points[-1]
# cv2.line(img, (int(round(xe1)), int(round(ye1))), (int(round(xe2)), int(round(ye2))), green, 4)


# define initial cluster
clustering = np.random.choice(n_cluster, n, replace=True)

for h in range(200):
    for i in range(n):
        residuals = [0] * n_cluster
        for j in range(n_cluster):
            clusters = [[] for _ in range(n_cluster)]
            for k in range(n):
                if i == k:
                    clusters[j].append(equation_lines[k])
                else:
                    clusters[clustering[k]].append(equation_lines[k])
            residuals[j] = compute_error(clusters)

        if h == 0 and i == 0:
            smallest_total_residuals = max(residuals)
            print("smallest_total_residuals: " + str(smallest_total_residuals))

        #print(residuals)

        for r in range(len(residuals)):
            counter = collections.Counter(clustering)
            if (counter.get(clustering[i]) > 10) and residuals[r] < smallest_total_residuals:
                clustering[i] = residuals.index(residuals[r])
                smallest_total_residuals = residuals[r]
                print("smallest_total_residuals: " + str(smallest_total_residuals))

                for m in range(len(clusters)):
                    x, y, residual = calculate_vanishing_point(clusters[m])
                    print("cluster " + str(m + 1) + ": " + str(len(clusters[m])))
                    print("  residuals: " + str((residual[0] / (len(clusters[m])))))

clusters = [[] for _ in range(n_cluster)]
for i in range(n):
    clusters[clustering[i]].append(equation_lines[i])

for i in range(n_cluster):
    cluster = clusters[i]
    for m, c in cluster:
        cv2.line(img, (0, int(round(c))), (width, int(round(width * m + c))), clustering_color[i], 1)

    # plot all intersection points
    for j in range(len(cluster)):
        for k in range(j + 1, len(cluster)):
            m1, c1 = cluster[j]
            m2, c2 = cluster[k]
            if m1 != m2:
                x_intersect = (c2 - c1) / (m1 - m2)
                y_intersect = m1 * x_intersect + c1
                x_intersect = int(round(x_intersect))
                y_intersect = int(round(y_intersect))
                cv2.circle(img, (x_intersect, y_intersect), 10, clustering_color[i], -1)

    x, y, residuals = calculate_vanishing_point(cluster)
    #print(x, y, residuals)
    cv2.circle(img, (x, y), 20, clustering_color[i], -1)

cv2.imwrite(filename + '(computed).jpg', img)