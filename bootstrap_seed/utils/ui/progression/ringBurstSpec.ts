/**
 * Expanding ring burst — shared spec for v9 mockup and CelebrationLayer (one shot, 3 rings).
 */
export const EXPANDING_RING_COUNT = 3;
export const EXPANDING_RING_SIZE_PX = 175;

export const EXPANDING_RING_CLASSES = {
  layer: "f35-expanding-ring-layer",
  ring: "f35-expanding-ring",
} as const;

export type ExpandingRingRingSpec = {
  durationSec: number;
  delaySec: number;
  ringMax: number;
};

/** Ring timing matches v9 mockup RingPulse (single burst, not looped). */
export function buildExpandingRingSpecs(
  count = EXPANDING_RING_COUNT,
): ExpandingRingRingSpec[] {
  return Array.from({ length: count }, (_, i) => ({
    durationSec: 1.3 + i * 0.15,
    delaySec: i * 0.18,
    ringMax: 2.2 + i * 0.5,
  }));
}

export function expandingRingRingStyle(
  color: string,
  spec: ExpandingRingRingSpec,
): Record<string, string | number> {
  return {
    borderColor: color,
    animationDuration: `${spec.durationSec}s`,
    animationDelay: `${spec.delaySec}s`,
    "--f35-ring-max": String(spec.ringMax),
  };
}

/** Inject in canvas mockups; production imports ``expandingRing.css`` instead. */
export const EXPANDING_RING_STYLESHEET = `
.${EXPANDING_RING_CLASSES.layer} {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  overflow: visible;
}
.${EXPANDING_RING_CLASSES.ring} {
  position: absolute;
  left: 50%;
  top: 50%;
  width: ${EXPANDING_RING_SIZE_PX}px;
  height: ${EXPANDING_RING_SIZE_PX}px;
  margin-left: ${-EXPANDING_RING_SIZE_PX / 2}px;
  margin-top: ${-EXPANDING_RING_SIZE_PX / 2}px;
  border-radius: 999px;
  border: 2px solid #2e7d32;
  opacity: 0;
  pointer-events: none;
  animation-name: f35ExpandingRing;
  animation-timing-function: cubic-bezier(0.2, 0.7, 0.3, 1);
  animation-fill-mode: both;
}
@keyframes f35ExpandingRing {
  0% { transform: scale(0.15); opacity: 0.85; }
  100% { transform: scale(var(--f35-ring-max, 2.2)); opacity: 0; }
}
`.trim();
