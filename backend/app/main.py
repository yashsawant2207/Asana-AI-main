"""FastAPI server: streams webcam frames in, returns landmarks + feedback JSON.

Run locally:  uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import io
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

try:
    from app.audio import audio_engine
    has_audio = True
except ImportError:
    audio_engine = None
    has_audio = False
from app.cv.landmarker import PoseTracker
from app.cv.registry import evaluate

app = FastAPI(title="Asana AI Pose Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loaded once at startup; expensive to construct.
tracker = PoseTracker()
_executor = ThreadPoolExecutor(max_workers=1)

FULL_BODY_VISIBILITY_THRESHOLD = 0.5
FULL_BODY_VISIBILITY_INDICES = [15, 16, 23, 24, 27, 28]


def _detect(jpeg_bytes: bytes):
    return tracker.detect(jpeg_bytes)


def _is_full_body_visible(landmarks):
    if landmarks is None or len(landmarks) < max(FULL_BODY_VISIBILITY_INDICES) + 1:
        return False

    for index in FULL_BODY_VISIBILITY_INDICES:
        visibility = getattr(landmarks[index], "visibility", 0.0)
        if visibility is None or visibility < FULL_BODY_VISIBILITY_THRESHOLD:
            return False

    left_sh = landmarks[11]
    right_sh = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    left_knee = landmarks[25]
    right_knee = landmarks[26]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]

    if any(getattr(lm, "y", None) is None for lm in [
        left_sh,
        right_sh,
        left_hip,
        right_hip,
        left_knee,
        right_knee,
        left_ankle,
        right_ankle,
    ]):
        return False

    left_hip_top = min(left_hip.y, right_hip.y)
    right_hip_top = max(left_hip.y, right_hip.y)
    left_knee_low = max(left_knee.y, right_knee.y)
    left_ankle_low = max(left_ankle.y, right_ankle.y)
    shoulder_top = min(left_sh.y, right_sh.y)

    if left_ankle.y <= left_hip.y + 0.08 or right_ankle.y <= right_hip.y + 0.08:
        return False

    if left_hip_top - shoulder_top < 0.05:
        return False

    if left_knee_low <= left_hip_top + 0.06:
        return False

    if left_ankle_low < 0.68:
        return False

    if left_ankle_low - shoulder_top < 0.38:
        return False

    ankle_visible_low = any(
        getattr(landmarks[i], "visibility", 0.0) >= FULL_BODY_VISIBILITY_THRESHOLD and landmarks[i].y >= 0.68
        for i in (27, 28)
    )
    if not ankle_visible_low:
        return False

    return True


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/audio")
def get_audio(
    text: str,
    language: str = "en-US",
    voice: str = "",
    speed: float = 1.0,
):
    """Generate a short spoken audio clip from text using the Kokor0-v1.0 backend."""
    if not has_audio or audio_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Audio backend is not available (torch or kokoro is missing)."
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="The text query parameter cannot be empty.")

    try:
        # Note: in app/audio.py, the method is named `synthesize`
        wav_bytes = audio_engine.synthesize(text, language=language, voice=voice or None, speed=speed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return StreamingResponse(io.BytesIO(wav_bytes), media_type="audio/wav")


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    pose_id = "tree"
    latest_frame: bytes | None = None
    processing = False
    loop = asyncio.get_running_loop()

    # Stateful variables for message debouncing & cooldown
    import time
    prev_msgs = set()
    prev_was_correct = False
    msg_cooldowns = {}

    async def process_latest():
        nonlocal latest_frame, processing, pose_id, prev_msgs, prev_was_correct, msg_cooldowns
        if processing:
            return
        processing = True
        try:
            while latest_frame is not None:
                data = latest_frame
                latest_frame = None
                landmarks, w, h = await loop.run_in_executor(_executor, _detect, data)
                # A newer frame arrived while we were processing — skip stale result.
                if latest_frame is not None:
                    continue
                if landmarks is None or not _is_full_body_visible(landmarks):
                    prev_msgs.clear()
                    prev_was_correct = False
                    await websocket.send_json(
                        {"detected": False, "landmarks": [], "is_correct": False, "feedback_msgs": [], "audio_msgs": []}
                    )
                    continue

                is_correct, msgs = evaluate(pose_id, landmarks, w, h)

                audio_msgs = []
                now = time.time()
                if is_correct:
                    if not prev_was_correct:
                        audio_msgs.append("Perfect alignment!")
                        prev_was_correct = True
                    prev_msgs.clear()
                else:
                    prev_was_correct = False
                    for msg in msgs:
                        is_new_error = msg not in prev_msgs
                        cooldown_expired = (now - msg_cooldowns.get(msg, 0.0)) >= 8.0
                        if is_new_error or cooldown_expired:
                            audio_msgs.append(msg)
                            msg_cooldowns[msg] = now
                    prev_msgs = set(msgs)

                await websocket.send_json(
                    {
                        "detected": True,
                        "landmarks": [
                            {"x": p.x, "y": p.y, "visibility": getattr(p, "visibility", 1.0)}
                            for p in landmarks
                        ],
                        "is_correct": is_correct,
                        "feedback_msgs": msgs,
                        "audio_msgs": audio_msgs,
                    }
                )
        finally:
            processing = False
            if latest_frame is not None:
                asyncio.create_task(process_latest())

    try:
        while True:
            message = await websocket.receive()
            if "text" in message and message["text"] is not None:
                try:
                    cfg = json.loads(message["text"])
                    if cfg.get("type") == "config" and cfg.get("pose"):
                        pose_id = cfg["pose"]
                except json.JSONDecodeError:
                    pass
                continue

            data = message.get("bytes")
            if not data:
                continue

            latest_frame = data
            await process_latest()
    except WebSocketDisconnect:
        return
