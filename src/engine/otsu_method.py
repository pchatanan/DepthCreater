import numpy as np
from itertools import combinations


def multi_otsu(grey, n_split=1, upper=256):
    bins = np.bincount(grey.ravel())
    bins = bins[:upper]
    p_list = bins / bins.sum()
    L = np.arange(upper)
    Mt = np.dot(L, p_list.T)

    inter_var = 0
    threshold = 0
    for idx in combinations(range(2, len(p_list) - 1), n_split):
        P, B = np.split(p_list, idx), np.split(L, idx)
        W = [(p.sum() if p.sum() != 0 else np.nextafter(0, 1)) for p in P]
        M = [np.dot(B[i], P[i].T) / W[i] for i in range(n_split + 1)]
        candidate = np.dot((np.array(M) - Mt) ** 2, np.array(W).T)
        if candidate > inter_var:
            inter_var = candidate
            threshold = idx
    return list(threshold)


def apply_threshold(grey, threshold):
    n_split = len(threshold)
    threshold.insert(0, 0)
    threshold.append(255)
    for i in range(n_split + 1):
        if i == 0:
            value = 0
        elif i == n_split:
            value = 255
        else:
            value = round(i * 255 / n_split)
        grey[(threshold[i] < grey) & (grey < threshold[i + 1])] = value
    return grey
