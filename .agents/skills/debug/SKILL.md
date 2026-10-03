# debug

Reproduce first, then fix.

1. Reproduce with the smallest command (pytest path, vitest path, or `./scripts/verify.sh`).
2. Identify the seam (API, UI, config) from failure output.
3. Fix with a test when fixing behavior; rerun verify.
