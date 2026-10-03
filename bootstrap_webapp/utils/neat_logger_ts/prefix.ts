/** Timestamp + level prefix with [TS] runtime tag (Phase B adds [PY] in Python). */

export const NC = "\u001b[0m";
export const BLUE = "\u001b[0;34m";
export const GREEN = "\u001b[0;32m";
export const YELLOW = "\u001b[1;33m";
export const RED = "\u001b[0;31m";

export type LogLevel = "INFO" | "SUCCESS" | "WARNING" | "ERROR";

function formatTimestamp(): string {
  const now = new Date();
  const ms = String(now.getMilliseconds()).padStart(3, "0");
  const base = now.toISOString().slice(0, 19).replace("T", " ");
  const tz =
    Intl.DateTimeFormat(undefined, { timeZoneName: "short" })
      .formatToParts(now)
      .find((p) => p.type === "timeZoneName")?.value ?? "UTC";
  return `${base}.${ms} ${tz}`;
}

function levelColor(level: LogLevel): string {
  switch (level) {
    case "INFO":
      return BLUE;
    case "SUCCESS":
      return GREEN;
    case "WARNING":
      return YELLOW;
    case "ERROR":
      return RED;
    default:
      return NC;
  }
}

export function formatLogPrefixPlain(level: LogLevel): string {
  return `[${formatTimestamp()}] [TS] [${level}] `;
}

export function formatLogPrefixColored(level: LogLevel): string {
  const color = levelColor(level);
  return `[${formatTimestamp()}] [TS] ${color}[${level}]${NC} `;
}

export function shouldColorTty(): boolean {
  return Boolean(process.env.PGLPL_FORCE_COLOR) || Boolean(process.stdout.isTTY);
}

export function stripAnsi(text: string): string {
  return text.replace(/\u001b\[[0-9;]*m/g, "");
}
