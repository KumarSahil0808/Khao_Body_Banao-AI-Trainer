"""
AI Fitness Trainer — Flask Backend (MediaPipe Tasks API)
=========================================================
Compatible with mediapipe >= 0.10.30.

Endpoints
---------
GET  /video_feed          MJPEG live stream with pose overlay + HUD
GET  /api/status          JSON snapshot of current session
POST /api/set_mode        Switch exercise mode  {"mode": "curl"|"pushup"|"squat"}
POST /api/reset           Reset counter + calories for current mode
GET  /api/session_summary Workout summary
GET  /                    Health check
"""

import os
import sys
import cv2
import time
import threading
import numpy as np

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarkerOptions, PoseLandmarkerResult

from exercises.curl   import curl_counter
from exercises.pushup import pushup_counter
from exercises.squat  import squat_counter
from utils.posture    import check_posture

# ─────────────────────────────────────────────────────────────
# Flask Setup
# ─────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────────────────────
# Model path
# ─────────────────────────────────────────────────────────────

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "pose_landmarker_lite.task")

if not os.path.exists(MODEL_PATH):
    sys.exit(
        f"[ERROR] Pose model not found at: {MODEL_PATH}\n"
        "Download it with:\n"
        "  Invoke-WebRequest -Uri https://storage.googleapis.com/mediapipe-models/"
        "pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task "
        "-OutFile models/pose_landmarker_lite.task"
    )

# ─────────────────────────────────────────────────────────────
# Calorie Multipliers (kcal per rep)
# ─────────────────────────────────────────────────────────────

CALORIE_PER_REP = {
    "curl":   0.35,
    "pushup": 0.50,
    "squat":  0.60,
}

# Landmark index constants (same as PoseLandmark enum values)
CONNECTIONS = [
    (11, 12), (11, 13), (13, 15),           # left arm
    (12, 14), (14, 16),                     # right arm
    (11, 23), (12, 24), (23, 24),           # torso
    (23, 25), (25, 27), (27, 29), (27, 31), # left leg
    (24, 26), (26, 28), (28, 30), (28, 32), # right leg
]

# ─────────────────────────────────────────────────────────────
# Shared Session State
# ─────────────────────────────────────────────────────────────

lock = threading.Lock()

session = {
    "mode":            "curl",
    "counter":         0,
    "stage":           None,
    "angle":           0.0,
    "calories":        0.0,
    "posture_ok":      True,
    "posture_warning": "",
    "form_warning":    "",
    "fps":             0.0,
    "running":         False,
    "pose_detected":   False,
    "left_counter":    0,
    "right_counter":   0,
    "left_stage":      None,
    "right_stage":     None,
    "left_angle":      0.0,
    "right_angle":     0.0,
}

# ─────────────────────────────────────────────────────────────
# Draw helpers
# ─────────────────────────────────────────────────────────────

def _landmark_px(lm, w, h):
    return int(lm.x * w), int(lm.y * h)


def _draw_skeleton(image, landmarks, w, h):
    """Draw skeleton dots and lines on the frame."""
    pts = [_landmark_px(lm, w, h) for lm in landmarks]

    for (a, b) in CONNECTIONS:
        if a < len(pts) and b < len(pts):
            cv2.line(image, pts[a], pts[b], (0, 180, 255), 2, cv2.LINE_AA)

    for pt in pts:
        cv2.circle(image, pt, 4, (0, 255, 120), -1, cv2.LINE_AA)


# ─────────────────────────────────────────────────────────────
# MJPEG Generator
# ─────────────────────────────────────────────────────────────

def generate_frames():
    """Capture webcam → run pose detection → yield MJPEG frames."""

    options = PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.6,
        min_pose_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS,         30)

    with lock:
        session["running"] = True

    last_rep_time = 0.0
    last_left_rep_time = 0.0
    last_right_rep_time = 0.0
    prev_time     = time.time()
    frame_ts_ms   = 0

    with mp_vision.PoseLandmarker.create_from_options(options) as landmarker:

        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]

            # ── FPS ───────────────────────────────────────────
            now       = time.time()
            fps       = 1.0 / (now - prev_time + 1e-9)
            prev_time = now

            # ── MediaPipe Tasks inference ─────────────────────
            rgb       = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            frame_ts_ms += 33          # ~30 fps timestamp increment
            result: PoseLandmarkerResult = landmarker.detect_for_video(mp_image, frame_ts_ms)

            image         = frame.copy()
            pose_detected = bool(result.pose_landmarks)

            form_warning    = ""
            posture_ok      = True
            posture_warning = ""
            angle           = 0.0
            left_angle      = 0.0
            right_angle     = 0.0

            with lock:
                mode          = session["mode"]
                counter       = session["counter"]
                stage         = session["stage"]
                cal           = session["calories"]
                left_counter  = session["left_counter"]
                right_counter = session["right_counter"]
                left_stage    = session["left_stage"]
                right_stage   = session["right_stage"]
                left_prev_angle = session["left_angle"]
                right_prev_angle = session["right_angle"]

            if pose_detected:
                landmarks = result.pose_landmarks[0]  # first person

                try:
                    # ── Exercise logic ─────────────────────────
                    if mode == "curl":
                        (left_counter, left_stage, left_angle, last_left_rep_time,
                         right_counter, right_stage, right_angle, last_right_rep_time) = curl_counter(
                             landmarks, left_counter, left_stage, last_left_rep_time, left_prev_angle,
                             right_counter, right_stage, last_right_rep_time, right_prev_angle
                         )
                        counter = left_counter + right_counter
                        if left_angle > 170 or right_angle > 170:
                            form_warning = "DON'T OVER-EXTEND ARM"
                        angle = max(left_angle, right_angle)
                        stage = left_stage
                        
                        # Debug prints for bilateral bicep curl tracking
                        print(f"[DEBUG] Left Angle: {left_angle:.1f} | Right Angle: {right_angle:.1f} | Left Stage: {left_stage} | Right Stage: {right_stage}")

                    elif mode == "pushup":
                        counter, stage, angle, last_rep_time = pushup_counter(
                            landmarks, counter, stage, last_rep_time)
                        if angle > 175:
                            form_warning = "GO LOWER"
                        left_angle = angle
                        right_angle = angle

                    elif mode == "squat":
                        counter, stage, angle, last_rep_time = squat_counter(
                            landmarks, counter, stage, last_rep_time)
                        if angle > 170:
                            form_warning = "BEND YOUR KNEES MORE"
                        left_angle = angle
                        right_angle = angle

                    # Reset local timers if session got reset externally
                    if counter == 0:
                        last_rep_time = 0.0
                        last_left_rep_time = 0.0
                        last_right_rep_time = 0.0

                    # ── Posture check ──────────────────────────
                    posture_ok, posture_warning = check_posture(landmarks, mode)

                    # ── Calories ───────────────────────────────
                    cal = round(counter * CALORIE_PER_REP.get(mode, 0.5), 2)

                except Exception:
                    pass

                # ── Draw skeleton ──────────────────────────────
                _draw_skeleton(image, landmarks, w, h)

                # ── Draw debug overlay on screen ────────────────────
                if mode == "curl":
                    overlay = image.copy()
                    cv2.rectangle(overlay, (15, 15), (325, 135), (10, 10, 15), -1)
                    cv2.rectangle(overlay, (15, 15), (325, 135), (57, 255, 20), 1)  # neon green border
                    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    line_type = cv2.LINE_AA
                    color_left = (57, 255, 20)      # neon green
                    color_right = (255, 0, 128)     # neon pink/magenta
                    color_title = (255, 255, 255)   # white

                    cv2.putText(image, "CYBER-DEBUG: BILATERAL CURL", (25, 35), font, 0.45, color_title, 1, line_type)
                    cv2.putText(image, f"LEFT ANGLE: {left_angle:.1f} deg", (25, 60), font, font_scale, color_left, 1, line_type)
                    cv2.putText(image, f"LEFT STAGE: {str(left_stage or '---').upper()}", (25, 80), font, font_scale, color_left, 1, line_type)
                    cv2.putText(image, f"RIGHT ANGLE: {right_angle:.1f} deg", (25, 105), font, font_scale, color_right, 1, line_type)
                    cv2.putText(image, f"RIGHT STAGE: {str(right_stage or '---').upper()}", (25, 125), font, font_scale, color_right, 1, line_type)

            # ── Update shared state ───────────────────────────
            with lock:
                session["counter"]         = counter
                session["stage"]           = stage
                session["angle"]           = round(float(angle), 1)
                session["calories"]        = cal
                session["posture_ok"]      = posture_ok
                session["posture_warning"] = posture_warning
                session["form_warning"]    = form_warning
                session["fps"]             = round(fps, 1)
                session["pose_detected"]   = pose_detected
                session["left_counter"]    = left_counter
                session["right_counter"]   = right_counter
                session["left_stage"]      = left_stage
                session["right_stage"]     = right_stage
                session["left_angle"]      = round(float(left_angle), 1)
                session["right_angle"]     = round(float(right_angle), 1)

            # ── MJPEG encode ──────────────────────────────────
            _, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 80])
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buf.tobytes()
                + b"\r\n"
            )

    cap.release()
    with lock:
        session["running"] = False


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/status")
def get_status():
    with lock:
        return jsonify(dict(session))


@app.route("/api/set_mode", methods=["POST"])
def set_mode():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "").strip().lower()
    if mode not in ("curl", "pushup", "squat"):
        return jsonify({"error": "mode must be curl | pushup | squat"}), 400
    with lock:
        session.update({
            "mode": mode, "counter": 0, "stage": None,
            "angle": 0.0, "form_warning": "", "posture_warning": "",
            "left_counter": 0, "right_counter": 0,
            "left_stage": None, "right_stage": None,
            "left_angle": 0.0, "right_angle": 0.0,
        })
    return jsonify({"status": "ok", "mode": mode})


@app.route("/api/reset", methods=["POST"])
def reset():
    with lock:
        session.update({
            "counter": 0, "stage": None, "calories": 0.0,
            "angle": 0.0, "form_warning": "", "posture_warning": "",
            "left_counter": 0, "right_counter": 0,
            "left_stage": None, "right_stage": None,
            "left_angle": 0.0, "right_angle": 0.0,
        })
    return jsonify({"status": "reset"})


@app.route("/api/session_summary")
def session_summary():
    with lock:
        return jsonify({
            "mode":       session["mode"],
            "reps":       session["counter"],
            "calories":   session["calories"],
            "posture_ok": session["posture_ok"],
            "left_reps":  session["left_counter"],
            "right_reps": session["right_counter"],
        })


@app.route("/api/generate_diet", methods=["POST"])
def generate_diet():
    data = request.get_json(silent=True) or {}
    weight = data.get("weight")
    goal = data.get("goal", "").strip().lower()

    if not weight:
        return jsonify({"error": "Weight is required"}), 400
    try:
        weight = float(weight)
    except ValueError:
        return jsonify({"error": "Weight must be a valid number"}), 400

    if weight < 20 or weight > 250:
        return jsonify({"error": "Weight must be between 20kg and 250kg"}), 400

    if goal not in ("gain", "loss", "maintain"):
        return jsonify({"error": "Goal must be muscle gain, fat loss, or maintenance"}), 400

    # 1. Protein & Calories Calculations
    if goal == "gain":
        protein = round(weight * 2.0)
        calories = round(weight * 35)
    elif goal == "loss":
        protein = round(weight * 1.8)
        calories = round(weight * 24)
    else:  # maintain
        protein = round(weight * 1.4)
        calories = round(weight * 30)

    # 2. Water Intake
    water = round(weight * 0.04, 1)

    # 3. Dynamic Indian Diet Plan
    if goal == "gain":
        breakfast = f"Oats porridge ({round(weight * 0.8)}g oats) made with 1.5 glasses of Milk, topped with 2 Bananas, 2 tbsp Peanut Butter, and 3 boiled Eggs (or Sattu milk shake with almonds)."
        lunch = f"250g Chicken Breast (or 200g Paneer Bhurji/Scramble), 1.5 cups Cooked Rice, 1 bowl Dal, and a large portion of Mixed Green Salad."
        evening = f"Sattu drink (40g Sattu powder mixed in milk/water with a pinch of black salt), 1 Banana, and a handful of mixed almonds/cashews."
        dinner = f"3 Wheat Rotis, 150g Paneer/Chicken Curry, 1 bowl Thick Dal, and a side of steamed vegetables (broccoli/cauliflower)."
    elif goal == "loss":
        breakfast = f"Oats ({round(weight * 0.5)}g) cooked in water, 4 boiled Egg whites (or 100g Tofu/Paneer scramble with veggies), and 1 Apple."
        lunch = f"150g Grilled Chicken Breast (or 120g low-fat Paneer), 1 small bowl of Dal, a large raw cucumber & tomato salad, and 1 whole wheat Roti."
        evening = f"1 cup unsweetened Green Tea, a handful of roasted Chana (chickpeas), or 1 glass of refreshing low-fat buttermilk (Chaas)."
        dinner = f"Sautéed Tofu/Paneer (150g) cooked with bell peppers and spinach, 1 bowl clear Lentil (Dal) soup, and sliced raw carrots."
    else:  # maintain
        breakfast = f"Oats porridge ({round(weight * 0.6)}g oats) made with 1 glass of Milk, 1 Banana, 1.5 tbsp Peanut Butter, and 2 boiled Eggs (or 120g Paneer bhurji)."
        lunch = f"150g Paneer/Chicken Breast curry, 1 cup Cooked Rice, 1 bowl Dal, 1 whole wheat Roti, and a raw mixed green salad."
        evening = f"Sattu shake (30g Sattu in water or milk) or 1 glass of thick Sweet/Salty Lassi, and 1 Apple."
        dinner = f"2 Wheat Rotis, 120g Paneer or Chicken curry, 1 bowl Dal, and a fresh salad of cucumber and carrot."

    return jsonify({
        "status": "success",
        "protein": f"{protein} g/day",
        "calories": f"{calories} kcal",
        "water": f"{water} liters",
        "diet": {
            "breakfast": breakfast,
            "lunch": lunch,
            "evening": evening,
            "dinner": dinner
        }
    })


@app.route("/")
def health():
    return jsonify({"status": "AI Fitness Trainer backend running ✓"})


# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("[INFO] Starting AI Fitness Trainer backend on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)