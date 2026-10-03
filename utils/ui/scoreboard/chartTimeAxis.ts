/**
 * Points-over-time x-axis — display labels and sparse tick selection.
 */
import type { TimeSeriesInterval } from "./types";

/** Hourly bucket keys use ``YYYY-MM-DDThh:00``; chart shows ``YYYY-MM-DD hh:00``. */
export function formatCategoryAxisLabel(category: string, interval: TimeSeriesInterval): string {
  if (interval === "hourly") {
    const match = /^(\d{4}-\d{2}-\d{2})T(\d{2}):00$/.exec(category);
    if (match) {
      return `${match[1]} ${match[2]}:00`;
    }
  }
  return category;
}

/** Pick up to *maxLabels* indices (always first + last) so x-axis stays readable. */
export function pickCategoryLabelIndices(count: number, maxLabels = 8): number[] {
  if (count <= 0) return [];
  if (count <= maxLabels) {
    return Array.from({ length: count }, (_, i) => i);
  }
  const indices = new Set<number>([0, count - 1]);
  const step = Math.max(1, Math.ceil((count - 1) / (maxLabels - 1)));
  for (let i = 0; i < count; i += step) {
    indices.add(i);
  }
  return [...indices].sort((a, b) => a - b);
}
