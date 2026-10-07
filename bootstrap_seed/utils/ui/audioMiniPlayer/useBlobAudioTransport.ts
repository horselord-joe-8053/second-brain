/**
 * Singleton HTMLAudioElement transport: credentialed blob fetch, pause/resume without
 * refetch, seek/replay on loaded blob, abort stale fetches on URL switch.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import {
  cycleAudioSpeed,
  readStoredAudioSpeed,
  writeStoredAudioSpeed,
} from "./audioSpeed";
import { clampScrubRatio, isAtEnd, scrubTimeFromRatio } from "./scrubMath";
import type { AudioMiniPlayerSpeed, BlobAudioTransportValue, UseBlobAudioTransportOptions } from "./types";

export function useBlobAudioTransport(
  options: UseBlobAudioTransportOptions,
): BlobAudioTransportValue {
  const { fetchAudio, speedStorageKey, defaultSpeed = 1, onLog, onError } = options;

  const fetchAudioRef = useRef(fetchAudio);
  const onLogRef = useRef(onLog);
  const onErrorRef = useRef(onError);
  fetchAudioRef.current = fetchAudio;
  onLogRef.current = onLog;
  onErrorRef.current = onError;

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const blobUrlRef = useRef<string | null>(null);
  const playTokenRef = useRef(0);
  const fetchAbortRef = useRef<AbortController | null>(null);
  const activeUrlRef = useRef<string | null>(null);
  const loadedUrlRef = useRef<string | null>(null);

  const [activeUrl, setActiveUrl] = useState<string | null>(null);
  const [playingUrl, setPlayingUrl] = useState<string | null>(null);
  const [loadingUrl, setLoadingUrl] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentTimeSec, setCurrentTimeSec] = useState(0);
  const [durationSec, setDurationSec] = useState(0);
  const [speed, setSpeed] = useState<AudioMiniPlayerSpeed>(() =>
    readStoredAudioSpeed(speedStorageKey, defaultSpeed),
  );

  const safePause = useCallback((audio: HTMLAudioElement | null) => {
    if (!audio) return;
    try {
      audio.pause();
    } catch {
      /* jsdom / edge hosts */
    }
  }, []);

  const revokeBlob = useCallback(() => {
    if (!blobUrlRef.current) return;
    try {
      URL.revokeObjectURL(blobUrlRef.current);
    } catch {
      /* partial URL polyfills */
    }
    blobUrlRef.current = null;
  }, []);

  const abortInflightFetch = useCallback(
    (reason: string, url?: string | null) => {
      const controller = fetchAbortRef.current;
      if (!controller) return;
      fetchAbortRef.current = null;
      controller.abort();
      onLogRef.current?.("fetch_abort", url ? { reason, url } : { reason });
    },
    [],
  );

  const syncTimeFromAudio = useCallback((audio: HTMLAudioElement) => {
    const dur = audio.duration;
    const cur = audio.currentTime;
    if (!Number.isFinite(dur) || dur <= 0) {
      setCurrentTimeSec(cur);
      setProgress(0);
      return;
    }
    setCurrentTimeSec(cur);
    setDurationSec(dur);
    setProgress(Math.min(1, cur / dur));
  }, []);

  useEffect(() => {
    activeUrlRef.current = activeUrl;
  }, [activeUrl]);

  useEffect(() => {
    const audio = new Audio();
    audioRef.current = audio;

    const onEnded = () => {
      setPlayingUrl(null);
      const url = activeUrlRef.current;
      if (url) onLogRef.current?.("ended", { url });
    };
    const onTimeUpdate = () => syncTimeFromAudio(audio);
    const onLoadedMetadata = () => {
      if (Number.isFinite(audio.duration) && audio.duration > 0) {
        setDurationSec(audio.duration);
      }
    };

    audio.addEventListener("ended", onEnded);
    audio.addEventListener("timeupdate", onTimeUpdate);
    audio.addEventListener("loadedmetadata", onLoadedMetadata);

    return () => {
      audio.removeEventListener("ended", onEnded);
      audio.removeEventListener("timeupdate", onTimeUpdate);
      audio.removeEventListener("loadedmetadata", onLoadedMetadata);
      abortInflightFetch("provider_unmount");
      safePause(audio);
      revokeBlob();
      audioRef.current = null;
    };
  }, [abortInflightFetch, revokeBlob, safePause, syncTimeFromAudio]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.playbackRate = speed;
  }, [speed]);

  const canResumeUrl = useCallback((url: string) => {
    const audio = audioRef.current;
    return (
      activeUrlRef.current === url &&
      loadedUrlRef.current === url &&
      Boolean(blobUrlRef.current) &&
      Boolean(audio?.src)
    );
  }, []);

  const pause = useCallback(() => {
    const url = activeUrlRef.current;
    safePause(audioRef.current);
    setPlayingUrl(null);
    if (url) onLogRef.current?.("pause", { url });
  }, [safePause]);

  const pauseActiveUrl = useCallback(
    (url: string) => {
      if (activeUrlRef.current !== url) return;
      abortInflightFetch("live_gate_lock", url);
      safePause(audioRef.current);
      setPlayingUrl(null);
      setLoadingUrl((cur) => (cur === url ? null : cur));
      onLogRef.current?.("pause", { reason: "live_gate_lock", url });
    },
    [abortInflightFetch, safePause],
  );

  const seekRatio = useCallback(
    (ratio: number) => {
      const audio = audioRef.current;
      const url = activeUrlRef.current;
      if (!audio || !url || !canResumeUrl(url)) return;
      const dur = audio.duration;
      if (!Number.isFinite(dur) || dur <= 0) return;
      const target = scrubTimeFromRatio(ratio, dur);
      audio.currentTime = target;
      syncTimeFromAudio(audio);
      onLogRef.current?.("seek", { url, at: target, ratio: clampScrubRatio(ratio) });
    },
    [canResumeUrl, syncTimeFromAudio],
  );

  const play = useCallback(
    (url: string) => {
      const audio = audioRef.current;
      if (!audio) return;

      const token = ++playTokenRef.current;
      setActiveUrl(url);
      abortInflightFetch("switch_card", url);
      safePause(audio);
      setPlayingUrl(null);
      loadedUrlRef.current = null;
      revokeBlob();
      setProgress(0);
      setCurrentTimeSec(0);
      setDurationSec(0);
      setLoadingUrl(url);

      const controller = new AbortController();
      fetchAbortRef.current = controller;

      onLogRef.current?.("fetch_start", { token, url });

      void (async () => {
        try {
          const blob = await fetchAudioRef.current(url, controller.signal);
          if (token !== playTokenRef.current) {
            onLogRef.current?.("fetch_stale", { token, current: playTokenRef.current, url });
            return;
          }
          if (!blob.size) {
            throw new Error("audio empty response");
          }
          const blobUrl = URL.createObjectURL(blob);
          blobUrlRef.current = blobUrl;
          audio.src = blobUrl;
          audio.playbackRate = speed;
          await audio.play();
          if (token !== playTokenRef.current) {
            onLogRef.current?.("play_stale", { token, current: playTokenRef.current, url });
            return;
          }
          fetchAbortRef.current = null;
          setLoadingUrl(null);
          setPlayingUrl(url);
          loadedUrlRef.current = url;
          syncTimeFromAudio(audio);
          onLogRef.current?.("play_start", { token, speed, url });
        } catch (err) {
          if (err instanceof DOMException && err.name === "AbortError") {
            onLogRef.current?.("fetch_aborted", { token, url });
            if (token === playTokenRef.current) {
              setLoadingUrl(null);
            }
            return;
          }
          if (token !== playTokenRef.current) return;
          fetchAbortRef.current = null;
          setLoadingUrl(null);
          setPlayingUrl(null);
          onErrorRef.current?.("play_failed", err, { token, url });
        }
      })();
    },
    [abortInflightFetch, revokeBlob, safePause, speed, syncTimeFromAudio],
  );

  const resume = useCallback(
    (url: string) => {
      const audio = audioRef.current;
      if (!audio) return;
      setActiveUrl(url);
      audio.playbackRate = speed;
      void (async () => {
        try {
          await audio.play();
          setPlayingUrl(url);
          onLogRef.current?.("resume", { url, at: audio.currentTime });
        } catch (err) {
          onErrorRef.current?.("resume_failed", err, { url });
          loadedUrlRef.current = null;
          play(url);
        }
      })();
    },
    [play, speed],
  );

  const replay = useCallback(
    (url: string) => {
      const audio = audioRef.current;
      if (!canResumeUrl(url) || !audio) {
        play(url);
        return;
      }
      setActiveUrl(url);
      audio.currentTime = 0;
      syncTimeFromAudio(audio);
      onLogRef.current?.("replay", { url });
      void (async () => {
        try {
          audio.playbackRate = speed;
          await audio.play();
          setPlayingUrl(url);
        } catch (err) {
          onErrorRef.current?.("replay_failed", err, { url });
        }
      })();
    },
    [canResumeUrl, play, speed, syncTimeFromAudio],
  );

  const toggle = useCallback(
    (url: string) => {
      if (playingUrl === url) {
        pause();
        return;
      }
      const audio = audioRef.current;
      if (
        canResumeUrl(url) &&
        audio &&
        isAtEnd(audio.currentTime, audio.duration)
      ) {
        replay(url);
        return;
      }
      if (canResumeUrl(url)) {
        resume(url);
        return;
      }
      play(url);
    },
    [canResumeUrl, pause, play, playingUrl, replay, resume],
  );

  const cycleSpeed = useCallback(() => {
    setSpeed((prev) => {
      const next = cycleAudioSpeed(prev);
      writeStoredAudioSpeed(speedStorageKey, next);
      const audio = audioRef.current;
      if (audio) audio.playbackRate = next;
      const url = activeUrlRef.current;
      onLogRef.current?.("speed", url ? { speed: next, url } : { speed: next });
      return next;
    });
  }, [speedStorageKey]);

  const isActiveUrl = useCallback(
    (url: string | null | undefined) => Boolean(url && activeUrl === url),
    [activeUrl],
  );

  const isPlayingUrl = useCallback(
    (url: string | null | undefined) => Boolean(url && playingUrl === url),
    [playingUrl],
  );

  return {
    activeUrl,
    playingUrl,
    loadingUrl,
    progress,
    currentTimeSec,
    durationSec,
    speed,
    toggle,
    pause,
    pauseActiveUrl,
    seekRatio,
    replay,
    cycleSpeed,
    isActiveUrl,
    isPlayingUrl,
  };
}
