"""
Posture Detection — MediaPipe Tasks API compatible.

Uses integer landmark indices instead of mp.solutions.pose enums.
"""

from utils.angle import calculate_angle

# Landmark indices
NOSE           = 0
LEFT_EAR       = 7
LEFT_SHOULDER  = 11
RIGHT_SHOULDER = 12
LEFT_HIP       = 23
RIGHT_HIP      = 24
LEFT_KNEE      = 25
RIGHT_KNEE     = 26


def check_posture(landmarks, mode: str) -> tuple:
    """
    Analyse landmark positions for common posture faults.

    Returns:
        (posture_ok: bool, warning_message: str)
    """

    try:
        def pt(idx):
            lm = landmarks[idx]
            return [lm.x, lm.y]

        left_shoulder  = pt(LEFT_SHOULDER)
        right_shoulder = pt(RIGHT_SHOULDER)
        left_hip       = pt(LEFT_HIP)
        right_hip      = pt(RIGHT_HIP)
        nose           = pt(NOSE)
        left_knee      = pt(LEFT_KNEE)
        right_knee     = pt(RIGHT_KNEE)

        # ── 1. Shoulder level symmetry ────────────────────────────
        shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
        if shoulder_diff > 0.07:
            return False, "KEEP SHOULDERS LEVEL"

        # ── 2. Spine / back alignment ─────────────────────────────
        spine_angle = calculate_angle(
            left_shoulder,
            left_hip,
            [left_hip[0], left_hip[1] + 0.1]   # vertical reference downward
        )
        if spine_angle > 20:
            return False, "STRAIGHTEN YOUR BACK"

        # ── 3. Mode-specific checks ───────────────────────────────
        mid_shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
        mid_hip_y      = (left_hip[1]      + right_hip[1])      / 2

        if mode == "squat":
            hip_width  = abs(left_hip[0]  - right_hip[0])
            knee_width = abs(left_knee[0] - right_knee[0])
            if knee_width < hip_width * 0.5:
                return False, "SPREAD KNEES SHOULDER-WIDTH"

        if mode == "pushup":
            hip_sag = mid_hip_y - mid_shoulder_y
            if hip_sag > 0.15:
                return False, "DON'T SAG YOUR HIPS"
            if hip_sag < -0.05:
                return False, "LOWER YOUR HIPS"

        # ── 4. Head-forward posture ───────────────────────────────
        mid_shoulder_x = (left_shoulder[0] + right_shoulder[0]) / 2
        if abs(nose[0] - mid_shoulder_x) > 0.14:
            return False, "KEEP YOUR HEAD NEUTRAL"

        return True, ""

    except Exception:
        return True, ""
