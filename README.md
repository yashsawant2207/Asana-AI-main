# Asana AI — Real-Time Yoga Pose Coach

Asana AI is a premium, real-time yoga posture coaching application. By combining a **React (Vite) frontend** with a **FastAPI (MediaPipe) python pose-tracking engine**, it analyzes live webcam frames over WebSockets to overlay coordinates and provide verbal/visual alignment adjustments as you practice.

---

## 🌟 Key Features

- **Live Skeleton Overlay**: Renders real-time MediaPipe pose landmarks and lines directly over the webcam feed.
- **State-Based Voice Guidance**: Natural browser-native text-to-speech feedback that debounces coordinate noise, prevents voice stuttering, and silences itself immediately upon correct posture alignment.
- **Dynamic body detection**: Enhanced visibility tolerance boundaries so that minor movements, lighting shifts, or compact spaces do not prematurely trigger "Please step back" errors.
- **Milestone Cues**: Audio milestones (e.g. `"Perfect alignment!"`) to motivate and guide you when a pose is successfully held.
- **Pose Library**: A beautiful catalog of 12 classic asanas complete with Sanskrit names, muscle focuses, alignment checklist items, and fully aligned visual illustrations.

---

## 🏗️ Architecture

```
                    ┌────────────────────────┐
                    │    Frontend (React)    │
                    │   Vite + TS + Tailwind │
                    └─────┬────────────▲─────┘
                          │            │
                  Webcam  │            │  Landmarks, Error Cues
                  Frames  │            │  & Speech Triggers
                 (Binary) │            │  (JSON)
                          ▼            │
                    ┌──────────────────┴─────┐
                    │    Backend (FastAPI)   │
                    │  Python + MediaPipe    │
                    └────────────────────────┘
```

- **Frontend**: [Vite](https://vitejs.dev/) + React 19 + TypeScript + TailwindCSS + TanStack Router. Runs on `http://localhost:5173`.
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + MediaPipe + OpenCV-Python (headless). Runs on `http://localhost:8000` (WebSocket endpoint at `/ws`).

---

## 📂 Directory Structure & File Working

Below is the file tree of the workspace, followed by a detailed description of what each file does.

```
asana-ai/
├── backend/                       # Python FastAPI Pose Engine
│   ├── app/
│   │   ├── cv/
│   │   │   ├── geometry.py        # Trig math helper (angles, distances)
│   │   │   ├── landmarker.py      # MediaPipe model wrapper
│   │   │   ├── registry.py        # Maps pose ID to evaluator rules
│   │   │   └── rules.py           # Angle constraints for all 12 yoga poses
│   │   ├── audio.py               # Optional Kokoro audio TTS engine
│   │   └── main.py                # FastAPI server, WebSockets loop & debouncer
│   ├── models/
│   │   ├── pose_landmarker.task        # MediaPipe ML model file (heavy)
│   │   └── pose_landmarker_lite.task   # MediaPipe ML model file (lite)
│   ├── Dockerfile                 # Container image specification
│   ├── requirements.txt           # Python dependency specifications
│   └── README.md                  # Backend local docs
│
├── public/                        # Static static assets
│   ├── assets/
│   │   └── yoga-poses/            # Cleaned, un-cropped asana PNG images
│   ├── favicon.ico                # Site icon
│   └── robots.txt                 # Search engine crawling rules
│
├── src/                           # Frontend React Web App
│   ├── components/
│   │   └── ui/
│   │       └── button.tsx         # Custom Shadcn Button component
│   ├── hooks/
│   │   ├── use-audio-feedback.ts  # Intelligent state-based TTS speaker
│   │   ├── use-mobile.tsx         # Mobile viewport detector
│   │   └── use-pose-socket.ts     # Handles frames ingestion & state syncing
│   ├── lib/
│   │   ├── pose-overlay.ts        # Canvas overlays & skeleton lines drawer
│   │   ├── poses.ts               # Pose catalog specification metadata
│   │   └── utils.ts               # CSS classes merger helper
│   ├── routes/
│   │   ├── __root.tsx             # Root page shell (headers, navigation, footer)
│   │   ├── index.tsx              # Landing page (hero callouts & features)
│   │   ├── poses.tsx              # Library grid with all 12 pose cards
│   │   └── practice.tsx           # Webcam, skeleton stream, and coaching UI
│   ├── main.tsx                   # Frontend entry point (loads router and CSS)
│   ├── routeTree.gen.ts           # Auto-generated TanStack routes mapping
│   └── styles.css                 # Global CSS sheets & Tailwind theme configurations
│
├── tsconfig.json                  # TypeScript compiler settings
├── vite.config.ts                 # Vite bundler configs & Router plugins
├── package.json                   # Frontend script & packages definitions
└── README.md                      # This main documentation file
```

---

### 🐍 Backend File Working

#### 📄 `backend/app/main.py`
The FastAPI application root. It sets up CORS headers and exposes the `/ws` WebSocket endpoint. It streams JPEG frames from the camera, runs the MediaPipe detector, passes landmarks to the rule engine, implements stateful voice feedback debouncing (8-second cooldowns), and dispatches final coordinates and cues back to the browser.

#### 📄 `backend/app/cv/landmarker.py`
A wrapper around the MediaPipe Pose Landmarker package. It loads the compiled `.task` machine learning model once at startup and evaluates individual frames, converting OpenCV image arrays into 33 coordinate pose landmarks.

#### 📄 `backend/app/cv/geometry.py`
Implements the geometric math utilities. It calculates the distances between joints in 3D coordinate space and the exact 2D/3D angles formed by three joint coordinates (e.g. ankle-knee-hip).

#### 📄 `backend/app/cv/rules.py`
The core business logic rules for all 12 yoga poses. For each pose (e.g., Tree, Warrior I, Cobra), it checks if specified angles match the ideal pose definition. If an angle fails, it generates a human-readable adjustment message (e.g. `"Bend your front knee deeper"`).

#### 📄 `backend/app/cv/registry.py`
Serves as the central dispatcher mapping the string `pose_id` received from the React app (such as `"warrior_ii"`) to the correct evaluator function in `rules.py`.

#### 📄 `backend/app/audio.py`
An optional TTS audio generator endpoint backend using the Kokoro model. If Python's `torch` library is installed, it compiles text inputs into high-quality WAV speech bytes.

---

### ⚛️ Frontend File Working

#### 📄 `src/main.tsx`
The primary React entry point. It sets up index configurations, mounts fonts, imports global CSS styles, and initializes TanStack Router.

#### 📄 `src/styles.css`
Contains custom global styling rules, Tailwind directives, custom glassmorphism overlays, and variables for responsive layout styling.

#### 📄 `src/hooks/use-audio-feedback.ts`
Intelligent, stateful TTS manager. It coordinates the browser's native `SpeechSynthesis` API. It checks `isSpeakingRef` to prevent incoming frame updates from cutting off the active speaker (eliminating stutters), triggers `"Perfect alignment!"` exactly once when a pose is corrected, and silences instructions immediately when the user has no remaining errors.

#### 📄 `src/hooks/use-pose-socket.ts`
Manages the live WebSocket channel connecting to the python backend. It handles connecting, connection drops (automatic retries), sending raw JPEG image blobs, and updating React states with the returned coordinates and feedback strings.

#### 📄 `src/hooks/use-mobile.tsx`
Utility listener hook that tracks screen width changes, setting state flags if the current window matches the mobile breakpoint (<768px).

#### 📄 `src/lib/poses.ts`
Stores static configurations, Sanskirt translations, target focus categories, description texts, and illustration image paths for the 12 poses.

#### 📄 `src/lib/pose-overlay.ts`
Draws visual overlays on the HTML5 `<canvas>`. It connects coordinates returned by the backend with color-coded lines representing the skeletal structure (green for correct posture alignment, orange for errors).

#### 📄 `src/routes/__root.tsx`
Defines the main navigation layout header, main content layout wrapper, visual styling themes, and footer components.

#### 📄 `src/routes/index.tsx`
Renders the homepage. Includes beautiful visual sections, key features grids, and hero CTA buttons to direct users to start practicing.

#### 📄 `src/routes/poses.tsx`
Renders the Pose Library. It displays illustration cards with un-cropped, padded figures, Sanskrit translations, description tags, and alignment checklist rules.

#### 📄 `src/routes/practice.tsx`
The practice page. Manages camera state requests (`getUserMedia`), mounts the video element, binds requestAnimationFrame frame-sending loops, renders the canvas, displays correction cues, and handles voice toggle switches.

---

## 🚀 Setup & Execution

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (3.10 - 3.12)

---

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   * **Windows**:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   * **Unix / macOS**:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download the MediaPipe model file if not present:
   The model should be saved under `backend/models/pose_landmarker.task`.
5. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

### 2. Frontend Setup

1. Navigate to the root directory (where `package.json` is located):
   ```bash
   cd ..
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173` to start practicing!
