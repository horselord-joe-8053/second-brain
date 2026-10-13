#!/usr/bin/env python3.12
"""Generate natural llm_gen profile corpus (60 + 10) per REFACTOR_RETAIL_LLM_CORPUS_V2_NATURAL.md.

Deterministic seed for reproducibility; operators may instead use tmp/simulated_data/prompt_v2.txt
with an external LLM author.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts" / "retail"))

MODELS = ("Galaxy A15 5G", "Galaxy A16 5G", "Galaxy A25 5G")
CITIES = (
    ("Sydney", "NSW"),
    ("Melbourne", "VIC"),
    ("Brisbane", "QLD"),
    ("Perth", "WA"),
    ("Adelaide", "SA"),
    ("Canberra", "ACT"),
)

# 20 distinct issue themes (index i uses ISSUES[i % 20] + per-row detail).
ISSUES: tuple[tuple[str, str], ...] = (
    ("black screen after calls", "Reseated display flex and updated panel firmware."),
    ("battery drain while idle", "Recalibrated battery stats and removed rogue sync job."),
    ("5G handover drops data", "Reset network profile and verified carrier VoLTE."),
    ("rear camera blur and hunt", "Cleaned lens module and recalibrated autofocus."),
    ("USB-C charging intermittent", "Cleaned port debris and replaced charge flex."),
    ("NFC tap-to-pay silent fail", "Reset NFC stack and reissued wallet token."),
    ("Bluetooth car pairing loop", "Cleared pairing cache and refreshed BT firmware."),
    ("microphone faint on calls", "Replaced mic grille seal and tested VoLTE path."),
    ("storage full with few apps", "Cleared system cache partition and indexed media."),
    ("Wi-Fi drops on sleep", "Disabled aggressive Wi-Fi scanning in sleep policy."),
    ("fingerprint reader slow", "Re-enrolled prints after sensor cleaning."),
    ("overheat during video chat", "Applied thermal patch and limited background camera use."),
    ("ghost touches near edges", "Replaced touch digitizer after isolation test."),
    ("software update loop", "Flashed recovery image and staged OTA again."),
    ("SIM tray not detected", "Reseated tray and inspected SIM pins."),
    ("speaker crackle at volume", "Updated audio DSP and replaced speaker foam."),
    ("mobile hotspot auth fail", "Reset tethering profile and carrier APN."),
    ("app crash on launch", "Wiped app partition cache and updated Play services."),
    ("GPS drift in maps", "Reloaded GNSS assistance data and recalibrated compass."),
    ("eSIM profile switch fail", "Removed stale eSIM profile and reprovisioned."),
)

DETAIL_SLOTS = (
    "Started after a weekend road trip.",
    "Only reproducible on the first unlock of the day.",
    "Worse when battery is below twenty percent.",
    "Customer noticed it after installing a banking app.",
    "Happens on both Wi-Fi and cellular.",
    "No physical damage reported.",
    "Safe mode shows the same behaviour.",
    "Issue began following a security patch.",
    "Intermittent for two weeks then constant.",
    "Retail demo unit could not reproduce initially.",
)


@dataclass
class TicketRow:
    ticket_id: str
    item_number: str
    store_id: str
    city: str
    state: str
    model: str
    status: str
    customer_query_text: str
    resolution_text: str
    opened_at: str
    updated_at: str
    closed_at: str
    has_sam_e: bool
    sam_e: str | None


def _sam_code(n: int) -> str:
    return f"SAM-E{100 + n:03d}"


def _build_stored_text(
    rng: random.Random,
    *,
    index: int,
    model: str,
    city: str,
    state: str,
    issue: str,
    with_code: bool,
    code: str | None,
) -> str:
    opening = rng.choice(
        (
            f"Customer reports: {issue} on {model} in {city}, {state}.",
            f"Shop note: shopper describes {issue} on their {model} ({city}).",
            f"Intake: {model} owner in {city}, {state} — {issue}.",
            f"Need help with {model}: {issue} (visited {city} store).",
        )
    )
    detail = DETAIL_SLOTS[index % len(DETAIL_SLOTS)]
    extra = f" Ticket context #{index}: {rng.choice(('no case', 'no drops', 'original charger', 'dual SIM'))}."
    body = f"{opening} {detail}{extra}"
    if with_code and code:
        style = rng.choice(
            (
                f" Phone displayed {code} on the service menu.",
                f" Diagnostic {code} appeared in Samsung Members.",
                f" Technician later confirmed {code} in the log.",
            )
        )
        body = f"{body} {style}"
    return body.strip()


def generate_historical(seed: int, count: int = 60) -> list[TicketRow]:
    rng = random.Random(seed)
    rows: list[TicketRow] = []
    for i in range(count):
        model = MODELS[i % len(MODELS)]
        city, state = CITIES[i % len(CITIES)]
        issue, fix = ISSUES[i % len(ISSUES)]
        with_code = i % 2 == 0  # 50% with SAM-E
        code = _sam_code(i // 2) if with_code else None
        status = "received" if i % 5 == 4 else "resolved"
        text = _build_stored_text(
            rng,
            index=i,
            model=model,
            city=city,
            state=state,
            issue=issue,
            with_code=with_code,
            code=code,
        )
        closed = "2025-01-03T10:00:00Z" if status == "resolved" else ""
        res = fix if status == "resolved" else ""
        rows.append(
            TicketRow(
                ticket_id=f"T-0042-{i:06d}",
                item_number=f"ITM-{i:08d}",
                store_id=f"ST-{i:04d}",
                city=city,
                state=state,
                model=model,
                status=status,
                customer_query_text=text,
                resolution_text=res,
                opened_at="2025-01-01T10:00:00Z",
                updated_at="2025-01-02T10:00:00Z",
                closed_at=closed,
                has_sam_e=with_code,
                sam_e=code,
            )
        )
    return rows


def _paraphrase_issue(issue: str, rng: random.Random) -> str:
    swaps = {
        "black screen after calls": "screen stays black when answering calls",
        "battery drain while idle": "battery empties overnight with minimal use",
        "5G handover drops data": "mobile data cuts out when switching to 5G",
        "rear camera blur and hunt": "camera hunts focus and saves blurry shots",
        "USB-C charging intermittent": "charging stops unless the cable is held at an angle",
        "NFC tap-to-pay silent fail": "contactless payments do nothing at the terminal",
        "Bluetooth car pairing loop": "car Bluetooth keeps failing during pairing",
        "microphone faint on calls": "callers can barely hear me unless on speaker",
        "storage full with few apps": "storage shrinks even after deleting photos",
        "Wi-Fi drops on sleep": "Wi-Fi disconnects every time the screen turns off",
        "fingerprint reader slow": "fingerprint unlock takes several attempts",
        "overheat during video chat": "video calls make the phone very hot quickly",
        "ghost touches near edges": "screen registers taps I did not make",
        "software update loop": "update downloads but never finishes installing",
        "SIM tray not detected": "SIM is inserted but the phone shows no SIM",
        "speaker crackle at volume": "speaker distorts at medium volume",
        "mobile hotspot auth fail": "hotspot clients connect but get no internet",
        "app crash on launch": "banking app closes immediately on open",
        "GPS drift in maps": "maps location jumps blocks away outdoors",
        "eSIM profile switch fail": "eSIM switch hangs on verifying profile",
    }
    return swaps.get(issue, issue)


def generate_eval(rows: list[TicketRow], seed: int) -> list[dict]:
    rng = random.Random(seed + 1)
    resolved = [r for r in rows if r.status == "resolved"]
    # Spread gold across models/issues: every 4th resolved index
    gold = [resolved[i] for i in range(0, min(40, len(resolved)), 4)][:10]
    eval_rows: list[dict] = []
    code_in_query_flags: list[bool] = []
    for g in gold:
        if g.has_sam_e:
            code_in_query_flags.append(len(code_in_query_flags) % 2 == 0)
        else:
            code_in_query_flags.append(False)

    for n, g in enumerate(gold):
        issue_key = ISSUES[int(g.ticket_id.split("-")[-1]) % len(ISSUES)][0]
        issue_p = _paraphrase_issue(issue_key, rng)
        caller = rng.choice(("Jordan", "Sam", "Casey", "Riley", "Morgan", "Taylor"))
        include_code = code_in_query_flags[n] and g.sam_e
        if include_code:
            q = (
                f"Need help: {caller} in {g.city} with a {g.model} — {issue_p}. "
                f"Also seeing reference {g.sam_e} in the support app."
            )
            stratum = "code_in_query"
        else:
            q = f"Need help: {caller} in {g.city} with a {g.model} — {issue_p}."
            if "SM-" in g.customer_query_text:
                stratum = "literal_token"
                q += " Mentioned model code SM-A156 during intake."
            else:
                stratum = "paraphrase"
        eval_rows.append(
            {
                "eval_id": f"eval-{n + 1:04d}",
                "query": q,
                "model_filter": g.model,
                "expected_ticket_ids": [g.ticket_id],
                "stratum": stratum,
                "source_ticket_id": g.ticket_id,
            }
        )
    return eval_rows


def write_csv(path: Path, rows: list[TicketRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ticket_id",
        "item_number",
        "store_id",
        "city",
        "state",
        "model",
        "status",
        "customer_query_text",
        "resolution_text",
        "opened_at",
        "updated_at",
        "closed_at",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "ticket_id": r.ticket_id,
                    "item_number": r.item_number,
                    "store_id": r.store_id,
                    "city": r.city,
                    "state": r.state,
                    "model": r.model,
                    "status": r.status,
                    "customer_query_text": r.customer_query_text,
                    "resolution_text": r.resolution_text,
                    "opened_at": r.opened_at,
                    "updated_at": r.updated_at,
                    "closed_at": r.closed_at,
                }
            )


def write_manifest(path: Path, rows: list[TicketRow], seed: int) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(
                json.dumps(
                    {
                        "ticket_id": r.ticket_id,
                        "model": r.model,
                        "status": r.status,
                        "seed": seed,
                        "customer_query_text": r.customer_query_text,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def write_eval(path: Path, eval_rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in eval_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=20261012)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "tmp" / "simulated_data",
    )
    args = p.parse_args()
    rows = generate_historical(args.seed)
    eval_rows = generate_eval(rows, args.seed)
    out = args.out_dir
    write_csv(out / "service_queries.csv", rows)
    write_manifest(out / "ticket_manifest.jsonl", rows, args.seed)
    write_eval(out / "ticket_retrieval.jsonl", eval_rows)
    sam = sum(1 for r in rows if r.has_sam_e)
    print(f"wrote {len(rows)} tickets, {len(eval_rows)} eval rows, SAM-E rows={sam} -> {out}")


if __name__ == "__main__":
    main()
