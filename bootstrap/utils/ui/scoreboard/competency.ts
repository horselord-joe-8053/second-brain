/**
 * Combined Basic + Paragraph competency math (v13 canvas lock).
 * Word stack, competency %, and Top N priority all use the same aggregation.
 */
import type { ScoreBoardConfig, TermBucket, TermStat, WordStackCounts } from "./types";

export const BUCKET_SORT_ORDER: Record<TermBucket, number> = {
  unsatisfied: 0,
  untouched: 1,
  improving: 2,
  satisfied: 3,
};

export function termAttempts(t: TermStat): number {
  return t.basic_correct + t.basic_incorrect + t.para_correct + t.para_incorrect;
}

export function netBasePoints(t: TermStat, cfg: ScoreBoardConfig): number {
  return (
    cfg.basic_prac_point_per_word * (t.basic_correct - t.basic_incorrect) +
    cfg.paragraph_prac_point_per_word * (t.para_correct - t.para_incorrect)
  );
}

export function termCompetencyPct(t: TermStat, cfg: ScoreBoardConfig): number {
  if (termAttempts(t) === 0) return 0;
  const target = cfg.prac_full_competency_point_per_word;
  const ratio = netBasePoints(t, cfg) / target;
  return Math.max(0, Math.min(100, ratio * 100));
}

export function classifyTermCombined(t: TermStat, cfg: ScoreBoardConfig): TermBucket {
  const att = termAttempts(t);
  if (att === 0) return "untouched";
  const net = netBasePoints(t, cfg);
  const target = cfg.prac_full_competency_point_per_word;
  if (net >= target) return "satisfied";
  if (net > 0) return "improving";
  return "unsatisfied";
}

export function summarizeWordStack(terms: TermStat[], cfg: ScoreBoardConfig): WordStackCounts {
  const buckets = terms.map((t) => classifyTermCombined(t, cfg));
  return {
    satisfied: buckets.filter((b) => b === "satisfied").length,
    improving: buckets.filter((b) => b === "improving").length,
    unsatisfied: buckets.filter((b) => b === "unsatisfied").length,
    untouched: buckets.filter((b) => b === "untouched").length,
  };
}

export function leafCompetencyPct(terms: TermStat[], cfg: ScoreBoardConfig): number {
  if (!terms.length) return 0;
  return terms.reduce((s, t) => s + termCompetencyPct(t, cfg), 0) / terms.length;
}

export function leafNetTotal(terms: TermStat[], cfg: ScoreBoardConfig): number {
  return terms.reduce((s, t) => s + netBasePoints(t, cfg), 0);
}

export function leafEventCount(terms: TermStat[]): number {
  return terms.reduce((s, t) => s + termAttempts(t), 0);
}

export type PriorityItem = {
  term: TermStat;
  bucket: TermBucket;
  net: number;
};

/** Top N — combined net buckets; excludes Satisfied; sort Unsatisfied → Untouched A–Z → Improving. */
export function buildCombinedPriorityList(terms: TermStat[], cfg: ScoreBoardConfig): PriorityItem[] {
  const limit = cfg.num_top_priority_items;
  return terms
    .map((term) => ({
      term,
      bucket: classifyTermCombined(term, cfg),
      net: netBasePoints(term, cfg),
    }))
    .filter((x) => x.bucket !== "satisfied")
    .sort((a, b) => {
      const byBucket = BUCKET_SORT_ORDER[a.bucket] - BUCKET_SORT_ORDER[b.bucket];
      if (byBucket !== 0) return byBucket;
      if (a.bucket === "untouched") return a.term.label.localeCompare(b.term.label, "pt");
      return a.net - b.net;
    })
    .slice(0, limit);
}

export function priorityKeys(terms: TermStat[], cfg: ScoreBoardConfig): string[] {
  return buildCombinedPriorityList(terms, cfg).map((x) => x.term.content_key);
}
