// Normalized landmark coordinates (0..1) as returned by the Python backend.
export type Landmark = { x: number; y: number; visibility?: number };

// MediaPipe Pose connection pairs (33-landmark topology). Kept in the client
// so we only ship coordinates over the wire, not rendered video.
export const POSE_CONNECTIONS: [number, number][] = [
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
  [11, 23], [12, 24], [23, 24],
  [23, 25], [25, 27], [27, 29], [29, 31], [27, 31],
  [24, 26], [26, 28], [28, 30], [30, 32], [28, 32],
];

interface DrawOptions {
  isCorrect: boolean;
  mirror?: boolean;
}

export function drawPose(
  ctx: CanvasRenderingContext2D,
  landmarks: Landmark[],
  { isCorrect, mirror = true }: DrawOptions,
) {
  const { width, height } = ctx.canvas;
  ctx.clearRect(0, 0, width, height);
  if (!landmarks || landmarks.length === 0) return;

  const toX = (x: number) => (mirror ? (1 - x) * width : x * width);
  const toY = (y: number) => y * height;

  const boneColor = isCorrect
    ? "oklch(0.7 0.14 150)"
    : "oklch(0.72 0.14 65)";
  const jointColor = isCorrect
    ? "oklch(0.62 0.15 150)"
    : "oklch(0.68 0.18 45)";

  // Bones
  ctx.lineWidth = Math.max(3, width * 0.006);
  ctx.strokeStyle = boneColor;
  ctx.lineCap = "round";
  for (const [a, b] of POSE_CONNECTIONS) {
    const la = landmarks[a];
    const lb = landmarks[b];
    if (!la || !lb) continue;
    if ((la.visibility ?? 1) < 0.3 || (lb.visibility ?? 1) < 0.3) continue;
    ctx.beginPath();
    ctx.moveTo(toX(la.x), toY(la.y));
    ctx.lineTo(toX(lb.x), toY(lb.y));
    ctx.stroke();
  }

  // Joints
  const r = Math.max(4, width * 0.008);
  ctx.fillStyle = jointColor;
  const tracked = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28];
  for (const idx of tracked) {
    const lm = landmarks[idx];
    if (!lm || (lm.visibility ?? 1) < 0.3) continue;
    ctx.beginPath();
    ctx.arc(toX(lm.x), toY(lm.y), r, 0, Math.PI * 2);
    ctx.fill();
  }
}

export function clearCanvas(ctx: CanvasRenderingContext2D) {
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
}