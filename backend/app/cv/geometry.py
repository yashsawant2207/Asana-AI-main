"""Pure geometry helpers extracted from the original Colab notebook."""
import numpy as np


def calculate_angle(a, b, c):
    """3-joint angle (degrees) between points A, B, C."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


def distance(a, b):
    return float(np.linalg.norm(np.array(a) - np.array(b)))
