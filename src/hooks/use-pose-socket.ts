import { useCallback, useEffect, useRef, useState } from "react";
import type { Landmark } from "@/lib/pose-overlay";

export type SocketStatus = "idle" | "connecting" | "connected" | "offline";

export interface PoseFeedback {
  landmarks: Landmark[];
  isCorrect: boolean;
  messages: string[];
  audioMessages: string[];
  detected: boolean;
}

const WS_URL =
  (import.meta.env.VITE_CV_BACKEND_WS_URL as string | undefined) ??
  "ws://localhost:8000/ws";

interface BackendMessage {
  landmarks?: Landmark[];
  is_correct?: boolean;
  feedback_msgs?: string[];
  audio_msgs?: string[];
  detected?: boolean;
}

export function usePoseSocket(poseId: string) {
  const [status, setStatus] = useState<SocketStatus>("idle");
  const [feedback, setFeedback] = useState<PoseFeedback | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const poseRef = useRef(poseId);
  const wantOpenRef = useRef(false);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  poseRef.current = poseId;

  const sendConfig = useCallback(() => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "config", pose: poseRef.current }));
    }
  }, []);

  // Re-send config whenever the selected pose changes mid-session.
  useEffect(() => {
    sendConfig();
  }, [poseId, sendConfig]);

  const openSocket = useCallback(() => {
    if (wsRef.current) return;
    setStatus("connecting");
    let ws: WebSocket;
    try {
      ws = new WebSocket(WS_URL);
    } catch {
      setStatus("offline");
      return;
    }
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("connected");
      sendConfig();
    };
    ws.onmessage = (event) => {
      try {
        const data: BackendMessage = JSON.parse(event.data);
        setFeedback({
          landmarks: data.landmarks ?? [],
          isCorrect: Boolean(data.is_correct),
          messages: data.feedback_msgs ?? [],
          audioMessages: data.audio_msgs ?? [],
          detected: data.detected ?? (data.landmarks?.length ?? 0) > 0,
        });
      } catch {
        /* ignore malformed frames */
      }
    };
    ws.onerror = () => {
      setStatus("offline");
    };
    ws.onclose = () => {
      wsRef.current = null;
      setStatus("offline");
      if (wantOpenRef.current) {
        reconnectRef.current = setTimeout(openSocket, 2500);
      }
    };
  }, [sendConfig]);

  const connect = useCallback(() => {
    wantOpenRef.current = true;
    openSocket();
  }, [openSocket]);

  const disconnect = useCallback(() => {
    wantOpenRef.current = false;
    if (reconnectRef.current) clearTimeout(reconnectRef.current);
    wsRef.current?.close();
    wsRef.current = null;
    setStatus("idle");
    setFeedback(null);
  }, []);

  const sendFrame = useCallback((blob: Blob) => {
    const ws = wsRef.current;
    // Drop frames when the socket is backed up so feedback stays near real-time.
    if (ws && ws.readyState === WebSocket.OPEN && ws.bufferedAmount === 0) {
      ws.send(blob);
    }
  }, []);

  useEffect(() => {
    return () => {
      wantOpenRef.current = false;
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, []);

  return { status, feedback, connect, disconnect, sendFrame, wsUrl: WS_URL };
}