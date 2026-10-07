/**
 * Catalog-23 pool rollup for competency word stacks — mirrors API ``rollup_terms_to_catalog_pool``.
 * Uses ``config/seeds/catalog-23-pools.json`` so prod UI matches backend even on partial API payloads.
 */
import catalog from "../../../config/seeds/catalog-23-pools.json";
import type { TermStat } from "./types";

type CatalogPoolEntry = {
  content_key: string;
  lemma: string;
};

const CATALOG_POOLS = catalog.pools as Record<string, CatalogPoolEntry[]>;

export const CATALOG_23_SCOPES = catalog.scopes as readonly string[];

const FIELD_SUFFIXES = [":masc_pl", ":fem_pl", ":masc", ":fem", ":form"] as const;

function lemmaNorm(text: string): string {
  return text.trim().toLowerCase();
}

function stripFieldSuffix(contentKey: string): string {
  for (const suffix of FIELD_SUFFIXES) {
    if (contentKey.endsWith(suffix)) {
      return contentKey.slice(0, -suffix.length);
    }
  }
  return contentKey;
}

export function poolContentKey(scope: string, lemma: string): string {
  return `${scope}:${lemma.trim().toLowerCase()}`;
}

export function isCatalog23Scope(scope: string): boolean {
  return (CATALOG_23_SCOPES as readonly string[]).includes(scope);
}

function emptyPoolTerm(contentKey: string, label: string): TermStat {
  return {
    content_key: contentKey,
    label,
    basic_correct: 0,
    basic_incorrect: 0,
    para_correct: 0,
    para_incorrect: 0,
  };
}

function addTerm(target: TermStat, source: TermStat): TermStat {
  const pool_item_id = target.pool_item_id || source.pool_item_id || 0;
  return {
    content_key: target.content_key,
    label: target.label,
    basic_correct: target.basic_correct + source.basic_correct,
    basic_incorrect: target.basic_incorrect + source.basic_incorrect,
    para_correct: target.para_correct + source.para_correct,
    para_incorrect: target.para_incorrect + source.para_incorrect,
    ...(pool_item_id > 0 ? { pool_item_id } : {}),
  };
}

/** One combined Basic+Paragraph term per catalog pool row; fills never-attempted lemmas as untouched. */
export function rollupTermsToCatalogPool(scope: string, terms: TermStat[]): TermStat[] {
  if (!isCatalog23Scope(scope)) {
    return terms;
  }
  const entries = CATALOG_POOLS[scope];
  if (!entries?.length) {
    return terms;
  }

  const keyToPool: Record<string, string> = {};
  const buckets: Record<string, TermStat> = {};
  for (const entry of entries) {
    const label = (entry.lemma || "").trim() || entry.content_key;
    const poolKey = entry.content_key;
    buckets[poolKey] = emptyPoolTerm(poolKey, label);
    for (const alias of [poolKey, poolContentKey(scope, entry.lemma), lemmaNorm(entry.lemma)]) {
      if (alias) {
        keyToPool[alias] = poolKey;
      }
    }
  }

  for (const term of terms) {
    let poolKey: string | undefined;
    for (const candidate of [
      term.content_key,
      stripFieldSuffix(term.content_key),
      lemmaNorm(term.label),
      lemmaNorm(term.content_key.split(":").pop() ?? ""),
    ]) {
      if (candidate && keyToPool[candidate]) {
        poolKey = keyToPool[candidate];
        break;
      }
    }
    if (!poolKey) {
      continue;
    }
    buckets[poolKey] = addTerm(buckets[poolKey], term);
  }

  return Object.values(buckets);
}

export function catalogPoolSize(scope: string): number {
  return CATALOG_POOLS[scope]?.length ?? 0;
}
