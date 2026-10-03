/**
 * Named ring colors for ``expanding_ring.color`` — hex or tokens like ``shiny-gold-1``.
 * Tokens map to shared CSS classes in ``expandingRing.css`` (gradient + glow presets).
 */
import type { ExpandingRingRingSpec } from "./ringBurstSpec";
import { EXPANDING_RING_CLASSES, expandingRingRingStyle } from "./ringBurstSpec";

export const SHINY_GOLD_1_TOKEN = "shiny-gold-1";

export const RING_COLOR_TOKEN_IDS = [SHINY_GOLD_1_TOKEN] as const;

export type RingColorTokenId = (typeof RING_COLOR_TOKEN_IDS)[number];

/** Optional ``#`` prefix in YAML; ``shinny-gold-1`` aliases the canonical token. */
const TOKEN_ALIASES: Record<string, RingColorTokenId> = {
  [SHINY_GOLD_1_TOKEN]: SHINY_GOLD_1_TOKEN,
  "shinny-gold-1": SHINY_GOLD_1_TOKEN,
};

const TOKEN_CLASS: Record<RingColorTokenId, string> = {
  [SHINY_GOLD_1_TOKEN]: "f35-expanding-ring--shiny-gold-1",
};

/** Canvas mockups inject this block when repo imports are unavailable. */
export const RING_TOKEN_STYLESHEET = `
.f35-expanding-ring.f35-expanding-ring--shiny-gold-1 {
  border: none;
  background: radial-gradient(circle closest-side, transparent calc(50% - 5px), #7a5420 calc(50% - 5px), #926f34 calc(50% - 3px), #f7ef8a 50%, #edc967 calc(50% + 3px), #ae8625 calc(50% + 5px), transparent calc(50% + 5px));
  box-shadow: 0 0 10px rgba(247, 239, 138, 0.55), 0 0 22px rgba(174, 134, 37, 0.45);
  filter: saturate(1.15) contrast(1.1);
  animation-name: f35ExpandingRingGold;
}
@keyframes f35ExpandingRingGold {
  0% { transform: scale(0.15); opacity: 0.96; }
  100% { transform: scale(var(--f35-ring-max, 2.2)); opacity: 0; }
}
`.trim();

export type ResolvedRingAppearance =
  | { kind: "solid"; color: string }
  | { kind: "token"; token: RingColorTokenId; className: string };

export function normalizeRingColorSpec(spec: string): string {
  return spec.trim().replace(/^#/, "").toLowerCase();
}

export function resolveRingAppearance(spec: string): ResolvedRingAppearance {
  const key = normalizeRingColorSpec(spec);
  const token = TOKEN_ALIASES[key];
  if (token) {
    return { kind: "token", token, className: TOKEN_CLASS[token] };
  }
  const trimmed = spec.trim();
  const color = trimmed.startsWith("#") ? trimmed : `#${trimmed}`;
  return { kind: "solid", color };
}

export function ringSpanClassName(
  appearance: ResolvedRingAppearance,
  extraClass?: string,
): string {
  const parts = [EXPANDING_RING_CLASSES.ring];
  if (appearance.kind === "token") parts.push(appearance.className);
  if (extraClass) parts.push(extraClass);
  return parts.filter(Boolean).join(" ");
}

export function ringSpanStyle(
  appearance: ResolvedRingAppearance,
  spec: ExpandingRingRingSpec,
): Record<string, string | number> {
  const timing = {
    animationDuration: `${spec.durationSec}s`,
    animationDelay: `${spec.delaySec}s`,
    "--f35-ring-max": String(spec.ringMax),
  };
  if (appearance.kind === "solid") {
    return { ...expandingRingRingStyle(appearance.color, spec) };
  }
  return timing;
}
