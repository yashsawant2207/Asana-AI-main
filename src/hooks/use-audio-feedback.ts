import { useEffect, useRef } from "react";

export function useAudioFeedback(
  audioMessages: string[] | undefined,
  activeMessages: string[] | undefined,
  enabled: boolean,
  language = "en-US",
) {
  const lastSpokenRef = useRef<string>("");
  const lastSpeakAtRef = useRef<number>(0);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const isSpeakingRef = useRef<boolean>(false);

  // Cancel speech synthesis when the component unmounts
  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // Cancel speech synthesis when voice guidance is disabled
  useEffect(() => {
    if (!enabled && typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      isSpeakingRef.current = false;
      utteranceRef.current = null;
      lastSpokenRef.current = "";
    }
  }, [enabled]);

  // Cancel speech synthesis when the user corrects their pose (no active errors)
  useEffect(() => {
    if (enabled && typeof window !== "undefined" && "speechSynthesis" in window) {
      const hasActiveErrors = activeMessages && activeMessages.length > 0;
      if (!hasActiveErrors && isSpeakingRef.current) {
        window.speechSynthesis.cancel();
        isSpeakingRef.current = false;
        utteranceRef.current = null;
        lastSpokenRef.current = "";
      }
    }
  }, [activeMessages, enabled]);

  useEffect(() => {
    if (!enabled || !audioMessages || audioMessages.length === 0) {
      return;
    }

    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }

    const text = audioMessages.join(". ");

    // 2. If we are currently speaking, let the current instruction finish.
    // This prevents rapid updates from cutting off the audio and causing one-word stutters.
    if (isSpeakingRef.current) {
      return;
    }

    // 3. Throttle speaking the exact same message to avoid annoying the user
    const now = Date.now();
    if (text === lastSpokenRef.current && now - lastSpeakAtRef.current < 6000) {
      return;
    }

    lastSpokenRef.current = text;
    lastSpeakAtRef.current = now;

    // Cancel any stray speech (should be none since isSpeakingRef is false)
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utteranceRef.current = utterance;
    utterance.lang = language;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => {
      isSpeakingRef.current = true;
    };

    utterance.onend = () => {
      if (utteranceRef.current === utterance) {
        isSpeakingRef.current = false;
        utteranceRef.current = null;
      }
    };

    utterance.onerror = () => {
      if (utteranceRef.current === utterance) {
        isSpeakingRef.current = false;
        utteranceRef.current = null;
      }
    };

    window.speechSynthesis.speak(utterance);
  }, [audioMessages, enabled, language]);
}



