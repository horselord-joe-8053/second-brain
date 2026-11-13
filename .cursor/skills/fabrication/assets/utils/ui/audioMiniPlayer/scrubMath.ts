/** Clamp seek ratio to [0, 1] for range input and pointer scrubbing. */
export function clampScrubRatio(ratio: number): number {
  if (!Number.isFinite(ratio)) return 0;
  return Math.min(1, Math.max(0, ratio));
}

/** Map elapsed seconds to scrub ratio; returns 0 when duration unknown. */
export function scrubRatioFromTime(currentSec: number, durationSec: number): number {
  if (!Number.isFinite(durationSec) || durationSec <= 0) return 0;
  return clampScrubRatio(currentSec / durationSec);
}

/** Map scrub ratio to target seconds, clamped to duration when known. */
export function scrubTimeFromRatio(ratio: number, durationSec: number): number {
  const clamped = clampScrubRatio(ratio);
  if (!Number.isFinite(durationSec) || durationSec <= 0) return 0;
  return clamped * durationSec;
}

/** True when playback reached the end (for replay vs resume). */
export function isAtEnd(currentSec: number, durationSec: number, epsilonSec = 0.25): boolean {
  if (!Number.isFinite(durationSec) || durationSec <= 0) return false;
  return currentSec >= durationSec - epsilonSec;
}
