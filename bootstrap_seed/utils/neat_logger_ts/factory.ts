/** Role-based logger factory (mirrors Python NeatLoggerFactory subset). */

import { loadNeatLoggerConfig, NeatLoggerConfig } from "./config";
import { NeatLogger } from "./logger";

let frontendMonitorLogger: NeatLogger | undefined;

export class NeatLoggerFactory {
  static frontendMonitor(overrides: Partial<NeatLoggerConfig> = {}): NeatLogger {
    if (!frontendMonitorLogger) {
      const cfg = loadNeatLoggerConfig("frontend_monitor");
      Object.assign(cfg, overrides);
      frontendMonitorLogger = new NeatLogger(cfg);
    }
    return frontendMonitorLogger;
  }

  /** Vitest isolation — reset singletons between tests. */
  static resetForTests(): void {
    frontendMonitorLogger = undefined;
  }
}
