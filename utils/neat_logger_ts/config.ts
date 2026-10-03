/** Load yaml config and resolve repo-relative log paths for neat_logger_ts. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

export type LogOutputMode = "stdout" | "file" | "both";

export type RoleConfig = {
  log_root: string;
  log_file_name: string;
  log_output: LogOutputMode;
  tag_prefix: string;
};

export type RawNeatLoggerYaml = {
  log_root?: string;
  log_output?: string;
  log_file_name?: string;
  heartbeat_interval_sec?: number;
  roles?: Record<string, Partial<RoleConfig>>;
};

const PKG_DIR = path.dirname(fileURLToPath(import.meta.url));
const FALLBACK_YAML = path.join(PKG_DIR, "neat_logger_fallback_config.yaml");

export class NeatLoggerConfig implements RoleConfig {
  log_root: string;
  log_file_name: string;
  log_output: LogOutputMode;
  tag_prefix: string;
  heartbeat_interval_sec: number;

  constructor(init: Partial<RoleConfig & { heartbeat_interval_sec?: number }> = {}) {
    this.log_root = init.log_root ?? "logs";
    this.log_file_name = init.log_file_name ?? "api.log";
    this.log_output = normalizeOutput(init.log_output ?? "both");
    this.tag_prefix = init.tag_prefix ?? "";
    this.heartbeat_interval_sec = init.heartbeat_interval_sec ?? 20;
  }

  resolvedLogPath(repoRoot: string): string {
    const root = path.isAbsolute(this.log_root)
      ? path.resolve(this.log_root)
      : path.resolve(repoRoot, this.log_root);
    return path.join(root, this.log_file_name);
  }
}

function normalizeOutput(raw: string): LogOutputMode {
  const mode = raw.trim().toLowerCase();
  if (mode === "stdout" || mode === "file" || mode === "both") {
    return mode;
  }
  return "both";
}

function readYamlFile(): RawNeatLoggerYaml {
  try {
    const text = fs.readFileSync(FALLBACK_YAML, "utf8");
    const data = parseYaml(text);
    return (data && typeof data === "object" ? data : {}) as RawNeatLoggerYaml;
  } catch {
    return {};
  }
}

function envOverride(keyTs: string, keyLegacy: string): string | undefined {
  const ts = process.env[keyTs]?.trim();
  if (ts) {
    return ts;
  }
  const legacy = process.env[keyLegacy]?.trim();
  return legacy || undefined;
}

function overlayEnv(base: RawNeatLoggerYaml): RawNeatLoggerYaml {
  const out: RawNeatLoggerYaml = { ...base };
  const root = envOverride("NEAT_LOGGER_TS_LOG_ROOT", "NEAT_LOGGER_LOG_ROOT");
  if (root) {
    out.log_root = root;
  }
  const mode = envOverride("NEAT_LOGGER_TS_LOG_OUTPUT", "NEAT_LOGGER_LOG_OUTPUT");
  if (mode) {
    out.log_output = mode;
  }
  const fname = envOverride("NEAT_LOGGER_TS_LOG_FILE_NAME", "NEAT_LOGGER_LOG_FILE_NAME");
  if (fname) {
    out.log_file_name = fname;
  }
  const hb = envOverride(
    "NEAT_LOGGER_TS_HEARTBEAT_INTERVAL_SEC",
    "NEAT_LOGGER_HEARTBEAT_INTERVAL_SEC",
  );
  if (hb) {
    const n = Number(hb);
    if (Number.isFinite(n) && n >= 1) {
      out.heartbeat_interval_sec = n;
    }
  }
  return out;
}

export function resolveRepoRoot(): string {
  const env = process.env.REPO_ROOT?.trim();
  if (env) {
    return path.resolve(env);
  }
  return path.resolve(PKG_DIR, "../..");
}

export function loadNeatLoggerConfig(role?: string): NeatLoggerConfig {
  const raw = overlayEnv(readYamlFile());
  const hb = Number(raw.heartbeat_interval_sec ?? 20);
  const base = new NeatLoggerConfig({
    log_root: raw.log_root,
    log_file_name: raw.log_file_name,
    log_output: normalizeOutput(String(raw.log_output ?? "both")),
    heartbeat_interval_sec: Number.isFinite(hb) && hb >= 1 ? hb : 20,
  });
  if (!role) {
    return base;
  }
  const roleCfg = raw.roles?.[role];
  if (!roleCfg) {
    return base;
  }
  return new NeatLoggerConfig({
    log_root: roleCfg.log_root ?? base.log_root,
    log_file_name: roleCfg.log_file_name ?? base.log_file_name,
    log_output: normalizeOutput(String(roleCfg.log_output ?? base.log_output)),
    tag_prefix: roleCfg.tag_prefix ?? base.tag_prefix,
    heartbeat_interval_sec: base.heartbeat_interval_sec,
  });
}

export function ensureParentDir(filePath: string): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

export function appendPlainLine(filePath: string, line: string): void {
  ensureParentDir(filePath);
  fs.appendFileSync(filePath, line.endsWith("\n") ? line : `${line}\n`, "utf8");
}
