import { useEffect, useRef } from "react";

export function useAudioFeedback(
  messages: string[] | undefined,
  enabled: boolean,
  language = "en-US",
) {
  const lastSpokenRef = useRef<string>("");
  const lastSpeakAtRef = useRef<number>(0);

  useEffect(() => {
    if (!enabled || !messages || messages.length === 0) {
      return;
    }

    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      return;
    }

    const text = messages.join(". ");
    const now = Date.now();

    if (text === lastSpokenRef.current && now - lastSpeakAtRef.current < 5000) {
      return;
    }

    lastSpokenRef.current = text;
    lastSpeakAtRef.current = now;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language;
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;
    window.speechSynthesis.speak(utterance);

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [messages, enabled, language]);
}
