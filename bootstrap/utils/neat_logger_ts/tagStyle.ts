/** Load config/logging.yaml tag colors (shared with Python neat_logger). */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

import { resolveRepoRoot } from "./config";

const PKG_DIR = path.dirname(fileURLToPath(import.meta.url));
const FALLBACK_YAML = path.join(PKG_DIR, "neat_logger_fallback_config.yaml");

const COLOR_CODES: Record<string, string> = {
  red: "\u001b[0;31m",
  green: "\u001b[0;32m",
  yellow: "\u001b[0;33m",
  cyan: "\u001b[0;36m",
  magenta: "\u001b[0;35m",
  blue: "\u001b[0;34m",
  purple: "\u001b[38;5;129m",
  orange: "\u001b[38;5;208m",
};

const NC = "\u001b[0m";

const DEFAULT_EXACT: Record<string, string> = {
  "[LLM-REQUEST]": "red",
  "[LLM-RESPONSE]": "green",
  "[LLM-USAGE][RECEIVED]": "green",
  "[LLM-USAGE][ESTIMATED]": "green",
  "[LLM-VERIFY-LOCAL]": "yellow",
  "[LLM-VERIFY-FINAL]": "yellow",
  "[VERIFY-SELF-CONTRADICT]": "yellow",
  "[LLM-ERROR]": "red",
  "[LLM-PROMPT-SIZE]": "cyan",
  "[PARAGRAPH-SENSE-ANCHOR]": "magenta",
  "[PARAGRAPH-HOST-LEADING]": "cyan",
};

const DEFAULT_PREFIX: Record<string, string> = {
  "[EXPGTEST_": "purple",
  "[PWLAD_": "orange",
};

type TagStylesYaml = {
  exact?: Record<string, string>;
  prefix?: Record<string, string>;
};

type ProjectLoggingYaml = {
  tag_styles?: TagStylesYaml;
  ansi_in_file_env?: string;
  legacy_ansi_in_file_env?: string;
};

let cache: { exact: Record<string, string>; prefix: Record<string, string> } | undefined;

function readYamlFile(filePath: string): Record<string, unknown> {
  try {
    const text = fs.readFileSync(filePath, "utf8");
    const data = parseYaml(text);
    return data && typeof data === "object" ? (data as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

function readFallbackYaml(): Record<string, unknown> {
  return readYamlFile(FALLBACK_YAML);
}

function resolveProjectLogConfigPath(): string | undefined {
  const fallback = readFallbackYaml();
  const rel = String(fallback.project_log_config ?? "").trim();
  if (!rel) {
    return undefined;
  }
  const p = path.isAbsolute(rel) ? path.resolve(rel) : path.resolve(resolveRepoRoot(), rel);
  return p;
}

function colorCode(name: string): string {
  return COLOR_CODES[name.trim().toLowerCase()] ?? NC;
}

function parseStyles(raw: ProjectLoggingYaml): {
  exact: Record<string, string>;
  prefix: Record<string, string>;
} {
  const block = raw.tag_styles ?? {};
  const exactRaw = block.exact ?? {};
  const prefixRaw = block.prefix ?? {};

  const exact: Record<string, string> = {};
  for (const [tag, colorName] of Object.entries({ ...DEFAULT_EXACT, ...exactRaw })) {
    exact[tag] = colorCode(String(colorName));
  }

  const prefix: Record<string, string> = {};
  for (const [pref, colorName] of Object.entries({ ...DEFAULT_PREFIX, ...prefixRaw })) {
    prefix[pref] = colorCode(String(colorName));
  }

  return { exact, prefix };
}

export function reloadTagStyles(): void {
  cache = undefined;
}

function loadStyles(): { exact: Record<string, string>; prefix: Record<string, string> } {
  if (cache) {
    return cache;
  }
  const cfgPath = resolveProjectLogConfigPath();
  const raw = cfgPath && fs.existsSync(cfgPath) ? (readYamlFile(cfgPath) as ProjectLoggingYaml) : {};
  cache = parseStyles(raw);
  return cache;
}

export function styledAnsiInFile(): boolean {
  const cfgPath = resolveProjectLogConfigPath();
  const raw =
    cfgPath && fs.existsSync(cfgPath) ? (readYamlFile(cfgPath) as ProjectLoggingYaml) : {};
  for (const key of ["ansi_in_file_env", "legacy_ansi_in_file_env"] as const) {
    const envKey = String(raw[key] ?? "").trim();
    if (envKey && ["1", "true", "yes"].includes(String(process.env[envKey] ?? "").trim().toLowerCase())) {
      return true;
    }
  }
  if (["1", "true", "yes"].includes(String(process.env.NEAT_LOGGER_STYLED_ANSI_IN_FILE ?? "").trim().toLowerCase())) {
    return true;
  }
  return ["1", "true", "yes"].includes(String(process.env.NEAT_LOGGER_LLM_ANSI_IN_FILE ?? "0").trim().toLowerCase());
}

export function shouldStyleTty(): boolean {
  return Boolean(process.env.PGLPL_FORCE_COLOR) || Boolean(process.stdout.isTTY);
}

export function styleConfiguredTags(msg: string): string {
  if (!msg.includes("[")) {
    return msg;
  }

  const { exact, prefix } = loadStyles();
  const exactTags = Object.keys(exact).sort((a, b) => b.length - a.length);
  const prefixItems = Object.entries(prefix).sort((a, b) => b[0].length - a[0].length);

  const out: string[] = [];
  let i = 0;
  while (i < msg.length) {
    if (msg[i] !== "[") {
      out.push(msg[i] ?? "");
      i += 1;
      continue;
    }

    let matched = false;
    for (const tag of exactTags) {
      if (msg.startsWith(tag, i)) {
        out.push(`${exact[tag]}${tag}${NC}`);
        i += tag.length;
        matched = true;
        break;
      }
    }
    if (matched) {
      continue;
    }

    const end = msg.indexOf("]", i);
    if (end < 0) {
      out.push(msg.slice(i));
      break;
    }

    const token = msg.slice(i, end + 1);
    let styled: string | undefined;
    for (const [pref, code] of prefixItems) {
      if (token.startsWith(pref)) {
        styled = `${code}${token}${NC}`;
        break;
      }
    }
    out.push(styled ?? token);
    i = end + 1;
  }

  return out.join("");
}

export function styledTtyAndFile(msg: string): { tty: string; fileMsg: string } {
  const tty = shouldStyleTty() ? styleConfiguredTags(msg) : msg;
  const fileMsg = styledAnsiInFile() ? tty : msg;
  return { tty, fileMsg };
}
