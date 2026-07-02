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

---

## 🛠️ Technology & Project Structure

### Backend Layout
- `backend/app/main.py` — WebSockets connections router, health checks, and stateful debouncing triggers.
- `backend/app/cv/landmarker.py` — MediaPipe Pose landmarker model loader.
- `backend/app/cv/rules.py` — Angle, distance, and joint alignment math rules for yoga poses.
- `backend/app/cv/registry.py` — Pose ID to rule mapping handler.

### Frontend Layout
- `src/routes/` — Application pages and routing configuration (`index.tsx`, `poses.tsx`, `practice.tsx`).
- `src/hooks/use-audio-feedback.ts` — Intelligent browser SpeechSynthesis manager.
- `src/hooks/use-pose-socket.ts` — Handles WebSocket frames ingestion and state propagation.
- `src/lib/poses.ts` — Yoga poses data specifications, benefits checklist, and asset maps.
