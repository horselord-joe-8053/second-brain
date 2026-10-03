/** Format seconds as `m:ss` for mini-player elapsed/total labels. */
export function formatAudioTime(totalSec: number): string {
  if (!Number.isFinite(totalSec) || totalSec < 0) return "0:00";
  const whole = Math.floor(totalSec);
  const mm = String(Math.floor(whole / 60));
  const ss = String(whole % 60).padStart(2, "0");
  return `${mm}:${ss}`;
}
