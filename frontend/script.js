/**
 * AI Fitness Trainer — Frontend Script
 * ======================================
 * Connects to the Flask backend at http://localhost:5000.
 *
 * Architecture:
 *  - MJPEG stream  → <img #video-feed src="/video_feed">
 *    The backend already draws the skeleton + HUD onto frames.
 *  - REST polling  → GET /api/status every 500 ms
 *    Updates all stat cards, posture warnings, rep counter ring, etc.
 *  - REST commands → POST /api/set_mode, POST /api/reset
 */

"use strict";

const BACKEND = "http://localhost:5000";
const POLL_MS = 500;   // status poll interval
const MAX_REPS = 30;   // ring fills at this number

/* ─── Exercise config ─────────────────────────── */
const EXERCISE_CONFIG = {
  curl: {
    label:  "BICEP CURL",
    tips:   ["Keep upper arm fixed", "Curl all the way to 40°", "Lower slowly (3 sec)"],
    quotes: [
      "\"Squeeze at the top. Feel it.\"",
      "\"Control beats speed every time.\"",
      "\"Your arms are getting stronger rep by rep.\"",
    ],
  },
  pushup: {
    label:  "PUSH-UP",
    tips:   ["Body in a straight plank", "Chest touches the floor", "Exhale on the push"],
    quotes: [
      "\"Gravity is your training partner.\"",
      "\"Perfect form over speed.\"",
      "\"10 clean reps beat 30 sloppy ones.\"",
    ],
  },
  squat: {
    label:  "SQUAT",
    tips:   ["Feet shoulder-width apart", "Knees track over toes", "Drive through the heels"],
    quotes: [
      "\"Strong legs, strong foundation.\"",
      "\"Get low. Build power.\"",
      "\"Champions squat deeper.\"",
    ],
  },
};

/* ─── DOM refs ────────────────────────────────── */
const elFeed       = document.getElementById("video-feed");
const elOverlay    = document.getElementById("feed-overlay");
const elOverTxt    = document.getElementById("overlay-text");
const elModeName   = document.getElementById("mode-name");
const elReps       = document.getElementById("rep-counter");
const elRing       = document.getElementById("ring-progress");
const elStageBadge = document.getElementById("stage-badge");
const elCalories   = document.getElementById("calories");
const elAngle      = document.getElementById("joint-angle");
const elFPS        = document.getElementById("fps-val");
const elPostureDot = document.getElementById("posture-dot");
const elPostureSt  = document.getElementById("posture-status");
const elPostureW   = document.getElementById("posture-warning");
const elFormWarn   = document.getElementById("form-warning-banner");
const elTips       = document.getElementById("tips-list");
const elQuote      = document.getElementById("coach-quote");
const elSumReps    = document.getElementById("summary-reps");
const elSumCals    = document.getElementById("summary-cals");
const elSumMode    = document.getElementById("summary-mode");
const elTimer      = document.querySelector(".session-timer .mono");
const elStatusBadge= document.getElementById("connection-badge");
const elStatusDot  = document.getElementById("status-dot");
const elStatusLbl  = document.getElementById("status-label");
const elReconnect  = document.getElementById("reconnect-btn");

const elMainRepContainer = document.querySelector(".rep-ring-container");
const elCurlContainer    = document.getElementById("curl-counters-container");
const elLeftReps         = document.getElementById("left-rep-counter");
const elRightReps        = document.getElementById("right-rep-counter");
const elLeftStageBadge   = document.getElementById("left-stage-badge");
const elRightStageBadge  = document.getElementById("right-stage-badge");

const modeBtns = document.querySelectorAll(".mode-btn");
const btnReset = document.getElementById("btn-reset");

/* ─── Voice Coach Refs ────────────────────────── */
const elVoiceToggle    = document.getElementById("voice-toggle-btn");
const elVoiceLabel     = document.getElementById("voice-toggle-label");
const elVoiceCoachCard = document.getElementById("voice-coach-card");
const elVoiceStatusDot = document.getElementById("voice-status-dot");
const elVoiceStatusTxt = document.getElementById("voice-status-text");
const elVoiceWaveform  = document.getElementById("voice-waveform");
const elVoiceLastMsg   = document.getElementById("voice-last-msg");

/* ─── Diet Refs ────────────────────────────────── */
const elWeightInput     = document.getElementById("weight-input");
const elGoalSelect      = document.getElementById("goal-select");
const elGenerateDietBtn = document.getElementById("generate-diet-btn");
const elDietResults     = document.getElementById("diet-results");
const elRecProtein      = document.getElementById("recommend-protein");
const elRecCalories     = document.getElementById("recommend-calories");
const elRecWater        = document.getElementById("recommend-water");
const elMealBreakfast   = document.getElementById("meal-breakfast");
const elMealLunch       = document.getElementById("meal-lunch");
const elMealSnack       = document.getElementById("meal-snack");
const elMealDinner      = document.getElementById("meal-dinner");

/* ─── State ───────────────────────────────────── */
let currentMode       = "curl";
let lastRepCount      = 0;
let lastLeftRepCount  = 0;
let lastRightRepCount = 0;
let isConnected     = false;
let pollTimer       = null;
let sessionStart    = Date.now();
let sessionTimerID  = null;
let quoteIdx        = 0;
let lastPostureOk   = true;    // track posture changes for voice alerts
let hasGreetedUser  = false;   // track if user has been welcomed this session

/* ═══════════════════════════════════════════════
   AI VOICE COACH ENGINE
═══════════════════════════════════════════════ */
const VoiceCoach = (() => {
  const synth = window.speechSynthesis;

  /* ── Message banks ───────────────────────────── */
  const MOTIVATION = [
    "Great job! Keep it up!",
    "Keep going! You're doing amazing!",
    "Excellent form! Stay strong!",
    "You are getting stronger every rep!",
    "Awesome work! Don't stop now!",
    "Push harder! You've got this!",
    "Stay focused! Champions never quit!",
    "Incredible pace! Keep the rhythm!",
    "Your dedication is inspiring!",
    "That's the power! Feel it!",
  ];

  const MODE_ANNOUNCE = {
    curl:   "Bicep Curl Mode Activated. Let's build those arms.",
    pushup: "Push-Up Mode Activated. Time to work the chest.",
    squat:  "Squat Mode Activated. Strong legs, strong foundation.",
  };

  const POSTURE_WARNINGS = [
    "Straighten your back.",
    "Fix your posture.",
    "Keep your shoulders balanced.",
    "Watch your alignment.",
    "Engage your core for better posture.",
  ];

  const WELCOME = "Welcome buddy, let's build strength together.";

  /* ── State ────────────────────────────────────── */
  let enabled         = true;
  let isSpeaking      = false;
  let lastSpokenText  = "";
  let lastMotivIdx    = -1;
  let lastPostureIdx  = -1;
  let selectedVoice   = null;
  let voicesLoaded    = false;

  /* Cooldowns (ms) */
  const COOLDOWN_MOTIVATION = 8000;
  const COOLDOWN_POSTURE    = 10000;
  const COOLDOWN_MODE       = 2000;
  let lastMotivTime   = 0;
  let lastPostureTime = 0;
  let lastModeTime    = 0;

  /* ── Voice selection ─────────────────────────── */
  function pickVoice() {
    const voices = synth.getVoices();
    if (!voices.length) return;

    // Prefer a natural-sounding English voice
    const preferred = [
      "Google UK English Female",
      "Google US English",
      "Microsoft Zira",
      "Microsoft David",
      "Samantha",
      "Alex",
    ];

    for (const name of preferred) {
      const v = voices.find(v => v.name.includes(name));
      if (v) { selectedVoice = v; return; }
    }

    // Fallback: first English voice
    const enVoice = voices.find(v => v.lang.startsWith("en"));
    if (enVoice) selectedVoice = enVoice;
    else selectedVoice = voices[0];
  }

  // Voices may load asynchronously
  if (synth) {
    synth.onvoiceschanged = () => { pickVoice(); voicesLoaded = true; };
    pickVoice(); // try immediately
  }

  /* ── Core speak function ─────────────────────── */
  function speak(text, { rate = 1.0, pitch = 1.05 } = {}) {
    if (!enabled || !synth || !text) return;
    if (text === lastSpokenText && isSpeaking) return;  // prevent exact duplicate while still speaking

    // Cancel any in-progress speech
    synth.cancel();

    const utter = new SpeechSynthesisUtterance(text);
    if (selectedVoice) utter.voice = selectedVoice;
    utter.rate   = rate;
    utter.pitch  = pitch;
    utter.volume = 1.0;

    utter.onstart = () => {
      isSpeaking = true;
      setUIState("speaking", text);
    };

    utter.onend = () => {
      isSpeaking = false;
      setUIState("ready");
    };

    utter.onerror = () => {
      isSpeaking = false;
      setUIState("ready");
    };

    lastSpokenText = text;
    synth.speak(utter);
  }

  /* ── UI state helpers ────────────────────────── */
  function setUIState(state, msg) {
    if (!elVoiceStatusDot) return;

    // Dot + text
    elVoiceStatusDot.className = "voice-status-dot " + (enabled ? state : "off");
    elVoiceStatusTxt.textContent = enabled
      ? (state === "speaking" ? "SPEAKING" : "READY")
      : "OFF";

    // Waveform
    if (state === "speaking") {
      elVoiceWaveform.classList.add("active");
      elVoiceCoachCard.classList.add("speaking");
    } else {
      elVoiceWaveform.classList.remove("active");
      elVoiceCoachCard.classList.remove("speaking");
    }

    // Last message display
    if (msg) {
      elVoiceLastMsg.textContent = `"${msg}"`;
      elVoiceLastMsg.classList.add("highlight");
      setTimeout(() => elVoiceLastMsg.classList.remove("highlight"), 2000);
    }
  }

  /* ── Pick random without immediate repeat ───── */
  function pickRandom(arr, lastIdx) {
    if (arr.length <= 1) return { idx: 0, text: arr[0] };
    let idx;
    do { idx = Math.floor(Math.random() * arr.length); } while (idx === lastIdx);
    return { idx, text: arr[idx] };
  }

  /* ── Public API ──────────────────────────────── */
  return {
    /** Toggle voice coach on/off */
    toggle() {
      enabled = !enabled;
      elVoiceToggle.classList.toggle("active", enabled);
      elVoiceToggle.setAttribute("aria-pressed", enabled ? "true" : "false");
      elVoiceLabel.textContent = enabled ? "VOICE ON" : "VOICE OFF";

      if (!enabled) {
        synth.cancel();
        isSpeaking = false;
        setUIState("off");
      } else {
        setUIState("ready");
        speak("Voice Coach activated. Let's go!");
      }
    },

    get isEnabled() { return enabled; },

    /** Welcome message on startup */
    welcome() {
      // Small delay to let voices load
      setTimeout(() => speak(WELCOME, { rate: 0.95, pitch: 1.0 }), 800);
    },

    /** Announce mode change */
    announceMode(mode) {
      const now = Date.now();
      if (now - lastModeTime < COOLDOWN_MODE) return;
      lastModeTime = now;

      const msg = MODE_ANNOUNCE[mode];
      if (msg) speak(msg, { rate: 1.0, pitch: 1.1 });
    },

    /** Motivational line every N reps */
    checkRepMilestone(repCount) {
      if (repCount <= 0 || repCount % 10 !== 0) return;
      const now = Date.now();
      if (now - lastMotivTime < COOLDOWN_MOTIVATION) return;
      lastMotivTime = now;

      const pick = pickRandom(MOTIVATION, lastMotivIdx);
      lastMotivIdx = pick.idx;
      speak(pick.text, { rate: 1.05, pitch: 1.1 });
    },

    /** Posture warning voice alerts */
    postureWarning(isOk) {
      if (isOk) return;  // only warn when posture is bad
      const now = Date.now();
      if (now - lastPostureTime < COOLDOWN_POSTURE) return;
      lastPostureTime = now;

      const pick = pickRandom(POSTURE_WARNINGS, lastPostureIdx);
      lastPostureIdx = pick.idx;
      speak(pick.text, { rate: 1.0, pitch: 0.95 });
    },
  };
})();

/* ── Voice toggle click handler ─────────────── */
if (elVoiceToggle) {
  elVoiceToggle.addEventListener("click", () => VoiceCoach.toggle());
}

/* ═══════════════════════════════════════════════
   FLOATING REP POPUP SYSTEM
═══════════════════════════════════════════════ */
let lastLeftPopupTime = 0;
let lastRightPopupTime = 0;
let lastCenterPopupTime = 0;

function showRepPopup(side) {
  const now = Date.now();
  if (side === "left") {
    if (now - lastLeftPopupTime < 400) return;
    lastLeftPopupTime = now;
  } else if (side === "right") {
    if (now - lastRightPopupTime < 400) return;
    lastRightPopupTime = now;
  } else {
    if (now - lastCenterPopupTime < 400) return;
    lastCenterPopupTime = now;
  }

  const elFeedWrapper = document.querySelector(".feed-wrapper");
  if (!elFeedWrapper) return;

  const popup = document.createElement("div");
  popup.className = `rep-popup ${side}-popup`;
  popup.textContent = "+1 REP 🔥";

  elFeedWrapper.appendChild(popup);

  // Auto-remove element after animation finishes
  popup.addEventListener("animationend", () => {
    popup.remove();
  });
}

/* ═══════════════════════════════════════════════
   VIDEO FEED
═══════════════════════════════════════════════ */
function startFeed() {
  // Bust cache so browser always reconnects
  elFeed.src = `${BACKEND}/video_feed?t=${Date.now()}`;
}

elFeed.addEventListener("load", () => {
  // First frame arrived — feed is live
  setConnected(true);
});

elFeed.addEventListener("error", () => {
  setConnected(false);
  // Retry after 3 s
  setTimeout(startFeed, 3000);
});

/* ═══════════════════════════════════════════════
   CONNECTION STATE
═══════════════════════════════════════════════ */
function setConnected(connected) {
  if (isConnected === connected) return;
  isConnected = connected;

  if (connected) {
    elOverlay.classList.add("hidden");
    elStatusBadge.classList.add("live");
    elStatusDot.classList.add("pulsing");
    elStatusLbl.textContent = "LIVE";
    startPoll();
  } else {
    elOverlay.classList.remove("hidden");
    elOverTxt.textContent = "BACKEND OFFLINE";
    elStatusBadge.classList.remove("live");
    elStatusDot.classList.remove("pulsing");
    elStatusLbl.textContent = "OFFLINE";
    stopPoll();
  }
}

/* ═══════════════════════════════════════════════
   STATUS POLLING
═══════════════════════════════════════════════ */
async function fetchStatus() {
  try {
    const res  = await fetch(`${BACKEND}/api/status`, { signal: AbortSignal.timeout(2000) });
    if (!res.ok) throw new Error("non-200");
    const data = await res.json();

    if (!isConnected) setConnected(true);
    updateUI(data);
  } catch {
    setConnected(false);
  }
}

function startPoll() {
  if (pollTimer) return;
  pollTimer = setInterval(fetchStatus, POLL_MS);
}

function stopPoll() {
  clearInterval(pollTimer);
  pollTimer = null;
}

/* ═══════════════════════════════════════════════
   UI UPDATE
═══════════════════════════════════════════════ */
function updateUI(data) {
  const { mode, counter, stage, angle, calories,
          posture_ok, posture_warning, form_warning, fps,
          left_counter, right_counter, left_stage, right_stage,
          left_angle, right_angle, pose_detected } = data;

  /* Voice Coach welcome greeting when user is first detected in the session */
  if (pose_detected && !hasGreetedUser) {
    hasGreetedUser = true;
    VoiceCoach.welcome();
  }

  /* Mode */
  const cfg = EXERCISE_CONFIG[mode] || EXERCISE_CONFIG.curl;
  elModeName.textContent  = cfg.label;
  elSumMode.textContent   = cfg.label;

  /* Reps */
  if (mode === "curl") {
    // Show curl counters side-by-side, hide central single ring
    elMainRepContainer.style.display = "none";
    elStageBadge.style.display = "none";
    elCurlContainer.style.display = "flex";

    if (left_counter !== undefined) {
      elLeftReps.textContent = left_counter;
      if (left_counter !== lastLeftRepCount) {
        animateRepBump(elLeftReps);
        showRepPopup("left");
        lastLeftRepCount = left_counter;
      }
    }

    if (right_counter !== undefined) {
      elRightReps.textContent = right_counter;
      if (right_counter !== lastRightRepCount) {
        animateRepBump(elRightReps);
        showRepPopup("right");
        lastRightRepCount = right_counter;
      }
    }

    // Stage badges for each arm
    const leftStageStr = (left_stage || "---").toUpperCase();
    elLeftStageBadge.textContent = leftStageStr;
    elLeftStageBadge.className = "stage-badge";
    if (left_stage === "UP") elLeftStageBadge.classList.add("up");
    if (left_stage === "DOWN") elLeftStageBadge.classList.add("down");

    const rightStageStr = (right_stage || "---").toUpperCase();
    elRightStageBadge.textContent = rightStageStr;
    elRightStageBadge.className = "stage-badge";
    if (right_stage === "UP") elRightStageBadge.classList.add("up");
    if (right_stage === "DOWN") elRightStageBadge.classList.add("down");

    // Display joint angle for both arms
    if (left_angle !== undefined && right_angle !== undefined) {
      elAngle.textContent = `L:${parseFloat(left_angle).toFixed(1)} R:${parseFloat(right_angle).toFixed(1)}`;
    } else {
      elAngle.textContent = "---";
    }

    // Keep overall total and summary correct
    elReps.textContent = counter;
    elSumReps.textContent = counter;
    lastRepCount = counter;
  } else {
    // Show central single ring, hide curl counters
    elMainRepContainer.style.display = "block";
    elStageBadge.style.display = "inline-block";
    elCurlContainer.style.display = "none";

    if (counter !== lastRepCount) {
      animateRepBump(elReps);
      showRepPopup("center");
      lastRepCount = counter;
    }
    elReps.textContent    = counter;
    elSumReps.textContent = counter;
    updateRing(counter);

    /* Stage badge */
    const stageStr = (stage || "---").toUpperCase();
    elStageBadge.textContent = stageStr;
    elStageBadge.className   = "stage-badge";
    if (stage === "UP")   elStageBadge.classList.add("up");
    if (stage === "DOWN") elStageBadge.classList.add("down");

    /* Angle */
    elAngle.textContent = angle ? `${parseFloat(angle).toFixed(1)}` : "---";
  }

  /* Calories */
  elCalories.textContent   = parseFloat(calories || 0).toFixed(2);
  elSumCals.textContent    = `${parseFloat(calories || 0).toFixed(2)} kcal`;

  /* FPS */
  elFPS.textContent = fps ? Math.round(fps) : "--";

  /* Posture */
  updatePosture(posture_ok, posture_warning);

  /* Voice Coach: posture warning */
  if (!posture_ok && lastPostureOk) {
    VoiceCoach.postureWarning(false);
  }
  lastPostureOk = posture_ok;

  /* Voice Coach: rep milestone check (total reps) */
  VoiceCoach.checkRepMilestone(counter);

  /* Form warning banner */
  updateFormWarning(form_warning);
}

/* ─── Helpers ────────────────────────────────── */
function updateRing(count) {
  const circumference = 314; // 2π×50
  const pct = Math.min(count / MAX_REPS, 1);
  elRing.style.strokeDashoffset = circumference * (1 - pct);
}

function animateRepBump(element = elReps) {
  element.classList.remove("bump");
  // Force reflow
  void element.offsetWidth;
  element.classList.add("bump");
  element.addEventListener("animationend", () => element.classList.remove("bump"), { once: true });
}

function updatePosture(ok, warning) {
  elPostureDot.className   = "posture-dot " + (ok ? "ok" : "bad");
  elPostureSt.className    = "posture-status " + (ok ? "ok" : "bad");
  elPostureSt.textContent  = ok ? "POSTURE OK" : "FIX POSTURE";
  elPostureW.textContent   = ok ? "" : (warning || "");
}

function updateFormWarning(msg) {
  if (msg) {
    elFormWarn.textContent = msg;
    elFormWarn.classList.add("visible");
  } else {
    elFormWarn.classList.remove("visible");
  }
}

/* ═══════════════════════════════════════════════
   MODE SWITCHING
═══════════════════════════════════════════════ */
function setMode(mode) {
  if (mode === currentMode) return;
  currentMode = mode;

  // Update button states
  modeBtns.forEach(btn => {
    const isActive = btn.dataset.mode === mode;
    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-pressed", isActive ? "true" : "false");
  });

  // Update tips + quote
  const cfg = EXERCISE_CONFIG[mode] || EXERCISE_CONFIG.curl;
  renderTips(cfg.tips);
  renderQuote(cfg.quotes);

  // Voice Coach: announce new mode
  VoiceCoach.announceMode(mode);

  // Tell backend
  fetch(`${BACKEND}/api/set_mode`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  }).catch(() => { /* swallow if offline */ });
}

modeBtns.forEach(btn => {
  btn.addEventListener("click", () => setMode(btn.dataset.mode));
});

/* ═══════════════════════════════════════════════
   RESET
═══════════════════════════════════════════════ */
btnReset.addEventListener("click", async () => {
  btnReset.disabled = true;
  try {
    await fetch(`${BACKEND}/api/reset`, { method: "POST" });
  } catch { /* swallow */ }
  lastRepCount = 0;
  lastLeftRepCount = 0;
  lastRightRepCount = 0;
  updateRing(0);
  elReps.textContent = "0";
  if (elLeftReps) elLeftReps.textContent = "0";
  if (elRightReps) elRightReps.textContent = "0";
  elCalories.textContent = "0.00";
  elSumReps.textContent  = "0";
  elSumCals.textContent  = "0.00 kcal";
  setTimeout(() => { btnReset.disabled = false; }, 600);
});

/* ═══════════════════════════════════════════════
   RECONNECT BUTTON
═══════════════════════════════════════════════ */
elReconnect.addEventListener("click", () => {
  elOverTxt.textContent = "RECONNECTING…";
  startFeed();
  fetchStatus();
});

/* ═══════════════════════════════════════════════
   TIPS & QUOTES
═══════════════════════════════════════════════ */
function renderTips(tips) {
  elTips.innerHTML = tips.map(t => `<li>${t}</li>`).join("");
}

function renderQuote(quotes) {
  quoteIdx = (quoteIdx + 1) % quotes.length;
  elQuote.textContent = quotes[quoteIdx];
}

/* Rotate quote every 12 s */
setInterval(() => {
  const cfg = EXERCISE_CONFIG[currentMode] || EXERCISE_CONFIG.curl;
  renderQuote(cfg.quotes);
}, 12_000);

/* ═══════════════════════════════════════════════
   SESSION TIMER
═══════════════════════════════════════════════ */
function fmtTime(ms) {
  const s   = Math.floor(ms / 1000);
  const m   = Math.floor(s / 60);
  const sec = s % 60;
  return `${String(m).padStart(2,"0")}:${String(sec).padStart(2,"0")}`;
}

sessionTimerID = setInterval(() => {
  elTimer.textContent = fmtTime(Date.now() - sessionStart);
}, 1000);

/* ═══════════════════════════════════════════════
   KHAO BODY BNAO (DIET GENERATION)
═══════════════════════════════════════════════ */
elGenerateDietBtn.addEventListener("click", async () => {
  const weight = parseFloat(elWeightInput.value);
  const goal   = elGoalSelect.value;
  
  if (isNaN(weight) || weight < 20 || weight > 250) {
    alert("Please enter a valid weight between 20 kg and 250 kg.");
    return;
  }
  
  elGenerateDietBtn.disabled = true;
  elGenerateDietBtn.textContent = "GENERATING PLAN...";
  
  try {
    const res = await fetch(`${BACKEND}/api/generate_diet`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ weight, goal })
    });
    
    const data = await res.json();
    if (res.ok && data.status === "success") {
      elRecProtein.textContent  = data.protein;
      elRecCalories.textContent = data.calories;
      elRecWater.textContent    = data.water;
      
      elMealBreakfast.textContent = data.diet.breakfast;
      elMealLunch.textContent     = data.diet.lunch;
      elMealSnack.textContent     = data.diet.evening;
      elMealDinner.textContent    = data.diet.dinner;
      
      // Reveal results card with smooth animation
      elDietResults.style.display = "block";
      elDietResults.scrollIntoView({ behavior: "smooth", block: "nearest" });
    } else {
      alert(data.error || "An error occurred while generating your diet plan.");
    }
  } catch (err) {
    alert("Could not connect to Flask server to generate plan. Please verify the backend is running.");
    console.error(err);
  } finally {
    elGenerateDietBtn.disabled = false;
    elGenerateDietBtn.textContent = "GENERATE DIET PLAN";
  }
});

/* ═══════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════ */
function init() {
  // Set initial tips
  const cfg = EXERCISE_CONFIG[currentMode];
  renderTips(cfg.tips);
  elQuote.textContent = cfg.quotes[0];

  // Start streaming + status poll
  startFeed();
  fetchStatus();     // immediate first check

  // Voice Coach welcome is now triggered when face/pose is first detected in video feed
}

init();