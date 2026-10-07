/**
 * Progress bar fill math — reusable across dual-bar headers and profile widgets.
 * Returns 0% when totals are negative or the band width is non-positive.
 */

export function progressBarFillPct(inLevel: number, band: number, total: number): number {
  if (total < 0 || band <= 0) return 0;
  return Math.min(100, Math.max(0, (inLevel / band) * 100));
}
