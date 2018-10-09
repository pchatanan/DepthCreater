import numpy as np


class SingleViewEngine:

    def __init__(self):
        self.v_points = {
            "vx": None,
            "vy": None,
            "vz": None
        }
        self.alpha = {
            "ax": None,
            "ay": None,
            "az": None
        }
        self.unit_l = {
            "lx": None,
            "ly": None,
            "lz": None
        }

    def set_v_points(self, v_points):
        self.v_points.update(v_points)

    def set_ref_length(self, axis, br, tr, zr):

        if axis == "z":
            v0 = self.v_points.get("vx")
            v1 = self.v_points.get("vy")
            v2 = self.v_points.get("vz")
            alpha_key = "az"
            l_key = "lz"
        elif axis == "y":
            v0 = self.v_points.get("vz")
            v1 = self.v_points.get("vx")
            v2 = self.v_points.get("vy")
            alpha_key = "ay"
            l_key = "ly"
        elif axis == "x":
            v0 = self.v_points.get("vy")
            v1 = self.v_points.get("vz")
            v2 = self.v_points.get("vx")
            alpha_key = "ax"
            l_key = "lx"

        L = np.cross(v0, v1)
        unit_L = L / np.linalg.norm(L)
        nominator = np.linalg.norm(np.cross(br, tr))
        denominator = zr * np.dot(unit_L, br) * np.linalg.norm(np.cross(v2, tr))
        alpha = -1 * nominator / denominator
        self.alpha[alpha_key] = alpha
        self.unit_l[l_key] = unit_L

    def get_length(self, bx, tx, ref_plane):

        if ref_plane == "xy":
            alpha = self.alpha.get("az")
            unit_L = self.unit_l.get("lz")
            v = self.v_points.get("vz")
        elif ref_plane == "yz":
            alpha = self.alpha.get("ax")
            unit_L = self.unit_l.get("lx")
            v = self.v_points.get("vx")
        elif ref_plane == "xz":
            alpha = self.alpha.get("ay")
            unit_L = self.unit_l.get("ly")
            v = self.v_points.get("vy")

        nominator2 = np.linalg.norm(np.cross(bx, tx))
        denominator2 = alpha * np.dot(unit_L, bx) * np.linalg.norm(np.cross(v, tx))
        Zx = -1 * nominator2 / denominator2

        return Zx


test_eng = SingleViewEngine()


# first find alpha
vx = np.array([953.86799047, 512.63531968, 1])
vy = np.array([-1273.14104253, 482.26310242, 1])
vz = np.array([502.2796561, -4740.22931104, 1])

test_eng.set_v_points({
    "vx": vx,
    "vy": vy,
    "vz": vz
})

br = np.array([701, 589, 1])
tr = np.array([697, 404, 1])
Zr = 91

test_eng.set_ref_length("z", br, tr, Zr)

bx = np.array([165, 576, 1])
tx = np.array([175, 371, 1])

Zx = test_eng.get_length(bx, tx, "xy")
print(Zx)

br = np.array([516, 399, 1])
tr = np.array([312, 408, 1])
test_eng.set_ref_length("y", br, tr, 90)

tx = np.array([308, 593, 1])
Zx = test_eng.get_length(br, tx, "xz")

print(Zx)
