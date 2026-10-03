import {
  AUDIO_MINI_PLAYER_SPEEDS,
  type AudioMiniPlayerSpeed,
} from "./types";

export { AUDIO_MINI_PLAYER_SPEEDS, type AudioMiniPlayerSpeed };

export function formatAudioSpeedLabel(speed: AudioMiniPlayerSpeed): string {
  return `${speed}×`;
}

export function cycleAudioSpeed(current: AudioMiniPlayerSpeed): AudioMiniPlayerSpeed {
  const idx = AUDIO_MINI_PLAYER_SPEEDS.indexOf(current);
  return AUDIO_MINI_PLAYER_SPEEDS[(idx + 1) % AUDIO_MINI_PLAYER_SPEEDS.length];
}

export function readStoredAudioSpeed(
  storageKey: string | undefined,
  fallback: AudioMiniPlayerSpeed = 1,
): AudioMiniPlayerSpeed {
  if (!storageKey) return fallback;
  try {
    const raw = localStorage.getItem(storageKey);
    const parsed = raw != null ? Number.parseFloat(raw) : NaN;
    if (AUDIO_MINI_PLAYER_SPEEDS.includes(parsed as AudioMiniPlayerSpeed)) {
      return parsed as AudioMiniPlayerSpeed;
    }
  } catch {
    /* private mode / quota */
  }
  return fallback;
}

export function writeStoredAudioSpeed(storageKey: string | undefined, speed: AudioMiniPlayerSpeed): void {
  if (!storageKey) return;
  try {
    localStorage.setItem(storageKey, String(speed));
  } catch {
    /* ignore */
  }
}
