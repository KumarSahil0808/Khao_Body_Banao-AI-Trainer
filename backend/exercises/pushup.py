"""
Push-up Counter — MediaPipe Tasks API compatible.

Landmark indices:
  11 = LEFT_SHOULDER
  13 = LEFT_ELBOW
  15 = LEFT_WRIST
"""

import time
from utils.angle import calculate_angle

LEFT_SHOULDER = 11
LEFT_ELBOW    = 13
LEFT_WRIST    = 15


def pushup_counter(landmarks, counter: int, stage, last_rep_time: float):
    """
    Count push-up repetitions.

    The elbow angle is used: it opens (>160°) at the top and
    closes (<80°) at the bottom.

    Returns:
        (counter, stage, angle, last_rep_time)
    """

    shoulder = [landmarks[LEFT_SHOULDER].x, landmarks[LEFT_SHOULDER].y]
    elbow    = [landmarks[LEFT_ELBOW].x,    landmarks[LEFT_ELBOW].y]
    wrist    = [landmarks[LEFT_WRIST].x,    landmarks[LEFT_WRIST].y]

    angle = calculate_angle(shoulder, elbow, wrist)

    if angle > 160:
        stage = "UP"

    if angle < 80 and stage == "UP":
        current_time = time.time()
        if current_time - last_rep_time > 0.8:
            stage = "DOWN"
            counter += 1
            last_rep_time = current_time

    return counter, stage, angle, last_rep_time