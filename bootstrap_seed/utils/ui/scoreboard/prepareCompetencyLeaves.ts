/**
 * Normalize competency-leaves API rows for v14 full-catalog grid — merge, rollup, rank ascending.
 */
import {
  leafCompetencyPct,
  leafEventCount,
  leafNetTotal,
  priorityKeys,
  summarizeWordStack,
} from "./competency";
import { CATALOG_23_SCOPES, isCatalog23Scope, rollupTermsToCatalogPool } from "./catalogPool";
import type { CompetencyLeafRow, ScoreBoardConfig } from "./types";

function glossaryForScope(scope: string): string {
  const head = (scope || "").split(":", 1)[0];
  const mapping: Record<string, string> = {
    inanimate: "noun",
    animate: "noun",
    animated: "noun",
    plural: "noun",
    "noun-phrase": "noun",
    places: "place",
    numbers: "number",
    clitics: "verb",
    "verb-complementation": "verb",
    comparison: "other-word",
    adjectives: "other-word",
    determiners: "other-word",
    contractions: "other-word",
    "por-para": "other-word",
  };
  return mapping[head] ?? head ?? "unknown";
}

function scopeLabel(scope: string): string {
  if (!scope) return "—";
  return scope.replace(":", " · ");
}

/** Legacy stat rows stored bare practice mode instead of nav chip scope. */
export function canonicalDashboardScope(scope: string): string {
  const s = (scope || "").trim();
  if (s === "cardinals") {
    return "numbers:cardinals";
  }
  return s;
}

export type CompetencySortDir = "asc" | "desc";

export function rankLeavesByCompetency(
  leaves: CompetencyLeafRow[],
  dir: CompetencySortDir = "asc",
): CompetencyLeafRow[] {
  const sign = dir === "asc" ? 1 : -1;
  return [...leaves].sort((a, b) => {
    if (a.competency_pct !== b.competency_pct) {
      return sign * (a.competency_pct - b.competency_pct);
    }
    return a.scope.localeCompare(b.scope);
  });
}

export function rankLeavesByCompetencyAsc(leaves: CompetencyLeafRow[]): CompetencyLeafRow[] {
  return rankLeavesByCompetency(leaves, "asc");
}

function poolItemIdByContentKey(terms: CompetencyLeafRow["terms"]): Map<string, number> {
  const out = new Map<string, number>();
  for (const term of terms) {
    const pid = term.pool_item_id ?? 0;
    if (pid > 0) {
      out.set(term.content_key, pid);
    }
  }
  return out;
}

function attachPoolItemIds(
  terms: CompetencyLeafRow["terms"],
  byKey: Map<string, number>,
): CompetencyLeafRow["terms"] {
  if (!byKey.size) {
    return terms;
  }
  return terms.map((term) => {
    const pid = term.pool_item_id ?? byKey.get(term.content_key) ?? 0;
    return pid > 0 ? { ...term, pool_item_id: pid } : term;
  });
}

function normalizeLeaf(leaf: CompetencyLeafRow, cfg: ScoreBoardConfig): CompetencyLeafRow {
  const poolIds = poolItemIdByContentKey(leaf.terms);
  const terms = attachPoolItemIds(rollupTermsToCatalogPool(leaf.scope, leaf.terms), poolIds);
  const word_stack = summarizeWordStack(terms, cfg);
  return {
    ...leaf,
    terms,
    word_stack,
    competency_pct: Math.round(leafCompetencyPct(terms, cfg) * 10) / 10,
    net_total: leafNetTotal(terms, cfg),
    events: leafEventCount(terms),
    priority_keys: priorityKeys(terms, cfg),
  };
}

function emptyCatalogLeaf(scope: string): CompetencyLeafRow {
  return {
    scope,
    label: scopeLabel(scope),
    glossary: glossaryForScope(scope),
    competency_pct: 0,
    net_total: 0,
    events: 0,
    word_stack: { satisfied: 0, improving: 0, unsatisfied: 0, untouched: 0 },
    terms: [],
    priority_keys: [],
  };
}

/**
 * Ensure every catalog-23 subarea appears once, rollup word stacks, append legacy stat-only scopes.
 */
export function ensureCatalogLeaves(apiLeaves: CompetencyLeafRow[], cfg: ScoreBoardConfig): CompetencyLeafRow[] {
  const byScope = new Map<string, CompetencyLeafRow>();
  for (const raw of apiLeaves) {
    const scope = canonicalDashboardScope(raw.scope);
    const existing = byScope.get(scope);
    if (!existing || raw.events > existing.events) {
      byScope.set(scope, { ...raw, scope });
    }
  }

  const merged: CompetencyLeafRow[] = [];
  for (const scope of CATALOG_23_SCOPES) {
    merged.push(normalizeLeaf(byScope.get(scope) ?? emptyCatalogLeaf(scope), cfg));
  }

  for (const leaf of byScope.values()) {
    if (!isCatalog23Scope(leaf.scope)) {
      merged.push(normalizeLeaf(leaf, cfg));
    }
  }

  return rankLeavesByCompetencyAsc(merged);
}

export function prepareCompetencyLeaves(apiLeaves: CompetencyLeafRow[], cfg: ScoreBoardConfig): CompetencyLeafRow[] {
  return ensureCatalogLeaves(apiLeaves, cfg);
}
