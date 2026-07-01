import type { Landmark } from "./pose-overlay";

const FULL_BODY_VISIBILITY_THRESHOLD = 0.6;
const FULL_BODY_LANDMARK_INDICES = [
  15, // left wrist
  16, // right wrist
  23, // left hip
  24, // right hip
  27, // left ankle
  28, // right ankle
] as const;

export function isFullBodyVisible(landmarks: Landmark[]): boolean {
  if (!landmarks || landmarks.length < 29) {
    return false;
  }

  return FULL_BODY_LANDMARK_INDICES.every((index) => {
    const visibility = landmarks[index]?.visibility;
    return typeof visibility === "number" && visibility >= FULL_BODY_VISIBILITY_THRESHOLD;
  });
}
