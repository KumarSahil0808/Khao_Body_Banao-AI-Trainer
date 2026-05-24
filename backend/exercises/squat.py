"""
Squat Counter — MediaPipe Tasks API compatible.

Landmark indices:
  23 = LEFT_HIP
  25 = LEFT_KNEE
  27 = LEFT_ANKLE
"""

import time
from utils.angle import calculate_angle

LEFT_HIP   = 23
LEFT_KNEE  = 25
LEFT_ANKLE = 27


def squat_counter(landmarks, counter: int, stage, last_rep_time: float):
    """
    Count squat repetitions.

    Knee angle:
      > 160° → standing (UP)
      < 90°  → squatted (DOWN)

    Returns:
        (counter, stage, angle, last_rep_time)
    """

    hip   = [landmarks[LEFT_HIP].x,   landmarks[LEFT_HIP].y]
    knee  = [landmarks[LEFT_KNEE].x,  landmarks[LEFT_KNEE].y]
    ankle = [landmarks[LEFT_ANKLE].x, landmarks[LEFT_ANKLE].y]

    angle = calculate_angle(hip, knee, ankle)

    if angle > 160:
        stage = "UP"

    if angle < 90 and stage == "UP":
        current_time = time.time()
        if current_time - last_rep_time > 0.8:
            stage = "DOWN"
            counter += 1
            last_rep_time = current_time

    return counter, stage, angle, last_rep_time