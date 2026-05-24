"""
Bicep Curl Counter — MediaPipe Tasks API compatible.

Landmark indices (PoseLandmark enum values):
  11 = LEFT_SHOULDER
  13 = LEFT_ELBOW
  15 = LEFT_WRIST
  12 = RIGHT_SHOULDER
  14 = RIGHT_ELBOW
  16 = RIGHT_WRIST
"""

import time
from utils.angle import calculate_angle

# Landmark index constants - Swapped to account for cv2.flip mirrored feed.
# Physical LEFT arm corresponds to MediaPipe RIGHT landmarks in a mirrored view.
LEFT_SHOULDER = 12
LEFT_ELBOW    = 14
LEFT_WRIST    = 16

# Physical RIGHT arm corresponds to MediaPipe LEFT landmarks in a mirrored view.
RIGHT_SHOULDER = 11
RIGHT_ELBOW    = 13
RIGHT_WRIST    = 15


def curl_counter_arm(landmarks, shoulder_idx, elbow_idx, wrist_idx, counter: int, stage, last_rep_time: float, prev_angle: float):
    """
    Helper to calculate curl reps for a single arm.
    Uses robust smoothing (EMA) and relaxed angle ranges for real-time webcam tracking.
    """
    shoulder = [landmarks[shoulder_idx].x, landmarks[shoulder_idx].y]
    elbow    = [landmarks[elbow_idx].x,    landmarks[elbow_idx].y]
    wrist    = [landmarks[wrist_idx].x,    landmarks[wrist_idx].y]

    raw_angle = calculate_angle(shoulder, elbow, wrist)
    
    # ── Smooth noisy angle fluctuations (Exponential Moving Average) ──
    alpha = 0.5  # EMA smoothing factor
    if prev_angle is None or prev_angle == 0.0:
        angle = raw_angle
    else:
        angle = alpha * raw_angle + (1 - alpha) * prev_angle

    current_time = time.time()

    # ── Relaxed curl detection logic ──
    # Extended arm angle > 140°
    # Contracted curl angle < 55°
    if angle > 140:
        if stage == "UP":
            # Debounce check to prevent duplicates
            if current_time - last_rep_time > 0.8:
                counter += 1
                last_rep_time = current_time
        stage = "DOWN"
    elif angle < 55:
        if stage == "DOWN":
            stage = "UP"

    return counter, stage, angle, last_rep_time


def curl_counter(landmarks, left_counter: int, left_stage, last_left_rep_time: float, left_prev_angle: float,
                 right_counter: int, right_stage, last_right_rep_time: float, right_prev_angle: float):
    """
    Count bicep curl repetitions for both arms independently.
    """
    left_counter, left_stage, left_angle, last_left_rep_time = curl_counter_arm(
        landmarks, LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST, left_counter, left_stage, last_left_rep_time, left_prev_angle
    )

    right_counter, right_stage, right_angle, last_right_rep_time = curl_counter_arm(
        landmarks, RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST, right_counter, right_stage, last_right_rep_time, right_prev_angle
    )

    return (
        left_counter, left_stage, left_angle, last_left_rep_time,
        right_counter, right_stage, right_angle, last_right_rep_time
    )