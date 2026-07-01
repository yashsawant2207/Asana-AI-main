# Asana AI — Python Pose Engine

FastAPI + MediaPipe + OpenCV backend that receives webcam frames over a
WebSocket and returns pose landmarks + real-time correction feedback.
The React frontend (in the repo root) renders the skeleton and feedback.

## 1. Download the model

```bash
wget -O models/pose_landmarker.task \
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task"
```

## 2. Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Point the frontend at it via `VITE_CV_BACKEND_WS_URL=ws://localhost:8000/ws`.

## 3. Deploy to Google Cloud Run

```bash
gcloud run deploy asana-pose-engine \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --cpu 2 --memory 2Gi --timeout 3600 --concurrency 4
```

Cloud Run supports WebSockets natively. Set the frontend env var to the
`wss://` URL Cloud Run returns. Tighten CORS `allow_origins` to your
frontend domain before going live.

## Architecture

```
frontend (React)  --JPEG frames-->  /ws  -->  PoseTracker (MediaPipe)
                  <--landmarks+feedback JSON--  rule engine (app/cv/rules.py)
```

## Structure

- `app/cv/geometry.py`  — angle & distance math
- `app/cv/landmarker.py` — MediaPipe wrapper (loaded once)
- `app/cv/rules.py`      — one evaluator per pose (from the Colab notebook)
- `app/cv/registry.py`   — pose id -> evaluator map (ids match the frontend)
- `app/main.py`          — FastAPI app + /ws + /health

## Future: Supabase

Keep Supabase off the per-frame hot path. Write session *summaries*
(e.g. "held Tree Pose 12s") after a session, not per frame.
