/**
 * Shared scoreboard layout tokens — keep in sync with canvas SCOREBOARD_GRID (v14).
 * Imported by prod components, Vitest, and dev preview routes.
 */
export const SCOREBOARD_GRID = {
  /** competency | subarea | word stack | tries | Top-N links */
  columns: "108px minmax(200px, 1.35fr) 180px 44px minmax(288px, max-content)",
  stackWidthPx: 156,
  colCount: 5,
} as const;

export const SCOREBOARD_GRID_STYLE = {
  gridTemplateColumns: SCOREBOARD_GRID.columns,
} as const;
