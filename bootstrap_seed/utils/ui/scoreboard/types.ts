/**
 * Shared scoreboard types — competency table and points-over-time chart (v13 canvas).
 */

export type TermBucket = "satisfied" | "improving" | "unsatisfied" | "untouched";

export type ScoreBoardConfig = {
  basic_prac_point_per_word: number;
  paragraph_prac_point_per_word: number;
  prac_full_competency_point_per_word: number;
  num_top_priority_items: number;
};

export type TermStat = {
  content_key: string;
  label: string;
  basic_correct: number;
  basic_incorrect: number;
  para_correct: number;
  para_incorrect: number;
  /** Published paragraph blank ``content_id`` — same SoT as ``GET …/paragraph/lemmas`` / URL ``lemma_ids``. */
  pool_item_id?: number;
};

export type WordStackCounts = {
  satisfied: number;
  improving: number;
  unsatisfied: number;
  untouched: number;
};

export type CompetencyLeafRow = {
  scope: string;
  label: string;
  glossary: string;
  competency_pct: number;
  net_total: number;
  events: number;
  word_stack: WordStackCounts;
  terms: TermStat[];
  priority_keys: string[];
};

export type TimeSeriesInterval = "hourly" | "daily" | "weekly" | "monthly";

export type PointsOverTimeSeries = {
  scope: string;
  label: string;
  cumulative: number[];
};

export type LevelMarker = {
  level: number;
  points: number;
  index: number;
};

export type PointsOverTimePayload = {
  categories: string[];
  series: PointsOverTimeSeries[];
  overall: number[];
  level_markers: LevelMarker[];
  interval: TimeSeriesInterval;
  timezone?: string;
  range_start?: string;
  range_end?: string;
};
