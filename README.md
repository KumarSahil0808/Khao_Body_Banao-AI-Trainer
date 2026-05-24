# ⚡ Khao Body Banao – AI Fitness Trainer ⚡

<p align="center">
  <img src="https://img.shields.io/badge/AI_Fitness_Trainer-Active-39ff14?style=for-the-badge&logo=android&logoColor=black" alt="Status Active" />
  <img src="https://img.shields.io/badge/Design_Theme-Cyberpunk_Neon-00fbfb?style=for-the-badge" alt="Cyberpunk Theme" />
  <img src="https://img.shields.io/badge/Easy_To_Run-100%25-ff007f?style=for-the-badge" alt="Easy to run" />
</p>

---

## 🌌 Introduction

Welcome to **Khao Body Banao** – a super cool, game-like **AI Fitness Trainer and Diet Planner**! 

Have you ever wanted a gym buddy who watches your posture, counts your reps, gives you voice motivation, and plans your meals, all while looking like a futuristic arcade game? That is exactly what this project does!

Using just your **webcam**, this application turns your room into an AI-powered fitness lab. It tracks your skeletal joints in real-time, counts bicep curls, alerts you when your back is bent, and cheers you up with an active **AI Voice Coach**!

---

## 🔥 Awesome Features

*   **🤖 AI Body Tracking**: Instantly tracks your body joints on screen using smart webcam cameras.
*   **💪 Double Arm Tracking**: Counts left and right arm bicep curls separately so you keep your muscle gains completely balanced!
*   **🔊 Motivational AI Voice Coach**: A real voice built right into the app that:
    *   Tells you when workout modes are activated.
    *   Gives quick posture advice like *"Straighten your back!"* when you slouch.
    *   Congratulates you every 10 reps with random cheerful lines like *"Awesome work!"* or *"Push harder!"*.
*   **💥 +1 REP Visual Popups**: Every single time you finish a clean rep, a floating, glowing **"+1 REP 🔥"** text pops up next to your video feed. It moves up and fades away smoothly like high-score numbers in an arcade video game!
*   **🥗 "Khao Body Banao" Diet Planner**: Enter your weight and fitness goals (Muscle Gain, Fat Loss, or Keep Fit) to instantly get your daily protein target, water amount, estimated calories, and a full breakfast-to-dinner meal plan!
*   **🚦 Posture Shield Alert**: Shows a bright red **"FIX POSTURE"** signal on your screen if your back is curved or shoulders are tilted, helping you avoid gym injuries!
*   **🎮 Cyberpunk Aesthetic**: A beautiful dark dashboard layout filled with glassmorphic cards, glowing neon green and cyan visual effects, connection status indicators, and live FPS speedometers.

---

## 🛠️ The Tech Stack (What makes it tick)

We kept the technology super simple, modular, and fast:
*   **🐍 Backend (The Brains)**: Powered by **Python & Flask**. Flask streams the live webcam video feed and calculates joint angles.
*   **👁️ Computer Vision**: Powered by **Google MediaPipe** and **OpenCV** to track skeleton joints without any expensive graphic cards.
*   **🎨 Frontend (The Looks)**: Built with clean **HTML5, CSS3, and JavaScript**. Custom CSS handles the high-glow cyberpunk panels and floaty "+1 REP 🔥" animations. Vanilla JS polls the stats from the backend and triggers the Voice Synthesis engine.

---

## 🖼️ App Layout & Screenshots

### 🖥️ Futuristic Game Dashboard
*A glassmorphic cyber-grid command center showing your stats, live feed, posture ratings, and live AI Coach waveforms.*
```
┌────────────────────────────────────────────────────────────────────────┐
│ [LIVE FEED] CONNECTION: ONLINE                                FPS: 30 │
├──────────────────────────┬─────────────────────────────────────────────┤
│ 👤 FIT PANEL             │            [ LIVE CAMERA FEED ]             │
│   Mode: BICEP CURL       │                                             │
│   Reps: 12   Calories: 72│             ┌─────────┐ ┌─────────┐         │
│   Angle: 94.2°           │             │  LEFT   │ │  RIGHT  │         │
│   Posture: EXCELLENT     │             │ 6 REPS  │ │ 6 REPS  │         │
│                          │             │  [UP]   │ │ [DOWN]  │         │
│ 🔊 AI VOICE COACH        │             └─────────┘ └─────────┘         │
│   [VOICE ON] Active      │               +1 REP 🔥 (Cyan Float VFX)    │
│   "Keep going!"          │                                             │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### 🍲 Diet Recommendation Cards ("Khao Body Banao")
*Inputs your stats to generate custom daily nutritional goals and high-protein meal guides instantly.*
```
┌────────────────────────────────────────────────────────────────────────┐
│ 🥗 KHAO BODY BNAO DIET PLANNER                                         │
│   Weight: [ 70 ] KG    Goal: [ Muscle Gain ]       [ GENERATE PLAN ]   │
├────────────────────────────────────────────────────────────────────────┤
│  ⚡ PROTEIN: 140g   |  🔥 CALORIES: 2310 kcal   |  💧 WATER: 3.5 Liters  │
├────────────────────────────────────────────────────────────────────────┤
│  🍳 BREAKFAST: Egg Whites, Oatmeal, Almonds, Banana                    │
│  🍲 LUNCH: Chicken Breast/Paneer, Brown Rice, Mixed Salad, Dal         │
│  🥛 SNACK: Whey Protein Shake or Sprouted Moong, Boiled Eggs           │
│  🍗 DINNER: Grilled Fish/Tofu, Sweet Potato, Steamed Broccoli          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Installation & Setup (Super Easy!)

### 📥 Step 1: Download the Project
Download or clone the files to your computer:
```bash
git clone https://github.com/KumarSahil0808/Khao_Body_Banao-AI-Trainer.git
cd Khao_Body_Banao-AI-Trainer
```

### 🐍 Step 2: Setup the Python Backend
Make sure you have [Python](https://www.python.org/downloads/) installed. Open your command terminal in the folder and type:
```bash
# Go to backend folder
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
# On Windows, activate it:
.\venv\Scripts\activate
# On Mac/Linux, activate it:
source venv/bin/activate

# Install the dependencies
pip install Flask opencv-python mediapipe flask-cors
```

---

## 🎮 How to Run

### 1. Fire up the backend server:
From your terminal in the `backend` folder, run:
```bash
python app.py
```
*Your backend is now live and waiting at `http://localhost:5000`!*

### 2. Open the frontend dashboard:
*   Open the `frontend` folder.
*   Double-click the `index.html` file to launch it directly in your favorite browser (Chrome, Edge, Firefox, or Safari)!
*   No special compiler required—it just works out of the box!

---

## 🌌 Future Plans (What's Next?)

*   **🏋️ More Exercises**: Support squat depth counting, push-ups, planks, and shoulder presses.
*   **📊 History Charts**: Add graphs to track your workouts over days and weeks.
*   **📱 Mobile Friendly**: Make it run smoothly on your smartphone browser.
*   **🎮 AR Cyber Avatar**: Render a cool 3D holographic robot copy of you that mimics your poses!

---

## 💻 Developer

Created with visual excellence and clean coding by:

<p align="left">
  <a>
    <img src="https://img.shields.io/badge/Developer-SK-39ff14?style=for-the-badge&logo=github&logoColor=black&labelColor=121222" alt="SK Badge" />
  </a>
</p>

---

<p align="center">
  ⭐ <b>If this project made you want to exercise or code, drop a Star!</b> ⭐
</p>
