"""
Angle calculation utility (Tasks-API compatible).
Accepts plain [x, y] lists and returns the joint angle at point b.
"""

import numpy as np

def calculate_angle(a, b, c) -> float:
    """
    Calculate the angle (degrees) at joint b, given three 2-D points a, b, c.

    Args:
        a, b, c: Each is a list/tuple [x, y].

    Returns:
        Angle in degrees [0, 180].
    """
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    radians = (
        np.arctan2(c[1] - b[1], c[0] - b[0])
        - np.arctan2(a[1] - b[1], a[0] - b[0])
    )
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return float(angle)