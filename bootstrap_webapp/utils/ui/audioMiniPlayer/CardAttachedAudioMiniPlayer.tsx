/**
 * Presentational card-attached audio bar — play/pause · replay · seek scrubber · time · speed.
 * All copy/aria labels are host-provided for i18n; styles in cardAttachedAudioMiniPlayer.css.
 */
import { formatAudioTime } from "./formatAudioTime";
import { clampScrubRatio } from "./scrubMath";
import { AudioMiniPauseIcon, AudioMiniPlayIcon, AudioMiniReplayIcon } from "./icons";

export type CardAttachedAudioMiniPlayerProps = {
  testId?: string;
  playing: boolean;
  loading: boolean;
  /** 0–1 progress for scrubber thumb position. */
  progress: number;
  currentTimeSec: number;
  durationSec: number;
  speedLabel: string;
  playLabel: string;
  pauseLabel: string;
  replayLabel: string;
  cycleSpeedLabel: string;
  scrubAriaLabel: string;
  /** When false, scrubber and replay are disabled (e.g. still fetching). */
  transportReady?: boolean;
  onTogglePlay: () => void;
  onReplay: () => void;
  onSeekRatio: (ratio: number) => void;
  onCycleSpeed: () => void;
};

export function CardAttachedAudioMiniPlayer({
  testId,
  playing,
  loading,
  progress,
  currentTimeSec,
  durationSec,
  speedLabel,
  playLabel,
  pauseLabel,
  replayLabel,
  cycleSpeedLabel,
  scrubAriaLabel,
  transportReady = true,
  onTogglePlay,
  onReplay,
  onSeekRatio,
  onCycleSpeed,
}: CardAttachedAudioMiniPlayerProps) {
  const playOrPauseLabel = playing ? pauseLabel : playLabel;
  const totalLabel = durationSec > 0 ? formatAudioTime(durationSec) : "—";
  const scrubDisabled = loading || !transportReady;
  const scrubRatio = clampScrubRatio(progress);
  const scrubPct = scrubRatio * 100;

  return (
    <div className="f35-audio-mini" data-testid={testId}>
      <button
        type="button"
        className={`f35-audio-mini__round-btn${playing ? " f35-audio-mini__round-btn--playing" : ""}${loading ? " f35-audio-mini__round-btn--loading" : ""}`}
        title={playOrPauseLabel}
        aria-label={playOrPauseLabel}
        disabled={loading}
        data-testid={testId ? `${testId}-play` : undefined}
        onClick={onTogglePlay}
      >
        {playing ? <AudioMiniPauseIcon /> : <AudioMiniPlayIcon />}
      </button>
      <button
        type="button"
        className="f35-audio-mini__round-btn f35-audio-mini__round-btn--secondary"
        title={replayLabel}
        aria-label={replayLabel}
        disabled={scrubDisabled}
        data-testid={testId ? `${testId}-replay` : undefined}
        onClick={onReplay}
      >
        <AudioMiniReplayIcon />
      </button>
      <div className="f35-audio-mini__track">
        <div className="f35-audio-mini__scrubber-wrap">
          <div className="f35-audio-mini__scrubber-rail" aria-hidden="true">
            <div
              className="f35-audio-mini__scrubber-fill"
              style={{ width: `${scrubPct}%` }}
              data-testid={testId ? `${testId}-scrubber-fill` : undefined}
            />
          </div>
          <input
            type="range"
            className="f35-audio-mini__scrubber"
            min={0}
            max={100}
            step={0.1}
            value={scrubPct}
            disabled={scrubDisabled}
            aria-label={scrubAriaLabel}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={Math.round(scrubPct)}
            data-testid={testId ? `${testId}-scrubber` : undefined}
            onChange={(e) => onSeekRatio(Number(e.target.value) / 100)}
          />
        </div>
        <span className="f35-audio-mini__time">
          {formatAudioTime(currentTimeSec)} / {totalLabel}
        </span>
      </div>
      <button
        type="button"
        className="f35-audio-mini__speed"
        title={cycleSpeedLabel}
        aria-label={cycleSpeedLabel}
        data-testid={testId ? `${testId}-speed` : undefined}
        onClick={onCycleSpeed}
      >
        {speedLabel}
      </button>
    </div>
  );
}
