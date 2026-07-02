import io
import logging
import os
import wave
from typing import Dict, Optional

import torch
from fastapi import HTTPException
from kokoro.model import KModel
from kokoro.pipeline import KPipeline

AUDIO_MODEL_NAME = os.environ.get("AUDIO_MODEL_NAME", "Kokor0-v1.0")
AUDIO_MODEL_PATH = os.environ.get("AUDIO_MODEL_PATH", "")
AUDIO_DEVICE = os.environ.get("AUDIO_DEVICE", "")

logger = logging.getLogger(__name__)

MODEL_SPEC: Dict[str, tuple[str, str]] = {
    "Kokor0-v1.0": ("hexgrad/Kokoro-82M", "kokoro-v1_0.pth"),
    "Kokoro-v1.0": ("hexgrad/Kokoro-82M", "kokoro-v1_0.pth"),
    "Kokor0-v1.1-zh": ("hexgrad/Kokoro-82M-v1.1-zh", "kokoro-v1_1-zh.pth"),
    "Kokoro-v1.1-zh": ("hexgrad/Kokoro-82M-v1.1-zh", "kokoro-v1_1-zh.pth"),
}

DEFAULT_VOICE_BY_LANG: Dict[str, str] = {
    "en-us": "a_heart",
    "en-gb": "b_heart",
    "es": "e_heart",
    "fr-fr": "f_heart",
    "hi": "h_heart",
    "it": "i_heart",
    "pt-br": "p_heart",
    "ja": "j_heart",
    "zh": "z_heart",
}


def _normalize_lang(lang: str) -> str:
    return lang.strip().lower().replace("_", "-")


def _default_voice(lang: str) -> str:
    return DEFAULT_VOICE_BY_LANG.get(lang, "a_heart")


class AudioEngine:
    def __init__(self, model_name: str = AUDIO_MODEL_NAME, model_path: str = AUDIO_MODEL_PATH):
        self.model_name = model_name
        self.model_path = model_path
        self.model: Optional[KModel] = None
        self.pipelines: Dict[str, KPipeline] = {}
        self.ready = False
        self._initialize()

    @property
    def device(self) -> str:
        if AUDIO_DEVICE:
            return AUDIO_DEVICE
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _resolve_model_paths(self) -> tuple[str, str, str]:
        if self.model_name not in MODEL_SPEC:
            raise RuntimeError(f"Unsupported audio model '{self.model_name}'.")

        repo_id, model_filename = MODEL_SPEC[self.model_name]
        config_path = None
        model_path = None

        if os.path.isdir(self.model_path):
            config_path = os.path.join(self.model_path, "config.json")
            model_path = os.path.join(self.model_path, model_filename)
        elif self.model_path.endswith(".json"):
            config_path = self.model_path
            model_path = os.path.join(os.path.dirname(self.model_path), model_filename)
        elif self.model_path.endswith(".pth"):
            config_path = os.path.join(os.path.dirname(self.model_path), "config.json")
            model_path = self.model_path
        else:
            raise RuntimeError(
                "AUDIO_MODEL_PATH must point to a Kokoro model directory, config.json, or .pth file."
            )

        if not os.path.exists(config_path) or not os.path.exists(model_path):
            raise RuntimeError(
                f"Kokoro model files not found. Expected config at {config_path} and model at {model_path}."
            )

        return repo_id, config_path, model_path

    def _initialize(self):
        if self.model_name not in MODEL_SPEC:
            logger.warning("Unsupported audio model '%s'.", self.model_name)
            return

        repo_id, _ = MODEL_SPEC[self.model_name]

        if self.model_path:
            try:
                repo_id, config_path, model_path = self._resolve_model_paths()
                self.model = KModel(repo_id=repo_id, config=config_path, model=model_path).to(self.device).eval()
            except Exception as exc:
                logger.error("Failed to initialize Kokoro from AUDIO_MODEL_PATH: %s", exc)
                return
        else:
            logger.info(
                "AUDIO_MODEL_PATH is not set; Kokoro will download model files from Hugging Face."
            )
            try:
                self.model = KModel(repo_id=repo_id).to(self.device).eval()
            except Exception as exc:
                logger.error("Failed to initialize Kokoro from Hugging Face: %s", exc)
                return

        self.ready = True
        logger.info(
            "Audio engine initialized for model %s on device %s",
            self.model_name,
            self.device,
        )

    def _get_pipeline(self, language: str) -> KPipeline:
        normalized = _normalize_lang(language)
        if normalized in self.pipelines:
            return self.pipelines[normalized]

        pipeline = KPipeline(lang_code=normalized, model=self.model)
        self.pipelines[normalized] = pipeline
        return pipeline

    def synthesize(
        self,
        text: str,
        language: str = "en-US",
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        if not self.ready or self.model is None:
            raise RuntimeError(
                "Audio backend is not configured. Set AUDIO_MODEL_PATH to your Kokoro model path or verify the model installation."
            )

        if not text.strip():
            raise ValueError("Text is required to generate audio.")

        normalized = _normalize_lang(language)
        voice = voice or _default_voice(normalized)
        pipeline = self._get_pipeline(normalized)

        results = list(pipeline(text, voice=voice, speed=speed, model=self.model))
        audio_segments = [result.audio for result in results if result.audio is not None]
        if not audio_segments:
            raise RuntimeError("Kokoro did not produce any audio output.")

        audio = torch.cat(audio_segments, dim=0) if len(audio_segments) > 1 else audio_segments[0]
        return self._to_wav_bytes(audio)

    def _to_wav_bytes(self, audio: torch.Tensor) -> bytes:
        audio = audio.cpu().numpy()
        if audio.ndim > 1:
            audio = audio.squeeze()

        clipped = audio.clip(-1.0, 1.0)
        samples = (clipped * 32767).astype("int16")

        with io.BytesIO() as buffer:
            with wave.open(buffer, mode="wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(samples.tobytes())
            return buffer.getvalue()


audio_engine = AudioEngine()
