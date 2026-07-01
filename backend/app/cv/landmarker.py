"""Wraps the MediaPipe PoseLandmarker. Created once and reused per frame."""
import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = os.environ.get("POSE_MODEL_PATH", "models/pose_landmarker_lite.task")


class PoseTracker:
    def __init__(self, model_path: str = MODEL_PATH):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def detect(self, jpeg_bytes: bytes):
        """Return (landmarks, width, height) or (None, w, h)."""
        arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return None, 0, 0
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)
        if result.pose_landmarks and len(result.pose_landmarks) > 0:
            return result.pose_landmarks[0], w, h
        return None, w, h
