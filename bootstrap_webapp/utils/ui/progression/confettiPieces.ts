/**
 * Level-up confetti piece generators — per-emitter bursts from v9 mockup.
 * Plug-and-play: pair with host CSS classes ``f35-confetti-*`` or supply your own renderer.
 */

export type ConfettiShape = "rect" | "dot" | "ribbon";

export type ConfettiPiece = {
  x: number;
  y: number;
  dx: number;
  peak: number;
  floor: number;
  delay: number;
  dur: number;
  color: string;
  shape: ConfettiShape;
  w: number;
  h: number;
  rx: number;
  ry: number;
  rz0: number;
  rz1: number;
  spinDur: number;
};

type Emitter = {
  x: number;
  y: number;
  angle: number;
  spread: number;
  power: [number, number];
  count: number;
  shapes?: ConfettiShape[];
};

export const CONFETTI_COLORS = [
  "#1976d2",
  "#2e7d32",
  "#ffb300",
  "#e91e63",
  "#00897b",
  "#ff7043",
  "#7b1fa2",
  "#26c6da",
] as const;

function prng(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function makePieces(
  emitters: Emitter[],
  colors: readonly string[],
  seed: number,
  baseDelay = 0,
  floorRange: [number, number] = [300, 460],
): ConfettiPiece[] {
  const r = prng(seed);
  const defaultShapes: ConfettiShape[] = ["rect", "rect", "dot", "ribbon", "rect", "ribbon"];
  const out: ConfettiPiece[] = [];
  emitters.forEach((e, ei) => {
    const shapes = e.shapes ?? defaultShapes;
    for (let i = 0; i < e.count; i += 1) {
      const a = ((e.angle + (r() * 2 - 1) * e.spread) * Math.PI) / 180;
      const p = e.power[0] + r() * (e.power[1] - e.power[0]);
      const dx = Math.cos(a) * p * (0.9 + r() * 0.5);
      const peak = Math.sin(a) * p;
      const shape = shapes[Math.floor(r() * shapes.length)] ?? "rect";
      const spinSign = r() > 0.5 ? 1 : -1;
      out.push({
        x: e.x,
        y: e.y,
        dx,
        peak: Math.min(peak, -30),
        floor: floorRange[0] + r() * (floorRange[1] - floorRange[0]),
        delay: baseDelay + ei * 0.08 + r() * 0.22,
        dur: 1.9 + r() * 1.1,
        color: colors[Math.floor(r() * colors.length)] ?? colors[0]!,
        shape,
        w: shape === "ribbon" ? 4 : shape === "dot" ? 6 + r() * 4 : 7 + r() * 5,
        h: shape === "ribbon" ? 16 + r() * 8 : shape === "dot" ? 0 : 9 + r() * 6,
        rx: spinSign * (540 + r() * 720),
        ry: -spinSign * (360 + r() * 720),
        rz0: r() * 360,
        rz1: r() * 360 + spinSign * 540,
        spinDur: 0.9 + r() * 0.9,
      });
    }
  });
  return out;
}

export function buildLeftCannonPieces(seed: number, baseDelay = 0.35): ConfettiPiece[] {
  return makePieces(
    [{ x: 2, y: 100, angle: -58, spread: 14, power: [340, 560], count: 45 }],
    CONFETTI_COLORS,
    seed,
    baseDelay,
  );
}

export function buildRightCannonPieces(seed: number, baseDelay = 0.35): ConfettiPiece[] {
  return makePieces(
    [{ x: 98, y: 100, angle: -122, spread: 14, power: [340, 560], count: 45 }],
    CONFETTI_COLORS,
    seed,
    baseDelay,
  );
}

export function buildCenterFountainPieces(seed: number): ConfettiPiece[] {
  return makePieces(
    [
      { x: 50, y: 100, angle: -90, spread: 26, power: [360, 620], count: 80 },
      { x: 50, y: 100, angle: -90, spread: 48, power: [220, 420], count: 50 },
    ],
    CONFETTI_COLORS,
    seed,
  );
}

export type GlitterRainPiece = {
  x: number;
  delay: number;
  dur: number;
  sway: number;
  swayDur: number;
  size: number;
  color: string;
};

export function buildGlitterRainPieces(seed: number, count = 90): GlitterRainPiece[] {
  const r = prng(seed);
  return Array.from({ length: count }, () => ({
    x: r() * 100,
    delay: r() * 1.4,
    dur: 2.6 + r() * 1.6,
    sway: (r() * 2 - 1) * 60,
    swayDur: 1.2 + r() * 1.2,
    size: 3 + r() * 4,
    color: CONFETTI_COLORS[Math.floor(r() * CONFETTI_COLORS.length)] ?? CONFETTI_COLORS[0]!,
  }));
}

/** Corner cannons only — legacy helper; prefer ``buildConfiguredConfettiPieces``. */
export function buildLevelUpConfettiPieces(seed = 11): ConfettiPiece[] {
  return [...buildLeftCannonPieces(seed, 0), ...buildRightCannonPieces(seed + 1, 0)];
}
