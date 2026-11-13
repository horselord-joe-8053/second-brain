# Technician knowledge handover — Samsung Fast Track Troubleshooting

**Sole source:** *Fast Track Troubleshooting* service-data sheet for **RF28K9070 / RF22K9381 / RF28K9380**, production reference **DRRF28K9070 – 060616**; 12 PDF pages. The cover is titled **Fast Track Troubleshooting** (not the filename `repair-guide.pdf`). This file was authored from **this 12-page PDF alone**, without using any user manual, earlier work, or other Samsung model knowledge. `[DOCUMENTED]` = stated/shown in this specific repair sheet; `[UNKNOWN]` = not established here. All references below are PDF page numbers (the sheet itself is mostly unnumbered).

> **MANDATORY AUDIENCE AND SAFETY BOUNDARY — TECHNICIANS ONLY.** The opening notice expressly restricts the sheet to persons with adequate appliance electrical/electronic/mechanical trade knowledge, and warns of injury or property damage. The sheet includes powered high-voltage measurements and forcing heaters/compressor/fans. **Never relay these physical procedures to an untrained customer or graduate without qualified onsite supervision.** A customer-support AI can safely interpret error categories and direct to a qualified Samsung repairer; detailed testing is only for authorized, competent technicians. The manufacturer/seller disclaims responsibility for misuse of the sheet (p. 1).

## Source applicability and help — SR-IDENTIFY-001 [DOCUMENTED; p. 1]

The cover explicitly names **RF28K9070**, **RF22K9381**, **RF28K9380**. This is not a statement that every fault applies identically to all suffixes; identify actual PCB/feature variant and check service sheet. Printed technical contact references: ASC/SSD **1-888-751-4086**, FE/ME **1-866-894-0637**; GSPN `http://gspn3.samsungcsportal.com/main.jsp`, e-learning `samsungasc.earlyconnect.com`, educational support **1-800-749-9421** / `e-learning@sea.samsung.com`. These are historical contact values printed in the sheet; not live-verified.

## Electrical safety and measurement ground — SR-SAFE-001 [DOCUMENTED; pp. 1–2, 5–6, 11–12]

- Use the **main PCB marked GND / circuit ground** as reference for any stated **DC voltage test**. The sheet says chassis ground produces **incorrect readings**. Do not casually interchange chassis and circuit ground. It does **not** endorse probing live mains by an untrained person.
- **Main board and inverter board** have **AC input and high voltage generated at SMPS PCB and inverter PCB power terminals**, prominent warning on p. 11. The available numbers do not remove shock/arc risk.
- Resistance measurements described after disconnecting a main PCB wire/harness explicitly say **power MUST be OFF**. Do not obtain resistance while energized. The document requires trade-level training; where PCB access, isolation, connector mapping or safe procedures cannot be verified, stop and consult certified service rather than improvising.
- Sensor resistance rule printed on p. 2: **over 100 kΩ = considered OPEN**, **under 2 kΩ = considered shorted**. A sensor can still be wrong when it is *out of tolerance* without meeting either threshold. Sheet also has a **freezer thermistor temperature/resistance/voltage chart**, p. 2. Use its exact chart for temperatures; do not fabricate intermediate readings absent proper interpretation.

## Four service interface entry modes — SR-MODES-001 [DOCUMENTED; p. 1]

All mode entry steps are **technician-only**; no ordinary customer should enter these to troubleshoot a generic cooling complaint.

| Mode | Button sequence printed by service sheet | Indication / exit |
|---|---|---|
| Demo / Cooling Off | Hold **Freezer + Fridge + Door Alarm 6 seconds** | `0–FF` displayed; repeat combination to exit |
| Load Mode | Hold **Freezer + Fridge + Flex Zone 6 seconds** | All ON/OFF LEDs blink; release to display operating-load status; p. 3 maps indicator segments |
| Diagnostic / Error display | Hold **Freezer + Fridge 6 seconds** until display blinks; continue holding until display blank or errors appear | Automatically exits after **1 minute**; error reference pp. 4–6 |
| Force / Defrost | Hold **Freezer + Flex Zone 6 seconds** until display blank and beep, then press **Flex Zone** to select successive force stages | Modes **1–5** shown as segment pictures; after mode 5 a blank screen and ~1-minute unattended exit; see forced-mode graph/table p. 1 |

**Important distinction:** these timing values come from *this repair service sheet* (6 seconds for the relevant modes). Do not replace them with any timings from a user guide or other model merely because button names look similar.

### Forced-operation meaning — SR-FORCE-001 [DOCUMENTED; p. 1]

The forced-mode diagram identifies states displayed as **FF**, **FF r**, **FF F**, **FF C**, **Fd**. It includes fan operation, compressor/temperature control and refrigerant flow valve routing. The **Fd** mode means **defrost: all heaters turned on**. The row for **FF** shows continuous freezer and fridge fans (as listed) and multiple valves swinging; **FF r/F/C** rows show different continuously driven fan/selected F/R/C valve combinations. This is not a user feature and can produce hazardous heat/equipment operation. Use the original p. 1 *Force Mode / Defrost* table/diagram to identify exactly which fan/valve is driven before activating; **do not assume the word 'r' is an error code**. Printed force-mode operating-time value for forced operations is **24 hr** in the table, while interface auto-exit behavior is a different **1 minute** display condition: don't conflate the two.

## Load Mode: LED location and device state — SR-LOAD-001 [DOCUMENTED; p. 3]

A load display is a **snapshot of currently commanded component state**, not proof the component physically runs. The table uses R compartment (refrigerator), F compartment (freezer) and CV/convertible zone display segments; lower-order-digit letters are **display segment identities**, not diagnostic error numbers.

| Operating element | Segment/location in load status | Meaning |
|---|---|---|
| R-fan highest | R lowest `a+b` | highest fridge fan state |
| R-fan high | R lowest `a` | high fridge fan state |
| R-fan low | R lowest `b` | low fridge fan state |
| Overload / hot ambient | R lowest `e` | external air **≥34°C** |
| Low ambient | R lowest `f` | external air **≤21°C** |
| Demo Mode | R lowest `g` | demo active |
| Compressor | F lowest `a` | commanded compressor state |
| F-fan highest | F lowest `b+c` | highest freezer fan state |
| F-fan high | F lowest `b` | high freezer fan state |
| F-fan low | F lowest `c` | low freezer fan state |
| Freezer defrost heater | F lowest `d` | freezer heater commanded |
| Convertible-zone fan highest | F lowest `e+f` | highest C-fan state |
| C-fan high | F lowest `e` | high C-fan state |
| C-fan low | F lowest `f` | low C-fan state |
| F valve | F second-lowest `b` | valve commanded open |
| CV valve | F second-lowest `c` | valve commanded open |
| R valve | F second-lowest `f` | valve commanded open |
| French-door heater | F second-lowest `g` | heater commanded |
| CV fan highest | `Freezer` + `Thin Ice` for CV compartment | highest convertible-zone fan |
| CV fan high | `Freezer` for CV compartment | high convertible-zone fan |
| CV fan low | `Thin Ice` for CV compartment | low convertible-zone fan |
| CV defrost heater | `Fridge` for CV compartment | convertible defrost heater on |
| Normal ambient | R lowest `e+f` LEDs off | external **22–33°C** |
| Ice-room fan | F second-lowest `d` | ice-room fan operating |
| Ice maker full | R second-lowest `e` | full bucket status |
| Wi-Fi indicator | display state | no AP/Internet OFF, router-only connection BLINK, Internet connected ON |

**Diagram reference:** *Load Mode* and the labeled display-segment graphic at printed PDF p. 3. Do not confuse low-order segments for sensor errors.

## Diagnostic mode codes: sensor faults — SR-DIAG-SENSOR [DOCUMENTED; p. 4]

First enter Diagnostic Mode with **Freezer + Fridge held 6 seconds**, and read error digits. The sheet frequently instructs checking open/short sensor and gives **main PCB** pin pairs with acceptable DC voltage windows. All physical measurements require qualified personnel, correct circuit ground, safe isolation/access and the exact PCB layout.

| Error code | Manual item | PCB contact / reference | Printed expected range |
|---:|---|---|---|
| 1 | Freezer sensor | CN30 pins **1–3** | **4.5–1.0 V DC** |
| 2 | Fridge sensor | CN30 **1–5** | **4.5–1.0 V DC** |
| 4 | Freezer defrost sensor | CN30 **1–4** | **4.5–1.0 V DC** |
| 5 | Fridge defrost sensor | CN30 **1–6** | **4.5–1.0 V DC** |
| 6 | Ambient sensor | CN30 **1–2** | **4.5–1.0 V DC** |
| 9 | Convertible-zone sensor | CN30 **11–12** | **4.1–0.8 V DC** |
| 11 | Convertible-zone defrost sensor | CN30 **11–13** | **4.1–0.8 V DC** |
| 13 | Humidity sensor | CN30 **7–9** | **4.1–0.8 V DC** |
| 14 | Fridge icemaker sensor | CN90 **3–8** | **4.5–1.0 V DC** |
| 15 | Ice room sensor | CN30 **10–11** | **4.5–1.0 V DC** |
| 16 | Fridge humidity sensor | CN30 **7–8** | **4.1–0.8 V DC** |

These voltages are **expected operating measurement ranges**, not a proof of all functional behavior. Out-of-range can be caused by sensor/circuit/connection issues; the source says inspect open or short, not indiscriminately replace a board. The sheet does not supply a universal voltage for every model/harness revision. Customer answer for these codes: report category and advise authorized service; do not suggest probing CN30 in the kitchen.

## Fan, heater, electrical and communication error matrix — SR-DIAG-POWER [DOCUMENTED; pp. 4–6]

| Code | Name | Printed diagnostic boundary or first check |
|---:|---|---|
| 21 | Freezer fan error | MAIN PCB **CN74 1↔4**, **7–12 V** |
| 22 | Fridge fan error | MAIN PCB **CN74 1↔3**, **7–12 V** |
| 23 | Compressor-room fan error | MAIN PCB **CN74 1↔6**, **7–12 V** |
| 24 | Freezer defrost error | **power OFF**, separate MAIN PCB CN70_1 wire; between **CN70_1-7 ↔ 3**, **63(230) Ω ±7%** depending input power; 0 Ω short, ∞ open wire/bimetal |
| 29 | Convertible-zone defrost error | **power OFF**, separate MAIN PCB CN70 wire; between **CN70_1-7 ↔ 1**, **63(230) Ω ±7%** depending input power; 0 Ω short, ∞ open wire/bimetal |
| 31 | Convertible-zone fan error | MAIN PCB **CN74 1↔5**, **7–12 V** |
| 35 | Freezer low register | Sheet literally shows `ERROR_Freezer low regist` without a usable electrical procedure |
| 37 | Convertible-zone low register | Sheet shows `ERROR_Convertible zone low regist` without diagnostic method |
| 39 | Icemaker function error | After changing ice maker, reconnect power and check operation (qualified service only) |
| 40 | Icemaker fan error | MAIN PCB **CN52-1 ↔ 6**, **7–12 V** |
| 41 | MAIN↔Panel communication error | Confirm cable problem, then oscilloscope investigation; sheet discusses board replacement after excluding wiring |
| 44 | MAIN↔Inverter communication error | Confirm cable problem, oscilloscope investigation, possible MAIN/inverter board replacement |
| 46 | I/O expander communication error | Sheet suggests main PCB replacement |
| 61 | Ice-duct heater error | **power OFF**, separate MAIN PCB CN51; **CN51 4↔6**, **135 Ω ±7%** (input-power dependent), 0 Ω short, ∞ open |
| 65 | Ice-bucket heater error | **power OFF**, separate MAIN PCB CN51; **CN51 4↔7**, **135 Ω ±7%**, 0 Ω short, ∞ open |
| 66 | Door-handle heater error | **power OFF**, separate MAIN PCB CN51; **CN51 1↔2**, **135 Ω ±7%**, 0 Ω short, ∞ open |
| 71 | Freezer abnormal temperature | Door held open, hot food/load can contribute; if condition resolves code disappears after predetermined period |
| 72 | Fridge abnormal temperature | Similar door/food investigation and resolution behavior |
| 73 | Convertible-zone chill error | Similar door/hot-food investigation and resolution behavior |
| 81 | Compressor run error | Check inverter PCB solder/shorted components, DC 15 V output **below 13.5 V**, compressor/cycle (qualified personnel) |
| 82 | Compressor IPM fault | Same inverter solder/short/DC 15 V **below 13.5 V** considerations |
| 83 | Compressor current error | Check compressor wiring, inverter PCB short/solder and compressor/cycle |
| 84 | Compressor motor stall | Check compressor/cycle, input voltage, inverter solder/short |
| 85 | Compressor low voltage | Sheet says occurs when input **AC 106 V or lower**; check input voltage via qualified service |

**Electrical caution:** the `63(230) ohm` notation is **preserved exactly as the service sheet prints it**, apparently reflecting input-voltage variation; the sheet does *not* fully define a precise model/region conversion in its text. Do not silently choose 63 vs 230 for a specific appliance without verifying its labeled voltage and original table. These are service checks, not customer-performed actions. Some p. 5 values display source ambiguities (e.g. 135 Ω line formatting); verify exact image and connector pins before any live work.

**Customer aliases:** “error 1 / freezer sensor”, “code 21 fan”, “code 24 defrost”, “error 41 communications”, “code 85 compressor low voltage”, “temperature alarm 73”. Note exact code+model before describing one column. See original color-coded **Diagnostic mode** tables pp. 4–6 for location photographs.

## Ice-maker and auger assembly access — SR-ICE-REMOVE [DOCUMENTED; p. 9]

**Technician-only disassembly; manufacturer supplies a step-by-step photographed procedure.** The note starts by waiting **5 minutes after manual freezer/fresh-food defrost** (refer to Forced Defrost Method) before removal. Then:

1. Lift and remove ice bucket.
2. Remove screw and lift **wire-housing cover**.
3. Disconnect icemaker-housing connector shown in photo.
4. Remove screw from **Duct Tray-Ice**.
5. Use flat-blade screwdriver to release duct to right from tab as photographed, with care not to damage duct.
6. Push refrigerant pipe down **slightly** as depicted and separate pipe/ice-maker assembly (this involves delicate sealed piping; refer to manufacturer photo and qualified procedure, do not apply force blindly).
7. Depress pictured hook and remove icemaker; press duct tray to withdraw carefully; the red warning says avoid damaging refrigerant-tray grommets on removal.
8. **Auger motor assembly:** disconnect **FAN-AUGER-ASSY connector**, release locking tab by lifting bottom hook, then raise assembly out of compartment, following photographic sequence.

This summary is not a stand-alone authorization to manipulate refrigerant plumbing. Refer to *Removal of Ice Bucket and Ice Maker* and *Removal of the Auger Motor Assy*, **p. 9**, including each numbered photo and red grommet warning. Never present to consumer as a DIY fix for low ice output.

## Refrigerant distribution: TDM 4-way valve — SR-TDM-001 [DOCUMENTED; p. 10]

The diagram explains **TDM valve** refrigerant routing: **#1 input from drier**, **#3 outputs to evaporators**; labelled colors: **FF section yellow tube**, **FRE section no color**, **convertible zone red tube**. A schematic shows staged/parallel-cycle routing and valve actuation. It is an identification aid, not an instruction for customers to cut or open sealed lines. For the exact photograph and tube numbers, cite **p. 10, TDM 4 Way Valve**. Any question about refrigerant recharging amounts, nitrogen pressure or solder points is UNKNOWN here.

## Main PCB, inverter PCB and wiring diagram — SR-BOARD-001 [DOCUMENTED; pp. 11–12]

**p. 11 *Main Board of Fridge Layout*** includes connector labels, circuit board photos, SMPS and inverter board; use it to map the CN30/CN51/CN52/CN70/CN74/CN90 test points recorded in tables. Red warning: **AC input and high voltage at SMPS and inverter power terminal**. The wiring diagram on **p. 12** is titled *Wiring Diagram* and includes dispenser connection. It contains dense schematic conductor lines, connector pin counts and equipment mapping not sufficiently legible as ordinary text extraction. A technician must inspect p. 11 board photo and p. 12 wiring schematic before connecting instruments; don't invent a wire color not printed in a particular connector.

## General symptom support (not a definitive electronic diagnostic) — SR-SYMPTOM-001 [DOCUMENTED; p. 7]

| User symptom | Source-listed first check |
|---|---|
| Front corners or sides hot / condensation | Heat-proof piping can warm front corners; check ambient, door closure, and humid contact with cold exterior. |
| No new ice | If bin emptied, allow **12 hours** to replenish. Check ice-maker OFF status, suitable freezer set point, filled water storage where applicable, ice bucket clumps. |
| Water dispenser not working | Check frozen/missing/incorrectly installed water tank and filter as applicable. This sheet covers models/variants and its general table may not match every reservoir type. |
| Bubbling noise | Refrigerant circulation bubbling is described as normal. |
| Bad odor | Remove spoiled food, clean regularly, seal strong-smelling food. |
| Frost inside | Food blocking vents or door not properly closed. |
| Internal condensation / moist produce | High-water-content uncovered food and prolonged open door; cover food and close door. |

A normal-sound table does not prove every unusual noise is harmless; persistent failure needs qualified assessment.

## Samsung Smart Home app and network (as this sheet states) — SR-APP-001 [DOCUMENTED; p. 8]

The guide is explicitly written for the **historical Samsung Smart Home app** on applicable models; it states Android **4.0 (ICS)+** or iOS **7.0+** for its publication period. It says older **Samsung Smart Refrigerator** app cannot connect with Samsung Smart Home model. Account login is required; verify router and refrigerator Wi-Fi icon, register fridge to home access point, check connection distance/electrical interference and retry, restart app/router; one step says unplug fridge and reconnect after **1 minute** when connected app fails. Do **not** replace this app name with another source's app instructions or guarantee present-day app availability. The sheet makes no claim about today's servers or Android/iOS supported releases.

## UNKNOWN boundaries—searchable abstention for customer and technician

### UNKNOWN-SR-SUFFIX — Exact RF28K9070SG suffix hardware applicability
**Evidence:** [UNKNOWN]. **Aliases:** “does every SG have same main board”, “which production PCB revision?”, “exact RF28K9070SG connector pins”. **Known:** p. 1 names RF28K9070 family, RF22K9381, RF28K9380. **Unknown:** a suffix-level pinout/variant guarantee. **Safe:** match actual board label/photos and qualified service information; do not combine incompatible layouts.

### UNKNOWN-SR-RESISTANCE-CHOICE — 63 vs 230 ohm heater interpretation
**Evidence:** [UNKNOWN] for a specific unit absent its electrical variant. **Aliases:** “heater 63 or 230 ohms?”, “which resistance for 120V?”, “thermistor R/T table value by interpolation”. **Known:** source prints `63(230) Ω ±7%` with variation by input power (pp. 4–5), thermistor temperature chart p. 2. **Unknown:** a safe universal assignment without identifying test conditions. **Safe:** use proper manufacturer diagram, unit label and qualified test procedure; do not silently choose.

### UNKNOWN-SR-COMP-CHARGE — Refrigerant sealed-system service
**Evidence:** [UNKNOWN]; **aliases:** “gas amount”, “recharge grams”, “replace sealed tube”, “valve field calibration”. **Known:** TDM tube identification p. 10, compressor fault codes pp. 6, 11. **Unknown:** refrigerant filling procedure/charge mass, approved soldering method and service tooling. **Safe:** qualified service only; no DIY steps.

### UNKNOWN-SR-DIAG-AFTER-RESET — Definitive component diagnosis from code alone
**Evidence:** [UNKNOWN]. **Aliases:** “code 41 means replace main board immediately”, “error 72 always compressor fault?”, “why code came back”. **Known:** table provides candidate method and component associations. **Unknown:** definitive failed part from number alone; mechanical/electronic confirmation. **Safe:** state table checks and require competent technician; no guaranteed board replacement from code only.

### UNKNOWN-SR-CURRENT-APP — Is Samsung Smart Home app supported now?
**Evidence:** [UNKNOWN]. **Aliases:** “Samsung app disappeared 2026”, “which updated app”, “modern phone setup?” **Known:** original p. 8 historical app and phone OS. **Unknown:** contemporary app changes or regional server availability. **Safe:** report what this document says, request current Samsung assistance outside this self-contained source.

### UNKNOWN-SR-CUSTOMER-DIY — Can a customer perform energized measurement?
**Evidence:** [UNKNOWN] as to customer qualification and safe authorization. **Aliases:** “can I put meter into CN30 myself”, “live inverter testing”, “force defrost at home”. **Known:** explicit p. 1 **For Technicians Only**, p. 11 high-voltage warning. **Safe:** **do not guide unqualified consumers through such measurements or forced modes**. Use general non-invasive symptom advice and refer trained service.

## Coverage and QA boundary

**One permitted source:** 12-page Samsung *Fast Track Troubleshooting* service sheet, visually reviewed including image-only pages 9–12. **Page map:** p. 1 modes/source/safety, p. 2 DC grounding and thermistor / sensor thresholds, p. 3 full Load Mode 26-state table, pp. 4–6 diagnostic code tables, p. 7 general symptoms, p. 8 historical Samsung Smart Home app, p. 9 two photographed ice-maker/auger procedures, p. 10 TDM valve schematic/color tubes, p. 11 main board/SMPS/inverter, p. 12 dispenser wiring diagram. These parts have been translated to text, with original image references only for spatial/probe locations.

**No images or raw PDF pages are embedded.** As a safety limitation, p. 11–12 dense schematics cannot be responsibly reproduced as a hypothetical ASCII pinout; use customer's original PDF for actual spatial verification. Sensor ranges/error rows were transcribed into meaningful tables and checked against source text. This is a human-authored source-specific handover, not an electrical engineering validation or qualified service certificate. Do not assume an error code alone proves failure or that a customer has the skill to operate tools.
