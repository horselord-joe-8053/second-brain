# Card-attached audio mini player (`@ui/audioMiniPlayer`)

Portable React building blocks for a **singleton blob-audio transport** plus a compact **card-attached mini bar** (play/pause · replay · seek scrubber · elapsed/total · speed chip).

## Document outline

1. [When to use](#when-to-use) — scope.
2. [Exports](#exports) — public surface.
3. [Quick start](#quick-start) — hook + presentational bar.
4. [Transport state machine](#transport-state-machine) — seek/replay rules.
5. [Styling](#styling) — CSS import.

---

## 1. When to use

Use when a list of cards shares **one** `HTMLAudioElement`, each card can trigger credentialed (or public) blob fetch once, and the active card shows an inline transport bar.

**Not included:** auth routes, i18n catalogs, or domain logging — pass those via `fetchAudio` / `onLog` hooks from the host app.

---

## 2. Exports

| Export | Role |
|--------|------|
| `useBlobAudioTransport` | Singleton fetch · blob URL · play / pause / resume / seek / replay / speed |
| `CardAttachedAudioMiniPlayer` | Presentational bar — all labels via props |
| `formatAudioTime`, `scrubMath`, `audioSpeed` helpers | Time formatting, ratio clamp, speed cycle |
| `AudioMiniPlayIcon`, `AudioMiniPauseIcon`, `AudioMiniReplayIcon` | SVG icons |

---

## 3. Quick start

```tsx
import "@ui/audioMiniPlayer/cardAttachedAudioMiniPlayer.css";
import {
  CardAttachedAudioMiniPlayer,
  useBlobAudioTransport,
} from "@ui/audioMiniPlayer";

function Page() {
  const audio = useBlobAudioTransport({
    fetchAudio: (url, signal) =>
      fetch(url, { credentials: "include", signal }).then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.blob();
      }),
  });

  return (
    <CardAttachedAudioMiniPlayer
      playing={audio.isPlayingUrl(clipUrl)}
      loading={audio.loadingUrl === clipUrl}
      progress={audio.progress}
      currentTimeSec={audio.currentTimeSec}
      durationSec={audio.durationSec}
      speed={audio.speed}
      speedLabel={`${audio.speed}×`}
      playLabel="Play"
      pauseLabel="Pause"
      replayLabel="Replay from beginning"
      cycleSpeedLabel="Cycle speed"
      scrubAriaLabel="Seek"
      onTogglePlay={() => audio.toggle(clipUrl)}
      onReplay={() => audio.replay(clipUrl)}
      onSeekRatio={(ratio) => audio.seekRatio(ratio)}
      onCycleSpeed={audio.cycleSpeed}
    />
  );
}
```

---

## 4. Transport state machine

| Action | Network | DOM |
|--------|---------|-----|
| Cold play | One fetch → blob URL | `audio.play()` |
| Pause | None | `audio.pause()`, keep blob + `currentTime` |
| Warm play | None | `audio.play()` at `currentTime` |
| Seek / scrub | None | Set `audio.currentTime` (no refetch) |
| Replay | None | `currentTime = 0` then `play()` |
| Switch URL | Abort prior fetch; new fetch | New blob |

**Ended:** `playingUrl` clears; blob stays loaded until switch. **Replay** (or play after ended) seeks to 0 without refetch.

---

## 5. Styling

Import once in the app entry:

```ts
import "@ui/audioMiniPlayer/cardAttachedAudioMiniPlayer.css";
```

Root class: `.f35-audio-mini`. Round transport buttons reuse `.f35-audio-mini__round-btn`.
