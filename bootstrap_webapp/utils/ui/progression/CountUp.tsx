/**
 * Animated integer counter — used on level-up EARNED stat (v9 mockup).
 */
import { useEffect, useState } from "react";

export type CountUpProps = {
  from: number;
  to: number;
  ms?: number;
  delayMs?: number;
};

export function CountUp({ from, to, ms = 1000, delayMs = 0 }: CountUpProps) {
  const [value, setValue] = useState(from);

  useEffect(() => {
    let raf = 0;
    const timer = window.setTimeout(() => {
      const start = performance.now();
      const tick = (now: number) => {
        const k = Math.min(1, (now - start) / ms);
        const eased = 1 - (1 - k) ** 3;
        setValue(Math.round(from + (to - from) * eased));
        if (k < 1) raf = requestAnimationFrame(tick);
      };
      raf = requestAnimationFrame(tick);
    }, delayMs);
    return () => {
      window.clearTimeout(timer);
      cancelAnimationFrame(raf);
    };
  }, [from, to, ms, delayMs]);

  return <>{value}</>;
}
