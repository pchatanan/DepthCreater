from engine.otsu_method import multi_otsu
from util.filemanager import FileManager
import cv2
import matplotlib.pyplot as plt
import numpy as np

file = FileManager('../res/img/Garfield_Building.jpg')
img = cv2.imread('../res/img/Garfield_Building.jpg')
height, width, channels = img.shape
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
bins = np.bincount(grey.ravel())
print(bins)

thresholds = multi_otsu(grey, n_split=2)
print(thresholds)
edges1 = cv2.Canny(grey, thresholds[0], thresholds[1])
cv2.imwrite(file.get_save_path("multiOtsu"), edges1)

high_thresh = multi_otsu(grey)[0]
low_thresh = multi_otsu(grey, upper=high_thresh)[0]
print([high_thresh, low_thresh])
edges2 = cv2.Canny(grey, low_thresh, high_thresh)
cv2.imwrite(file.get_save_path("singleOtsu"), edges2)

plt.figure(num=1, figsize=(10, 5))
plt.hist(grey.ravel(), bins=range(256), color="b", label="image histogram")
plt.axvline(x=thresholds[0],
            color="r",
            label="lower threshold ({})".format(thresholds[0]),
            linestyle='--')
plt.axvline(x=thresholds[1],
            color="r",
            label="higher threshold ({})".format(thresholds[1]))
plt.legend()
plt.title("Double Thresholds using Multi Otsu's Method")
plt.xlabel("bins")
plt.ylabel("No. of pixels")
plt.savefig('Multi Otsu\'s Method.png')

plt.figure(num=2, figsize=(10, 5))
plt.hist(grey.ravel(), bins=range(256), color="b", label="image histogram")
plt.axvline(x=high_thresh,
            color="r",
            label="higher threshold ({})".format(high_thresh))
plt.legend()
plt.title("Higher Threshold using Otsu's Method")
plt.xlabel("bins")
plt.ylabel("No. of pixels")
plt.savefig('Single Otsu\'s Method.png')

