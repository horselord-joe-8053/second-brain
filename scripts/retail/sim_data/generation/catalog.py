"""Issue themes, geography, and phrasing catalog for simulated tickets."""

from __future__ import annotations

MODELS = ("Galaxy A15 5G", "Galaxy A16 5G", "Galaxy A25 5G")
CITIES = (
    ("Sydney", "NSW"),
    ("Melbourne", "VIC"),
    ("Brisbane", "QLD"),
    ("Perth", "WA"),
    ("Adelaide", "SA"),
    ("Canberra", "ACT"),
)

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

PARAPHRASE_BY_ISSUE: dict[str, str] = {
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

# Hybrid B-lift: bait issue index → gold issue index (teaching pairs).
HYBRID_GOLD_BY_BAIT_IDX: tuple[tuple[int, int], ...] = (
    (2, 0),   # handover bait → black screen gold (A15 Sydney class)
    (12, 10), # ghost touch bait → fingerprint gold
    (5, 10),  # NFC bait → fingerprint gold (mis-route city)
)
