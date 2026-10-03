/** Scoped CLI logger: colored stdout/stderr + plain file mirror. */

import { appendPlainLine, NeatLoggerConfig, resolveRepoRoot } from "./config";
import {
  formatLogPrefixColored,
  formatLogPrefixPlain,
  shouldColorTty,
  stripAnsi,
} from "./prefix";
import { styledTtyAndFile } from "./tagStyle";

export class NeatLogger {
  private readonly cfg: NeatLoggerConfig;

  constructor(cfg: NeatLoggerConfig) {
    this.cfg = cfg;
  }

  private tag(msg: string): string {
    const prefix = this.cfg.tag_prefix?.trim();
    return prefix ? `${prefix} ${msg}` : msg;
  }

  private emit(
    level: "INFO" | "SUCCESS" | "WARNING" | "ERROR",
    msg: string,
    stream: NodeJS.WritableStream,
  ): void {
    const body = this.tag(msg);
    const plain = `${formatLogPrefixPlain(level)}${body}\n`;
    const coloredBody = shouldColorTty() ? body : stripAnsi(body);
    const colored = `${formatLogPrefixColored(level)}${coloredBody}`;

    if (this.cfg.log_output === "file" || this.cfg.log_output === "both") {
      try {
        appendPlainLine(this.cfg.resolvedLogPath(resolveRepoRoot()), plain.trimEnd());
      } catch {
        // Sink failure must not crash Playwright runs.
      }
    }
    if (this.cfg.log_output === "stdout" || this.cfg.log_output === "both") {
      try {
        stream.write(`${colored}\n`);
      } catch {
        // ignore broken pipe / detached stdout
      }
    }
  }

  info(msg: string): void {
    this.emit("INFO", msg, process.stdout);
  }

  success(msg: string): void {
    this.emit("SUCCESS", msg, process.stdout);
  }

  warning(msg: string): void {
    this.emit("WARNING", msg, process.stdout);
  }

  error(msg: string): void {
    this.emit("ERROR", msg, process.stderr);
  }

  styledInfo(msg: string): void {
    const { tty, fileMsg } = styledTtyAndFile(msg);
    this.infoTtyPlain({ ttyMsg: tty, fileMsg });
  }

  styledError(msg: string): void {
    const { tty, fileMsg } = styledTtyAndFile(msg);
    this.errorTtyPlain({ ttyMsg: tty, fileMsg });
  }

  /** TTY may include ANSI (e.g. purple progress); file mirror stays plain body only. */
  infoTtyPlain({ ttyMsg, fileMsg }: { ttyMsg: string; fileMsg: string }): void {
    const plainBody = this.tag(fileMsg);
    const plain = `${formatLogPrefixPlain("INFO")}${plainBody}\n`;

    if (this.cfg.log_output === "file" || this.cfg.log_output === "both") {
      try {
        appendPlainLine(this.cfg.resolvedLogPath(resolveRepoRoot()), plain.trimEnd());
      } catch {
        // ignore
      }
    }
    if (this.cfg.log_output === "stdout" || this.cfg.log_output === "both") {
      const ttyBody = this.tag(ttyMsg);
      const coloredPrefix = shouldColorTty()
        ? formatLogPrefixColored("INFO")
        : formatLogPrefixPlain("INFO");
      try {
        process.stdout.write(`${coloredPrefix}${ttyBody}\n`);
      } catch {
        // ignore
      }
    }
  }

  errorTtyPlain({ ttyMsg, fileMsg }: { ttyMsg: string; fileMsg: string }): void {
    const plainBody = this.tag(fileMsg);
    const plain = `${formatLogPrefixPlain("ERROR")}${plainBody}\n`;

    if (this.cfg.log_output === "file" || this.cfg.log_output === "both") {
      try {
        appendPlainLine(this.cfg.resolvedLogPath(resolveRepoRoot()), plain.trimEnd());
      } catch {
        // ignore
      }
    }
    if (this.cfg.log_output === "stdout" || this.cfg.log_output === "both") {
      const ttyBody = this.tag(ttyMsg);
      const coloredPrefix = shouldColorTty()
        ? formatLogPrefixColored("ERROR")
        : formatLogPrefixPlain("ERROR");
      try {
        process.stderr.write(`${coloredPrefix}${ttyBody}\n`);
      } catch {
        // ignore
      }
    }
  }
}
