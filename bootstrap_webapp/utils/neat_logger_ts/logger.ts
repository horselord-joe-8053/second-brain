/** Scoped CLI logger: colored stdout/stderr + plain file mirror. */

import { appendPlainLine, NeatLoggerConfig, resolveRepoRoot } from "./config";
import {
  formatLogPrefixColored,
  formatLogPrefixPlain,
  shouldColorTty,
  stripAnsi,
} from "./prefix";
import { styledTtyAndFile } from "./tagStyle";

/** Same violet as Python ``_heartbeat_badge`` so heartbeat lines scan apart from INFO. */
const VIOLET = "\u001b[38;5;129m";
const NC = "\u001b[0m";

export type HeartbeatOptions = {
  /** Seconds between ticks. Omitted uses config ``heartbeat_interval_sec`` (minimum 1). */
  intervalSec?: number;
  /** After this many seconds, emit one warning. Does not stop the work. */
  softWallSec?: number;
  /**
   * Log success or failure when ``stop`` runs.
   * Defaults to true, matching Python ``with Heartbeat(...)``.
   */
  announceComplete?: boolean;
};

/**
 * Periodic progress lines while async work is in flight.
 *
 * Uses ``setInterval``, so the event loop must be free to turn. A tight
 * synchronous loop will not tick until it yields (unlike Python's thread).
 */
export class NeatLoggerHeartbeat {
  private readonly logger: NeatLogger;
  private readonly message: string;
  private readonly intervalSec: number;
  private readonly softWallSec: number | undefined;
  private readonly announceComplete: boolean;
  private timer: ReturnType<typeof setInterval> | undefined;
  private readonly startedAt = Date.now();
  private softWallLogged = false;
  private stopped = false;

  constructor(
    logger: NeatLogger,
    message: string,
    intervalSec: number,
    softWallSec: number | undefined,
    announceComplete: boolean,
  ) {
    this.logger = logger;
    this.message = message;
    this.intervalSec = intervalSec;
    this.softWallSec = softWallSec;
    this.announceComplete = announceComplete;
    this.timer = setInterval(() => this.tick(), this.intervalSec * 1000);
    const handle = this.timer as { unref?: () => void };
    handle.unref?.();
  }

  private tick(): void {
    if (this.stopped) {
      return;
    }
    const elapsed = Math.floor((Date.now() - this.startedAt) / 1000);
    if (
      this.softWallSec !== undefined &&
      this.softWallSec > 0 &&
      elapsed > this.softWallSec &&
      !this.softWallLogged
    ) {
      this.logger.warning(
        `[HEARTBEAT] Still running after ${Math.round(this.softWallSec)}s (soft wall): ${this.message}`,
      );
      this.softWallLogged = true;
    }
    const body = `${this.message} … (${elapsed}s elapsed)`;
    this.logger.infoTtyPlain({
      ttyMsg: `${VIOLET}[HEARTBEAT]${NC} ${body}`,
      fileMsg: `[HEARTBEAT] ${body}`,
    });
  }

  /** Stop the timer. Pass an error to log failure when announceComplete is set. */
  stop(error?: unknown): void {
    if (this.stopped) {
      return;
    }
    this.stopped = true;
    if (this.timer !== undefined) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
    if (!this.announceComplete) {
      return;
    }
    const elapsed = Math.floor((Date.now() - this.startedAt) / 1000);
    if (error !== undefined) {
      this.logger.error(`Task failed: '${this.message}' (after ${elapsed}s)`);
    } else {
      this.logger.success(`Task completed: '${this.message}' (took ${elapsed}s)`);
    }
  }

  /** Clears the timer without a completion line, so a thrown error is not logged as success. */
  [Symbol.dispose](): void {
    if (this.stopped) {
      return;
    }
    this.stopped = true;
    if (this.timer !== undefined) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }
}

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

  /**
   * Start a heartbeat. Call ``stop()`` when the work finishes, or use ``withHeartbeat``.
   * ``Symbol.dispose`` only clears the timer (no success line).
   */
  heartbeat(message: string, opts: HeartbeatOptions = {}): NeatLoggerHeartbeat {
    const raw = opts.intervalSec ?? this.cfg.heartbeat_interval_sec;
    const intervalSec = Math.max(1, Number.isFinite(raw) ? raw : 20);
    return new NeatLoggerHeartbeat(
      this,
      message,
      intervalSec,
      opts.softWallSec,
      opts.announceComplete ?? true,
    );
  }

  /** Async stand-in for Python ``with logger.Heartbeat(...)``. */
  async withHeartbeat<T>(
    message: string,
    work: () => Promise<T>,
    opts: HeartbeatOptions = {},
  ): Promise<T> {
    const beat = this.heartbeat(message, opts);
    try {
      const result = await work();
      beat.stop();
      return result;
    } catch (err) {
      beat.stop(err);
      throw err;
    }
  }
}
