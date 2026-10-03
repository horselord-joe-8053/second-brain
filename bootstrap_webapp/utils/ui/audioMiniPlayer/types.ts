/** Tap-to-cycle playback rates for the card-attached speed chip. */
export const AUDIO_MINI_PLAYER_SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2] as const;

export type AudioMiniPlayerSpeed = (typeof AUDIO_MINI_PLAYER_SPEEDS)[number];

export type BlobAudioTransportLogEvent =
  | "fetch_start"
  | "fetch_abort"
  | "fetch_stale"
  | "fetch_aborted"
  | "play_start"
  | "play_stale"
  | "pause"
  | "resume"
  | "seek"
  | "replay"
  | "ended"
  | "speed";

export type UseBlobAudioTransportOptions = {
  /** Host fetch — e.g. credentialed GET returning a WAV/MP3 blob. */
  fetchAudio: (url: string, signal: AbortSignal) => Promise<Blob>;
  /** Optional localStorage key for persisting speed chip selection. */
  speedStorageKey?: string;
  defaultSpeed?: AudioMiniPlayerSpeed;
  onLog?: (event: BlobAudioTransportLogEvent, fields?: Record<string, unknown>) => void;
  onError?: (event: string, error: unknown, fields?: Record<string, unknown>) => void;
};

export type BlobAudioTransportValue = {
  activeUrl: string | null;
  playingUrl: string | null;
  loadingUrl: string | null;
  progress: number;
  currentTimeSec: number;
  durationSec: number;
  speed: AudioMiniPlayerSpeed;
  toggle: (url: string) => void;
  pause: () => void;
  pauseActiveUrl: (url: string) => void;
  seekRatio: (ratio: number) => void;
  replay: (url: string) => void;
  cycleSpeed: () => void;
  isActiveUrl: (url: string | null | undefined) => boolean;
  isPlayingUrl: (url: string | null | undefined) => boolean;
};
