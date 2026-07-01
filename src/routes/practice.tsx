import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { CheckCircle2, CircleDashed, Play, Square, Wifi, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { POSES, getPose } from "@/lib/poses";
import { usePoseSocket } from "@/hooks/use-pose-socket";
import { drawPose, clearCanvas } from "@/lib/pose-overlay";

export const Route = createFileRoute("/practice")({
  validateSearch: (search: Record<string, unknown>): { pose?: string } => ({
    pose: typeof search.pose === "string" ? search.pose : undefined,
  }),
  head: () => ({
    meta: [
      { title: "Practice — Asana AI" },
      {
        name: "description",
        content: "Live yoga practice with real-time posture feedback from a Python pose-tracking engine.",
      },
    ],
  }),
  component: PracticePage,
});

function PracticePage() {
  const { pose: initialPose } = Route.useSearch();
  const [poseId, setPoseId] = useState(
    initialPose && getPose(initialPose) ? initialPose : POSES[0].id,
  );
  const [running, setRunning] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [holdSeconds, setHoldSeconds] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const captureCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number | null>(null);
  const lastSendRef = useRef(0);
  const encodingRef = useRef(false);
  const holdStartRef = useRef<number | null>(null);

  const { status, feedback, connect, disconnect, sendFrame, wsUrl } = usePoseSocket(poseId);
  const pose = getPose(poseId)!;

  // Track how long the pose has been held correctly.
  useEffect(() => {
    if (feedback?.isCorrect) {
      if (holdStartRef.current == null) holdStartRef.current = Date.now();
    } else {
      holdStartRef.current = null;
      setHoldSeconds(0);
    }
  }, [feedback?.isCorrect]);

  useEffect(() => {
    if (!feedback?.isCorrect) return;
    const id = setInterval(() => {
      if (holdStartRef.current != null) {
        setHoldSeconds(Math.floor((Date.now() - holdStartRef.current) / 1000));
      }
    }, 500);
    return () => clearInterval(id);
  }, [feedback?.isCorrect]);

  // Draw overlay whenever feedback updates.
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!ctx || !canvas) return;
    if (feedback && feedback.landmarks.length > 0) {
      drawPose(ctx, feedback.landmarks, { isCorrect: feedback.isCorrect });
    } else {
      clearCanvas(ctx);
    }
  }, [feedback]);

  const captureLoop = useCallback(() => {
    const video = videoRef.current;
    if (video && video.readyState >= 2 && !encodingRef.current) {
      const now = performance.now();
      if (now - lastSendRef.current > 200) {
        let cc = captureCanvasRef.current;
        if (!cc) {
          cc = document.createElement("canvas");
          captureCanvasRef.current = cc;
        }
        cc.width = 320;
        cc.height = Math.round((video.videoHeight / video.videoWidth) * 320) || 240;
        const cctx = cc.getContext("2d");
        if (cctx) {
          encodingRef.current = true;
          cctx.drawImage(video, 0, 0, cc.width, cc.height);
          cc.toBlob(
            (blob) => {
              encodingRef.current = false;
              if (blob) {
                lastSendRef.current = performance.now();
                sendFrame(blob);
              }
            },
            "image/jpeg",
            0.55,
          );
        }
      }
    }
    rafRef.current = requestAnimationFrame(captureLoop);
  }, [sendFrame]);

  const stop = useCallback(() => {
    setRunning(false);
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    disconnect();
    const ctx = canvasRef.current?.getContext("2d");
    if (ctx) clearCanvas(ctx);
  }, [disconnect]);

  const start = useCallback(async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      connect();
      setRunning(true);
      lastSendRef.current = 0;
      rafRef.current = requestAnimationFrame(captureLoop);
    } catch {
      setCameraError("We couldn't access your camera. Please allow camera permission and try again.");
    }
  }, [connect, captureLoop]);

  useEffect(() => () => stop(), [stop]);

  return (
    <div className="mx-auto max-w-6xl px-5 py-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Practice</h1>
          <p className="mt-1 text-muted-foreground">
            Now practicing <span className="font-medium text-foreground">{pose.name}</span> · {pose.sanskrit}
          </p>
        </div>
        <ConnectionBadge status={status} wsUrl={wsUrl} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <div className="relative overflow-hidden rounded-2xl border border-border/60 bg-foreground/95 shadow-sm">
          <div className="relative aspect-[4/3] w-full">
            <video
              ref={videoRef}
              className="absolute inset-0 h-full w-full -scale-x-100 object-cover"
              playsInline
              muted
            />
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              className="absolute inset-0 h-full w-full"
            />
            {!running && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-foreground/70 text-center text-background">
                <p className="max-w-xs px-6 text-sm text-background/80">
                  {cameraError ?? "Press start to turn on your camera and begin the session."}
                </p>
                <Button onClick={start} size="lg">
                  <Play className="h-4 w-4" /> Start session
                </Button>
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-5">
          <div>
            <label className="text-sm font-medium text-foreground">Choose a pose</label>
            <select
              value={poseId}
              onChange={(e) => setPoseId(e.target.value)}
              className="mt-2 w-full rounded-lg border border-input bg-card px-3 py-2 text-sm text-foreground shadow-sm focus:outline-none focus:ring-1 focus:ring-ring"
            >
              {POSES.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} — {p.sanskrit}
                </option>
              ))}
            </select>
          </div>

          <div className="overflow-hidden rounded-3xl bg-muted">
            <img
              src={pose.image}
              alt={`Preview of ${pose.name}`}
              className="h-48 w-full object-cover object-center"
            />
          </div>

          <FeedbackPanel
            running={running}
            connected={status === "connected"}
            feedback={feedback}
            holdSeconds={holdSeconds}
            cues={pose.cues}
          />

          {running && (
            <Button variant="outline" onClick={stop}>
              <Square className="h-4 w-4" /> End session
            </Button>
          )}

          {status === "offline" && running && (
            <p className="rounded-lg bg-warning/15 px-3 py-2 text-xs text-warning-foreground">
              Can't reach the pose engine at <code>{wsUrl}</code>. Make sure the Python backend is
              running, then it will reconnect automatically.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function ConnectionBadge({ status, wsUrl }: { status: string; wsUrl: string }) {
  const map: Record<string, { label: string; className: string; icon: typeof Wifi }> = {
    idle: { label: "Not started", className: "bg-muted text-muted-foreground", icon: WifiOff },
    connecting: { label: "Connecting…", className: "bg-warning/20 text-warning", icon: CircleDashed },
    connected: { label: "Engine connected", className: "bg-success/15 text-success", icon: Wifi },
    offline: { label: "Engine offline", className: "bg-destructive/15 text-destructive", icon: WifiOff },
  };
  const s = map[status] ?? map.idle;
  return (
    <span
      title={wsUrl}
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium ${s.className}`}
    >
      <s.icon className="h-3.5 w-3.5" /> {s.label}
    </span>
  );
}

function FeedbackPanel({
  running,
  connected,
  feedback,
  holdSeconds,
  cues,
}: {
  running: boolean;
  connected: boolean;
  feedback: ReturnType<typeof usePoseSocket>["feedback"];
  holdSeconds: number;
  cues: string[];
}) {
  if (!running) {
    return (
      <div className="rounded-2xl border border-border/60 bg-card p-5 text-sm text-muted-foreground shadow-sm">
        <p className="font-medium text-foreground">What the coach checks</p>
        <ul className="mt-3 space-y-2">
          {cues.map((cue) => (
            <li key={cue} className="flex gap-2">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
              {cue}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (!connected || !feedback) {
    return (
      <div className="rounded-2xl border border-border/60 bg-card p-5 text-sm text-muted-foreground shadow-sm">
        Waiting for the pose engine…
      </div>
    );
  }

  if (!feedback.detected) {
    return (
      <div className="rounded-2xl border border-border/60 bg-card p-5 text-sm text-muted-foreground shadow-sm">
        Please step back. Your entire body must be visible to start checking the pose.
      </div>
    );
  }

  if (feedback.isCorrect) {
    return (
      <div className="rounded-2xl border border-success/40 bg-success/10 p-5 shadow-sm">
        <div className="flex items-center gap-2 text-success">
          <CheckCircle2 className="h-5 w-5" />
          <span className="text-lg font-semibold">Perfect alignment!</span>
        </div>
        <p className="mt-2 text-sm text-foreground">
          Held for <span className="font-semibold">{holdSeconds}s</span> — keep breathing.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-warning/40 bg-warning/10 p-5 shadow-sm">
      <p className="text-lg font-semibold text-warning-foreground">Adjust your pose</p>
      <ul className="mt-3 space-y-2">
        {feedback.messages.map((msg) => (
          <li key={msg} className="flex gap-2 text-sm text-foreground">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-warning" />
            {msg}
          </li>
        ))}
      </ul>
    </div>
  );
}