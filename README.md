# ⚡ Khao Body Banao – AI Fitness Trainer ⚡

<p align="center">
  <img src="https://img.shields.io/badge/AI_Engine-MediaPipe-00fbfb?style=for-the-badge&logo=google&logoColor=white" alt="MediaPipe Engine" />
  <img src="https://img.shields.io/badge/Backend-Flask_/_Python-39ff14?style=for-the-badge&logo=python&logoColor=white" alt="Flask Python Backend" />
  <img src="https://img.shields.io/badge/Frontend-HTML5_/_CSS3_/_JS-ff007f?style=for-the-badge&logo=javascript&logoColor=white" alt="HTML CSS JS Frontend" />
  <img src="https://img.shields.io/badge/Theme-Cyberpunk_/_Neon-00fbfb?style=for-the-badge" alt="Cyberpunk Theme" />
</p>

---

## 🌌 Overview

**Khao Body Banao** is a premium, state-of-the-art **AI Fitness Trainer and Diet Planner** designed with a stunning futuristic **Cyberpunk / Neon Green / Electric Cyan** gaming aesthetics. Powered by **MediaPipe Pose Landmarking**, the application performs real-time computer vision analysis via your webcam to track workout form, count repetitions, calculate calories burned, and warn you of posture deviations—all guided by a fully interactive **AI Voice Coach**.

Built for modern browsers and developers looking to showcase advanced computer vision integrations, it features a glassmorphic dashboard, bilateral curl tracking, a personalized diet planner ("Khao Body Banao"), and highly satisfying real-time "+1 REP 🔥" visual popups.

---

## 🚀 Key Features

*   **🦾 Real-Time AI Pose Detection**: Captures 33 skeletal keypoints at high FPS to analyze joint extension and flexion angles dynamically.
*   **💪 Bilateral Curl Tracking**: Monitors left and right arms independently. Displays individual arm angles, states (`UP`/`DOWN`), and separate repetition counters.
*   **🔊 Interactive AI Voice Coach**: Uses browser-native speech synthesis to act as an active trainer:
    *   Announces exercise mode activations ("Bicep Curl Mode Activated").
    *   Provides edge-triggered real-time posture corrections ("Straighten your back").
    *   Shouts randomized appreciation milestones every 10 reps ("Awesome work! Keep it up!").
    *   Features intelligent anti-spam cooldowns.
*   **🔥 Satisfying Gamified UI Popups**: Displays vibrant floating "+1 REP 🔥" neon popup notifications on rep completion, positioned dynamically near the tracking feed corresponding to the active side (Left/Right/Center).
*   **🥗 "Khao Body Banao" Diet System**: A built-in expert nutrition generator. Inputs body weight and fitness goals (Gain/Loss/Maintain) to calculate exact daily protein target, water intake, estimated calories, and outputs a complete breakfast-to-dinner meal layout.
*   **⚠️ Real-Time Posture Guard**: Monitors spinal alignment and shoulder tilt, providing instant visual warnings ("FIX POSTURE") and voice alerts when form compromises.
*   **⚡ Cyberpunk Performance Hud**: A stunning dark cyber-grid interface styled with rich glassmorphism (`backdrop-filter`), glowing neon indicators, real-time FPS counters, active connection badges, and responsive layouts.

---

## 🛠️ Tech Stack

*   **Core Logic & Computer Vision**:
    *   [Python 3](https://www.python.org/)
    *   [OpenCV](https://opencv.org/) (Real-time frame ingestion & manipulation)
    *   [Google MediaPipe](https://google.github.io/mediapipe/) (Pose Landmarking Engine)
*   **Server Architecture**:
    *   [Flask](https://flask.palletsprojects.com/) (Python Web Server hosting REST APIs & MJPEG Video Feed Streaming)
    *   [Flask-CORS](https://flask-cors.readthedocs.io/)
*   **Futuristic Frontend**:
    *   HTML5 (Semantic Structure)
    *   CSS3 (Custom Variable Design Tokens, Glassmorphism, Neon Glow Filters, Dynamic Keyframe Animations)
    *   Vanilla JavaScript (ES6+, REST Poll Engines, Asynchronous Voice Synthesizer, Dynamic DOM Popups, Canvas Updates)

---

## 🖼️ Dashboard & UI Showcase

### 🎛️ Main Dashboard View
> [!NOTE]  
> *A high-fidelity glassmorphic command center with neon green visual accents, interactive control panels, and live connection streams.*
```
┌────────────────────────────────────────────────────────────────────────┐
│ [LIVE] CONNECTION: LIVE                                       FPS: 30 │
├──────────────────────────┬─────────────────────────────────────────────┤
│ 👤 WORKOUT PANEL         │            [ LIVE CAMERA FEED ]             │
│   Mode: Bicep Curl       │                                             │
│   Reps: 12   Calories: 72│             ┌─────────┐ ┌─────────┐         │
│   Angle: L:45.2° R:112.5°│             │  LEFT   │ │  RIGHT  │         │
│   Posture: OK            │             │ 6 REPS  │ │ 6 REPS  │         │
│                          │             │  [UP]   │ │ [DOWN]  │         │
│ 🔊 AI VOICE COACH        │             └─────────┘ └─────────┘         │
│   [VOICE ON] Ready       │               +1 REP 🔥 (Cyan Floating)      │
│   "Excellent form!"      │                                             │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### 💪 Bilateral Curl Tracking Showcase
> [!TIP]  
> *Splits the video analytical overlay to independently display left-arm (electric cyan) and right-arm (neon green) pose variables.*
```
                  [ WEBCAM VIDEO STREAM ]
         / \ (Head)
        /   \
 (L. Arm) O===O (R. Arm)
   L: 42° |   | R: 114°
  [+1 REP 🔥]  [+1 REP 🔥]
   (Cyan)       (Green)
```

### 🍲 Diet Planner Layout ("Khao Body Banao")
> [!IMPORTANT]  
> *Generate personalized macronutrient configurations and complete whole-food diet splits with the touch of a button.*
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

## ⚙️ Installation & Setup

### Prerequisites
*   Python 3.8 or higher installed on your system.
*   A functional webcam.

### 📥 Step 1: Clone and Navigate
```bash
git clone https://github.com/KumarSahil0808/Khao_Body_Banao-AI-Trainer.git
cd Khao_Body_Banao-AI-Trainer
```

### 🐍 Step 2: Backend Dependencies Setup
Create a virtual environment (recommended) and install backend packages:
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install Flask opencv-python mediapipe flask-cors
```

### 🌐 Step 3: Frontend Setup
The frontend is built entirely on vanilla web technologies. It is fully ready to connect and requires no compilation step! 

---

## 🎮 How to Run

### 1. Launch the Flask API Server
From your activated terminal in the `backend` directory, run:
```bash
python app.py
```
*The server will boot up and bind to `http://localhost:5000`.*

### 2. Launch the Futuristic Frontend Dashboard
Simply open the `index.html` file located in the `frontend` folder:
*   Double-click `frontend/index.html` to open in any modern browser (Chrome, Edge, Safari, Firefox).
*   Alternatively, run it using a lightweight development server like VS Code Live Server or python's built-in HTTP server:
    ```bash
    cd ../frontend
    python -m http.server 8000
    ```
    *Then navigate to `http://localhost:8000`.*

---

## 🌌 Future Roadmap

*   [ ] **🏋️ Multi-Exercise expansion**: Add tracking modules for Overhead Shoulder Presses, Lunges, Plank timing, and Deadlifts.
*   [ ] **📈 Persistent User Analytics**: Connect an SQLite/MongoDB backend to track workout consistency, rep histories, and weight curves.
*   [ ] **🔗 Mobile Companion App**: Develop a lightweight React Native client mapping coordinates to mobile cameras.
*   [ ] **🎮 AR Avatar Gamification**: Render a full cybernetic avatar mimicking user poses in high-definition 3D space.

---

## 💻 Developer

Crafted with premium engineering and cybernetic styling:

<p align="left">
  <a>
    <img src="https://img.shields.io/badge/Developer-SK-39ff14?style=for-the-badge&logo=github&logoColor=black&labelColor=121222" alt="SK Signature" />
  </a>
</p>

---

<p align="center">
  ⭐ <b>If this project motivated you to build strength, drop a Star on GitHub!</b> ⭐
</p>
