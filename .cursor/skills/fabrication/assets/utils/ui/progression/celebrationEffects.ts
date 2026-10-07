/**
 * Configurable level-up celebration effects — scenario-centric ``progression.animation_effects`` (v9+).
 */
import {
  buildCenterFountainPieces,
  buildGlitterRainPieces,
  buildLeftCannonPieces,
  buildRightCannonPieces,
  type ConfettiPiece,
  type GlitterRainPiece,
} from "./confettiPieces";

export type { GlitterRainPiece };

export type LevelUpScenario = "subarea_level_up" | "general_level_up";

export type PopupSize = "small" | "medium" | "large";

export type ScenarioCelebrationConfig = {
  confetti: {
    left_bottom_cannon: boolean;
    right_bottom_cannon: boolean;
    center_bottom_cannon: boolean;
    glitter_rain_from_top: boolean;
  };
  expanding_ring: {
    enabled: boolean;
    color: string;
  };
  popup: {
    border_and_headline_color: string;
    size: PopupSize;
  };
};

export type AnimationEffectsConfig = {
  popup_fade_duration_ms: number;
  popup_interval_ms: number;
  scenarios: Record<LevelUpScenario, ScenarioCelebrationConfig>;
};

export const POPUP_SIZE_SCALE: Record<PopupSize, number> = {
  small: 0.85,
  medium: 1,
  large: 1.25,
};

export const POPUP_BASE_WIDTH_PX = 269;

export const DEFAULT_POPUP_FADE_DURATION_MS = 9600;
export const DEFAULT_POPUP_INTERVAL_MS = 500;

export const SCENARIO_RING_SUBAREA_GREEN = "#2e7d32";
/** Token resolved by ``ringColorTokens`` → gradient shiny gold ring. */
export const SCENARIO_RING_GENERAL_GOLD = "shiny-gold-1";

const DEFAULT_SUBAREA_SCENARIO: ScenarioCelebrationConfig = {
  confetti: {
    left_bottom_cannon: true,
    right_bottom_cannon: true,
    center_bottom_cannon: false,
    glitter_rain_from_top: false,
  },
  expanding_ring: { enabled: true, color: SCENARIO_RING_SUBAREA_GREEN },
  popup: { border_and_headline_color: SCENARIO_RING_SUBAREA_GREEN, size: "medium" },
};

const DEFAULT_GENERAL_SCENARIO: ScenarioCelebrationConfig = {
  confetti: {
    left_bottom_cannon: true,
    right_bottom_cannon: true,
    center_bottom_cannon: true,
    glitter_rain_from_top: true,
  },
  expanding_ring: { enabled: true, color: SCENARIO_RING_GENERAL_GOLD },
  popup: { border_and_headline_color: "#ffb300", size: "large" },
};

export const DEFAULT_ANIMATION_EFFECTS: AnimationEffectsConfig = {
  popup_fade_duration_ms: DEFAULT_POPUP_FADE_DURATION_MS,
  popup_interval_ms: DEFAULT_POPUP_INTERVAL_MS,
  scenarios: {
    subarea_level_up: DEFAULT_SUBAREA_SCENARIO,
    general_level_up: DEFAULT_GENERAL_SCENARIO,
  },
};

/** @deprecated Use ResolvedScenarioCelebration */
export type ResolvedCelebrationLayers = {
  leftCannon: boolean;
  rightCannon: boolean;
  centerFountain: boolean;
  glitterRain: boolean;
  expandingRing: boolean;
};

export type ResolvedScenarioCelebration = ResolvedCelebrationLayers & {
  ringColor: string;
  borderAndHeadlineColor: string;
  popupSize: PopupSize;
  popupScale: number;
};

export type LevelUpKind = "subarea" | "overall";

export function kindToScenario(kind: LevelUpKind): LevelUpScenario {
  return kind === "overall" ? "general_level_up" : "subarea_level_up";
}

export function resolveScenarioCelebration(
  config: AnimationEffectsConfig,
  scenario: LevelUpScenario,
): ResolvedScenarioCelebration {
  const sc =
    config.scenarios[scenario] ??
    (scenario === "general_level_up" ? DEFAULT_GENERAL_SCENARIO : DEFAULT_SUBAREA_SCENARIO);
  const popupSize = sc.popup.size;
  return {
    leftCannon: sc.confetti.left_bottom_cannon,
    rightCannon: sc.confetti.right_bottom_cannon,
    centerFountain: sc.confetti.center_bottom_cannon,
    glitterRain: sc.confetti.glitter_rain_from_top,
    expandingRing: sc.expanding_ring.enabled,
    ringColor: sc.expanding_ring.color,
    borderAndHeadlineColor: sc.popup.border_and_headline_color,
    popupSize,
    popupScale: POPUP_SIZE_SCALE[popupSize] ?? 1,
  };
}

/** Back-compat alias for confetti layer builders. */
export function resolveCelebrationLayers(
  config: AnimationEffectsConfig,
  scenario: LevelUpScenario,
): ResolvedCelebrationLayers {
  const r = resolveScenarioCelebration(config, scenario);
  return {
    leftCannon: r.leftCannon,
    rightCannon: r.rightCannon,
    centerFountain: r.centerFountain,
    glitterRain: r.glitterRain,
    expandingRing: r.expandingRing,
  };
}

export function buildConfiguredConfettiPieces(
  layers: ResolvedCelebrationLayers,
  seed: number,
): ConfettiPiece[] {
  const pieces: ConfettiPiece[] = [];
  if (layers.leftCannon) pieces.push(...buildLeftCannonPieces(seed + 77));
  if (layers.rightCannon) pieces.push(...buildRightCannonPieces(seed + 88));
  if (layers.centerFountain) pieces.push(...buildCenterFountainPieces(seed + 5));
  return pieces;
}

export function buildConfiguredGlitterRain(
  layers: ResolvedCelebrationLayers,
  seed: number,
  count = 90,
): GlitterRainPiece[] {
  if (!layers.glitterRain) return [];
  return buildGlitterRainPieces(seed + 99, count);
}
