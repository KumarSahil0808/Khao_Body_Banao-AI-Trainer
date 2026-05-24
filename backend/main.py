import cv2
import mediapipe as mp
import time

from backend.exercises.curl import curl_counter
from backend.exercises.pushup import pushup_counter
from backend.exercises.squat import squat_counter

from backend.utils.ui import draw_ui
from backend.utils.voice import speak

# =========================
# VARIABLES
# =========================

warning_time = 0
wrong_form_start = 0
last_motivation_rep = 0

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

cap.set(3, 1280)
cap.set(4, 720)

counter = 0
stage = None
mode = "curl"
last_rep_time = 0

# =========================
# MAIN LOOP
# =========================

with mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as pose:

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        image.flags.writeable = False

        results = pose.process(image)

        image.flags.writeable = True

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:

            landmarks = results.pose_landmarks.landmark

            # =========================
            # EXERCISE MODES
            # =========================

            if mode == "curl":

                counter, stage, angle, last_rep_time = curl_counter(
                    landmarks,
                    counter,
                    stage,
                    last_rep_time
                )

                exercise_name = "BICEP CURL"

            elif mode == "pushup":

                counter, stage, angle, last_rep_time = pushup_counter(
                    landmarks,
                    counter,
                    stage,
                    last_rep_time
                )

                exercise_name = "PUSHUP"

            elif mode == "squat":

                counter, stage, angle, last_rep_time = squat_counter(
                    landmarks,
                    counter,
                    stage,
                    last_rep_time
                )

                exercise_name = "SQUAT"

            # =========================
            # CALORIES
            # =========================

            calories = counter * 0.5

            # =========================
            # FORM CHECK
            # =========================

            form_correct = True
            warning_message = ""

            # CURL FORM
            if mode == "curl":

                if angle > 170:
                    form_correct = False
                    warning_message = "DON'T OVER EXTEND ARM"

            # PUSHUP FORM
            elif mode == "pushup":

                if angle > 175:
                    form_correct = False
                    warning_message = "GO LOWER"

            # SQUAT FORM
            elif mode == "squat":

                if angle > 170:
                    form_correct = False
                    warning_message = "BEND YOUR KNEE"

            # =========================
            # RED WARNING SCREEN
            # =========================

            current_time = time.time()

            if not form_correct:

                if wrong_form_start == 0:
                    wrong_form_start = current_time

                # 2 second delay
                if current_time - wrong_form_start >= 2:

                    cv2.rectangle(
                        image,
                        (300, 250),
                        (1000, 380),
                        (0,0,255),
                        -1
                    )

                    cv2.putText(
                        image,
                        warning_message,
                        (330,330),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.2,
                        (255,255,255),
                        3
                    )

                    if current_time - warning_time > 3:

                        speak(warning_message)

                        warning_time = current_time

            else:

                wrong_form_start = 0

            # =========================
            # UI
            # =========================

            draw_ui(
                image,
                exercise_name,
                counter,
                stage,
                calories
            )

            # =========================
            # MOTIVATION VOICE
            # =========================

            if counter == 10 and last_motivation_rep != 10:

                if mode == "curl":

                    speak("Great Bicep Curls Keep Going")

                elif mode == "pushup":

                    speak("Awesome Pushups You Can Do It")

                elif mode == "squat":

                    speak("Good Squats Keep Pushing")

                last_motivation_rep = 10

            elif counter == 20 and last_motivation_rep != 20:

                if mode == "curl":

                    speak("Excellent Bicep Workout")

                elif mode == "pushup":

                    speak("Amazing Pushups Keep Going")

                elif mode == "squat":

                    speak("Strong Squats Well Done")

                last_motivation_rep = 20

            elif counter == 30 and last_motivation_rep != 30:

                speak("Awesome Workout You Can Do It")

                last_motivation_rep = 30

        except:
            pass

        # =========================
        # DRAW LANDMARKS
        # =========================

        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        # =========================
        # CONTROLS TEXT
        # =========================

        cv2.putText(
            image,
            "1 = CURL | 2 = PUSHUP | 3 = SQUAT | Q = EXIT",
            (10,700),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        cv2.imshow("AI FITNESS TRAINER", image)

        key = cv2.waitKey(10) & 0xFF

        # =========================
        # KEYS
        # =========================

        if key == ord('1'):

            mode = "curl"
            counter = 0
            last_motivation_rep = 0

            speak("Bicep Curl Mode")

        elif key == ord('2'):

            mode = "pushup"
            counter = 0
            last_motivation_rep = 0

            speak("Pushup Mode")

        elif key == ord('3'):

            mode = "squat"
            counter = 0
            last_motivation_rep = 0

            speak("Squat Mode")

        elif key == ord('q'):
            break

# =========================
# RELEASE CAMERA
# =========================

cap.release()

cv2.destroyAllWindows()