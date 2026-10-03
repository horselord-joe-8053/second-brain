/**
 * Client pagination for ranked competency table — sort globally first, then slice.
 */

export type PaginatedLeaves<T> = {
  pageItems: T[];
  page: number;
  pageCount: number;
  total: number;
};

export function paginateLeaves<T>(sorted: T[], page: number, pageSize: number): PaginatedLeaves<T> {
  const total = sorted.length;
  const safeSize = Math.max(1, pageSize);
  const pageCount = Math.max(1, Math.ceil(total / safeSize));
  const clampedPage = Math.min(Math.max(0, page), pageCount - 1);
  const start = clampedPage * safeSize;
  return {
    pageItems: sorted.slice(start, start + safeSize),
    page: clampedPage,
    pageCount,
    total,
  };
}
