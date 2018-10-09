import cv2
import numpy as np
import os


class FixPerspective:

    def __init__(self, img_path, img_out, pts_src, width, height):
        self.img_path = img_path
        self.img_out = img_out
        self.pts_src = pts_src
        self.width = width
        self.height = height

    def show(self):
        # Read source image.
        im_src = cv2.imread(self.img_path)
        # Four corners of the book in source image
        pts_src = np.array(self.pts_src)
        # Read destination image.
        k = self.img_path.rfind(".")
        dst_path = self.img_path[:k] + "(fixed)." + self.img_path[k + 1:]
        # Four corners of the book in destination image.
        pts_dst = np.array([[0, 0], [self.width - 1, 0], [self.width - 1, self.height - 1], [0, self.height - 1]])
        # Calculate Homography
        h, status = cv2.findHomography(pts_src, pts_dst)

        # Warp source image to destination based on homography
        im_out = cv2.warpPerspective(im_src, h, (self.width, self.height))

        # Display images
        # cv2.imshow("Warped Source Image", im_out)

        if not os.path.exists(os.path.dirname(self.img_out)):
            os.makedirs(os.path.dirname(self.img_out))

        cv2.imwrite(self.img_out, im_out)
