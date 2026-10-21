<h1 id="test-wr-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Test analysis — LLM Wiki vs raw-sources RAG (lanes B, C, D)</h1>

**Type:** benchmark post-mortem (retrieval + Q&A).  
**Wiki run:** `ops/runs/retail-lane-abcd/abcd-full-openai-v2/` · **Raw run:** `ops/runs/retail-lane-abcd-raw/abcd-raw-full-openai-v1/` · **90 questions × 3 lanes** · same answer/judge, top-k=5, 8000-char prefix.  
**Related:** [`ABOUT_FOUR_LANE_TEST_ANALYSIS.md`](./ABOUT_FOUR_LANE_TEST_ANALYSIS.md) · plan [`REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md`](../ref_plan/wip/REFACTOR_RETAIL_RAW_SOURCES_RAG_ABCD_COMPARE.md) · **Last updated:** 2026-10-21.

<h2 id="test-wr-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Headline quadrants](#test-wr-1-quadrants) — pass/fail matrix per lane.
2. [Why methods differ](#test-wr-2-mechanisms) — corpus, retrieval, win/loss patterns.
3. [Retrieval path mix](#test-wr-3-path-mix) — wiki path kinds on raw-win tickets.
4. [Lane B — external Markdown](#test-wr-4-lane-b) — `brain/retail-md` case studies + samples.
5. [Lane C — plain text](#test-wr-5-lane-c) — `brain/retail-txt` case studies + samples.
6. [Lane D — learned digest](#test-wr-6-lane-d) — wiki full-copy vs raw split-less.
7. [Appendix — ticket lists](#test-wr-7-appendix) — full raw-only / wiki-only ids.

---

<h2 id="test-wr-1-quadrants" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Headline quadrants</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Lane</th><th>Both pass</th><th>Wiki only</th><th>Raw only</th><th>Both fail</th><th>Wiki pass rate</th><th>Raw pass rate</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd"><strong>B</strong></td><td>34</td><td>5</td><td style="background:#e8f5e9">24</td><td>27</td><td>43.3%</td><td style="background:#e8f5e9"><strong>64.4%</strong></td></tr>
<tr><td style="background:#e3f2fd"><strong>C</strong></td><td>34</td><td>0</td><td style="background:#e8f5e9">26</td><td>30</td><td>37.8%</td><td style="background:#e8f5e9"><strong>66.7%</strong></td></tr>
<tr><td style="background:#e3f2fd"><strong>D</strong></td><td>50</td><td style="background:#fff3e0">11</td><td>9</td><td>20</td><td style="background:#e8f5e9"><strong>67.8%</strong></td><td>65.6%</td></tr>
</tbody>
</table>


**Raw-only wins (wiki fail → raw pass)** are the main driver of raw beating wiki on **B** and **C**. **Wiki-only** cases on **D** often involve facts present in compiled **`wiki/sources/`** full-copy pages but absent or split differently in **`raw/sources/`** split-less digest.

<h2 id="test-wr-2-mechanisms" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Why methods differ</h2>


<table>
<thead><tr style="background:#1565c0;color:white"><th>Factor</th><th>LLM Wiki arm</th><th>Raw RAG arm</th></tr></thead>
<tbody>
<tr><td style="background:#e3f2fd">Corpus</td><td>Compiled <code>wiki/**</code> (cards, entities, source shards, graph)</td><td>Only <code>raw/sources/**</code> chunks (~2k chars)</td></tr>
<tr><td style="background:#e3f2fd">Retrieval</td><td>Hybrid keyword + vector + graph leg</td><td>Dense vector only</td></tr>
<tr><td style="background:#e3f2fd">Typical win</td><td>Graph/keyword pulls related source shard; D full-copy sources</td><td>Verbatim manual prose in one chunk; no concept dilution</td></tr>
<tr><td style="background:#e3f2fd">Typical loss</td><td>Top-k fills with <code>wiki/concepts/*</code> or wrong SKU source shard</td><td>Wrong SKU file in top-1; chunk boundary cuts gold sentence</td></tr>
</tbody></table>

<h2 id="test-wr-3-path-mix" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Retrieval path mix (raw-only win tickets)</h2>

**Lane B** — wiki top-5 path kinds on **24** raw-win tickets: `{'concept': 31, 'entity': 35, 'wiki_source': 36, 'other': 18}`

**Lane C** — wiki top-5 path kinds on **26** raw-win tickets: `{'wiki_source': 50, 'entity': 53, 'other': 26, 'concept': 1}`

**Lane D** — wiki top-5 path kinds on **9** raw-win tickets: `{'wiki_source': 28, 'concept': 3, 'other': 9, 'entity': 5}`

<h2 id="test-wr-4-lane-b" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. Lane B — external Markdown (`brain/retail-md`)</h2>

<h3 id="test-wr-4-1-e02" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 Case study — `ge_GNE27JYMFS-E02` (door alarm, 2 minutes)</h3>

- **Gold:** alarm if door open **more than 2 minutes**.

- **Wiki:** pass **False** · top paths: `['wiki/concepts/reversing-refrigerator-doors.md', 'wiki/entities/ge-gne27jymfs.md', 'wiki/concepts/adjustable-door-bins.md']`

- **Raw:** pass **True** · top paths: `['raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md']`

**Raw base text (GE user-guide.md):**
```text
frigerator temperature cannot

be changed during TurboCool™. The freezer

temperature is not affected during Turbo Cool.

When opening the refrigerator door during

TurboCool™, the fans will continue to run if they

have cycled on.

Door Alarm

To set the alarm, press the Door Alarm pad. This

alarm will sound if either door is open for more than

2 minutes. The beeping stops when you close the

door.

NOTE: To put the refrigerator control in the OFF position,

simultaneously touch the words Freezer and Fridge

for 3 seconds. Power to the refrigerator cannot be

disconnected by any setting on the control panel.

Changing °F to °C or °C to °F: Press and hold the

"DOOR ALARM" and "FREEZER" bu
```

**Wiki issue:** GE **2 minute** wording is **not** present in `brain/retail-md/wiki/sources/*gegne27*` shards searched; hybrid top-k led with **concept/entity** pages (`reversing-refrigerator-doors`, `ge-gne27jymfs` entity). Rank-5 source shard `page034` is image-caption heavy, not the control-panel alarm paragraph.

**Why raw wins:** full Docling MD retains the **Door Alarm** section verbatim; vector search lands on the same file (despite Kitchenaid rank-1 noise, prefix includes GE in top-k).


<h3 id="test-wr-raw-wins-samples" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Raw wins (wiki failed) — samples</h3>

<h3 id="test-wr-ticket-ge-gne27jymfs-h05-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H05` (hard)</h3>
**Question:** My GNE27J shows “tc,” and some food by the back vent is freezing. What does “tc” mean and what should I do about the food?


**Gold:** “tc” means TurboCool is activated. Move food away from the rear air vent; if cooling is still too strong, adjust the refrigerator to a warmer setting incrementally after TurboCool is no longer preventing a refrigerator temperature adjustment.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md/wiki/entities/ge-gne27jymfs.md` |

| Raw | True | `brain/retail-md/raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md` |


Wiki top-5: `['wiki/entities/ge-gne27jymfs.md', 'wiki/concepts/temperature-settings.md', 'wiki/concepts/control-panel-functions.md', 'wiki/concepts/temperature-controls.md', 'wiki/concepts/turbo-cool-function.md']`


Raw top-5: `['raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/repair-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
ing shelves to accommodate taller items.  
- **Specialized Pans and Dividers**: Enhance food storage efficiency.  

The user guide provides detailed information about the refrigerator's layout, including a diagram that highlights key components such as LED lighting, shelves, door bins, and an icemaker. This appliance is designed to provide optimal cooling performance and user-friendly operation, as detailed in its user guide.  

Additionally, the GE GNE27JYMFS features advanced control panel functionalities, which are central to the user guide. This includes detailed instructions on its operation, including temperature settings and special features like Turbo Cool. Regular maintenance is req
```

**Raw rank-1 excerpt (search evidence):**
```text
nded setting.

Refrigerator Compartment Temperature Control

Adjust refrigerator compartment temperature. The

refrigerator temperature is preset in the factory

at 37°F (2.8°C). Allow 24 hours for temperature to

stabilize to the preset recommended setting.

Water Filter

Press and hold 3 seconds to reset the Water Filter.

Turbo Cool

To set the TurboCool™, press the Turbo Cool pad

for 3 seconds. The display will show tc.

TurboCool™ rapidly cools the refrigerator

compartment in order to more quickly cool foods.

8VH TurboCool™ when adding a large amount of

the food to the refrigerator compartment, putting

away foods after they have been sitting out at room

temperature, or when puttin
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-ge-gne27jymfs-h06-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H06` (hard)</h3>
**Question:** I want to clean the fridge exterior and then pull the appliance out to clean behind it. What cleaning products and moving method should I use?


**Gold:** For fingerprint-resistant or painted finishes, use mild detergent in warm water with a soft or microfiber cloth and wipe dry; avoid abrasive and stainless-steel cleaners on those surfaces. Raise the front leveling legs and pull the refrigerator straight out, then push it straight back rather than si…


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md/wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page023--169h3pu.md` |

| Raw | True | `brain/retail-md/raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md` |


Wiki top-5: `['wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page023--169h3pu.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page022--1638wn9.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--10-user-guide--1xp31fe.md', 'wiki/concepts/care-and-cleaning-instructions.md', 'wiki/concepts/refrigerator-internal-components.md']`


Raw top-5: `['raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: source
title: GE GNE27JYMFS User Guide - Page 023
created: 2026-10-19
updated: 2026-10-19
tags: [user guide, refrigerator, GE GNE27JYMFS]
related: [ge-gne27jymfs, refrigerator-internal-components, care-and-cleaning-instructions]
sources: ["fridge-docs_md/ge_GNE27JYMFS/assets/user-guide/page_023.png"]
---
# GE GNE27JYMFS User Guide - Page 023
This page includes a cutaway diagram of the GE GNE27JYMFS refrigerator, illustrating its internal components and layout. The accompanying text provides care and cleaning instructions, specifically detailing how to move the refrigerator and replace lights. Understanding these components and maintenance procedures is crucial for proper care and longevity of the appliance.

![The image depicts a cutaway diagram of a refrigerator, showing its internal components and layout. Visible text includes "LEDs (locations may vary by model)" and various…
```

**Raw rank-1 excerpt (search evidence):**
```text
erator is plugged in.

Ice Maker Frame

ON/OFF Switch

ON/OFF Switch

Ice Maker

(On some models)

Figure E

21

49-1000472 Rev. 9

### Original figure / page illustration (PDF page 21)

![Original PDF page 21 (illustrations and visual labels)](assets/user-guide/page_021.png)


## PDF page 22

### Care and Cleaning

#### Cleaning the Outside

#### FINGERPRINT RESISTANT STAINLESS STEEL*, BLACK STAINLESS, SLATE, DARK

#### SLATE, PAINTED - Outside surfaces, door handles, and trim

DO NOT use Stainless Steel cleaners on the door surfaces.

IMPORTANT: The use of incorrect products may damage the outer finish of Fingerprint Resistant Stainless and

Black Stainless models. Please follow these inst
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-kitchenaid-krff507hps-h06-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`kitchenaid_KRFF507HPS-H06` (hard)</h3>
**Question:** The water from my dispenser is warm after I have filled several large jugs. How long should I wait for it to cool again, and what button sequence starts Measured Fill calibration?


**Gold:** After a large draw of water, allow about 3 hours for the supply to cool completely. To initiate Measured Fill calibration, press and hold OPTIONS and LOCK simultaneously for 3 seconds (after flushing the dispenser system).


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md/wiki/sources/13-fridge-docsmd--20-kitchenaidkrff507hps--10-user-guide--1bdnof4.md` |

| Raw | True | `brain/retail-md/raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md` |


Wiki top-5: `['wiki/sources/13-fridge-docsmd--20-kitchenaidkrff507hps--10-user-guide--1bdnof4.md', 'wiki/entities/kitchenaid-krff507hps.md', 'wiki/concepts/measured-fill-feature.md', 'wiki/sources/13-fridge-docsmd--20-kitchenaidkrff507hps--6-assets--10-user-guide--7-page024--suqbr9.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
lui
- Instrucțiuni de instalare
- Cerințe electrice
- Cerințe pentru alimentarea cu apă
- Ajustarea înclinării cabinetului
- Alinierea ușilor
- Stabilizarea frigiderului
- Curățarea frigiderului
- Întreținerea sistemului de filtrare a apei
- Avertismente de siguranță privind curățarea
- Sistem de filtrare a apei
- Funcții de frigider (ex. Max Ice, Water Filter Status)
- Instrucțiuni de instalare pentru uși și compartimente

<!-- llm-wiki:embedded-images -->
## Embedded Images

### Document

![L'image montre un réfrigérateur à portes françaises avec plusieurs éléments étiquetés. Les étiquettes incluent : A. Ice maker, B. Air filter, C. Water filter, D. Door bins, E. Crispers, F. Pantry drawer
```

**Raw rank-1 excerpt (search evidence):**
```text
Refrigerator:

Your refrigerator is heavy. When moving the refrigerator for

cleaning or service, be sure to cover the ﬂoor with

cardboard or hardboard to avoid ﬂoor damage. Always pull

the refrigerator straight out when moving it. Do not wiggle or

“walk” the refrigerator when trying to move it, as ﬂoor

damage could occur.

Clean Before Using

After you remove all of the packaging materials, clean the inside

of your refrigerator before using it. See the cleaning instructions in

“Refrigerator Care.”

Important information to know about glass shelves

and covers:

Do not clean glass shelves or covers with warm water when

they are cold. Shelves and covers may break if exposed to

sudden
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-kitchenaid-krff507hps-h09-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`kitchenaid_KRFF507HPS-H09` (hard)</h3>
**Question:** I replaced the water filter and still get weak dispenser flow. What must be true about the filter’s installed position, and which test distinguishes a clog from another water-supply problem?


**Gold:** Make sure the water filter is turned clockwise 90° and locked into the housing; without correct locking, water will not flow. If flow is merely weak, remove the filter and test the dispenser: improved flow indicates the filter may be clogged and needs replacement.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md/wiki/entities/kitchenaid-french-door-refrigerator-krff507hps.md` |

| Raw | True | `brain/retail-md/raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md` |


Wiki top-5: `['wiki/entities/kitchenaid-french-door-refrigerator-krff507hps.md', 'wiki/entities/kitchenaid-krff507hps.md', 'wiki/concepts/water-filter.md', 'wiki/sources/13-fridge-docsmd--20-kitchenaidkrff507hps--6-assets--10-user-guide--7-page017--1b62ko7.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---  
type: entity  
title: KitchenAid® French Door Refrigerator (Model KRFF507HPS)  
created: 2026-10-19  
updated: 2026-10-19  
tags: [refrigerator, KitchenAid, KRFF507HPS]  
related: [ice-maker, air-filter, water-filter, door-bins, crispers, pantry-drawer, freezer-drawer, led-ramp-on-lighting, in-door-ice-dispensing-system, pull-out-tray, refrigerator-door-removal-and-replacement]  
sources: ["fridge-docs_md/kitchenaid_KRFF507HPS/assets/user-guide/page_005.png", "fridge-docs_md/kitchenaid_KRFF507HPS/assets/user-guide/page_008.png"]  
---  
The Kitchen
```

**Raw rank-1 excerpt (search evidence):**
```text
er Front..............................................................11

-- Replace Drawer Front..............................................................11

-- Final Steps................................................................................11

Electrical Requirements..............................................................12

Water Supply Requirements.......................................................12

Connect the Water Supply.........................................................12

-- Connect to Water Line.............................................................13

-- Connect to Refrigerator............................................................13

--
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-kitchenaid-krff507hps-h10-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`kitchenaid_KRFF507HPS-H10` (hard)</h3>
**Question:** My newly installed refrigerator has not cooled fully. How long should the first cool-down take, and after changing a temperature set point how long should I wait before changing it again?


**Gold:** Allow about 24 hours following installation for complete cooling. After changing a set point, wait at least 24 hours before making another temperature adjustment, then recheck temperatures.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md/wiki/sources/13-fridge-docsmd--20-kitchenaidkrff507hps--6-assets--10-user-guide--7-page021--1hz5a92.md` |

| Raw | True | `brain/retail-md/raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md` |


Wiki top-5: `['wiki/sources/13-fridge-docsmd--20-kitchenaidkrff507hps--6-assets--10-user-guide--7-page021--1hz5a92.md', 'wiki/sources/13-fridge-docsmd--20-kitchenaidkrff507hps--6-assets--10-user-guide--7-page022--10qhhbn.md', 'wiki/entities/kitchenaid-french-door-refrigerator-krff507hps.md', 'wiki/concepts/temperature-settings.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
This page from the KitchenAid® KRFF507HPS user guide focuses on the hinged seal mechanism of the refrigerator doors and the temperature settings. It includes a labeled diagram illustrating the hinged seal, which enhances cooling efficiency by ensuring a tight seal when the door is closed. The guide also emphasizes the importance of waiting 24 hours before placing food in the refrigerator to ensure proper cooling.

![The image depicts a section of a refrigerator with a focus on the hinged seal mechanism. It includes a labeled diagram showing the "A. Hinged seal" that automatically folds inward when the left door is opened. The surrounding text discusses the operation of the refrigerator
```

**Raw rank-1 excerpt (search evidence):**
```text
mental

capabilities, or lack of experience and knowledge, unless

they have been given supervision or instruction concerning

use of the appliance by a person responsible for their safety.

IChildren should be supervised to ensure that they do not

play with the appliance.

ITo avoid the risk of children becoming trapped and

suffocating, do not allow them to play or hide inside the

refrigerator.

IIf the power supply cord is damaged, it must be replaced by

the manufacturer or its service agent or a similarly qualified

person.

3


## PDF page 4

### REFRIGERATOR SAFETY

Proper Disposal of Your Old Refrigerator

Before You Throw Away Your Old

Refrigerator or Freezer:

Take off the door
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-wiki-wins-samples" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Wiki wins (raw failed) — samples</h3>

<h3 id="test-wr-ticket-ge-gne27jymfs-h04-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H04` (hard)</h3>
**Question:** My water filter is unavailable, but I still want water and ice. What must be installed instead of the filter, and what water-pressure range does the guide require?


**Gold:** Install the designated filter bypass plug; neither the dispenser nor the ice maker will operate without a filter or bypass plug. The required cold-water pressure for the ice maker is 25–120 psi (172–827 kPa).


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md/wiki/entities/water-filter-cartridge-xwfe.md` |

| Raw | False | `brain/retail-md/raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md` |


Wiki top-5: `['wiki/entities/water-filter-cartridge-xwfe.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--10-user-guide--1xp31fe.md', 'wiki/concepts/water-filter-cartridge.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page014--1789a3o.md', 'wiki/concepts/filter-replacement-instructions.md']`


Raw top-5: `['raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---  
type: entity  
title: Water Filter Cartridge - XWFE  
created: 2026-10-19  
updated: 2026-10-19  
tags: [water filter, XWFE, specifications, product, filtrare, apă]  
related: [ge-gne27jymfs, ge-appliances, limited-warranty]  
sources: ["fridge-docs_md/ge_GNE27JYMFS/assets/user-guide/page_015.png", "fridge-docs_md/ge_GNE27JYMFS/assets/user-guide/page_049.png", "fridge-docs_md/ge_GNE27JYMFS/user-guide.md"]  
---  
# Water Filter Cartridge - XWFE  
The Water Filter Cartridge - XWFE is a specific model designed for use in certain GE refrigerators, including the GE GNE27JYMFS. It provides essential filtration for drinking water and ice, ensuring safety and quality. This cartridge is crucial for maintaining the quality of water dispensed from the refrigerator, adhering to specified water supply conditions for optimal performance.

## Specifications  
- **Service Flow:** 0.5 gpm (1.89 lp…
```

**Raw rank-1 excerpt (search evidence):**
```text
pliance that leave s our factory is inspected

thoroughly to ensure that it is working properly.

REFRIGERATOR SAFETY..............................................................3

What’s New Behind the Doors?...................................................5

PARTS AND FEATURES.................................................................5

INSTALLATION INSTRUCTIONS...................................................6

Unpack the Refrigerator...............................................................7

-- Remove the Packaging..............................................................7

-- Clean Before Using....................................................................7

Lo
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-ge-gne27jymfs-e04-easy" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-E04` (easy)</h3>
**Question:** What is the rated water-filter capacity of the XWFE cartridge?


**Gold:** 170 gallons (643.5 litres).


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md/wiki/entities/water-filter-cartridge-xwfe.md` |

| Raw | False | `brain/retail-md/raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md` |


Wiki top-5: `['wiki/entities/water-filter-cartridge-xwfe.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page049--mkh61m.md', 'wiki/entities/ge-gne27jymfs.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page050--xqzm30.md', 'wiki/concepts/filter-replacement-instructions.md']`


Raw top-5: `['raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
rtridge is crucial for maintaining the quality of water dispensed from the refrigerator, adhering to specified water supply conditions for optimal performance.

## Specifications  
- **Service Flow:** 0.5 gpm (1.89 lpm)  
- **Water Pressure Range:** 25-120 psi (172-827 kPa)  
- **Water Temperature Range:** 33°F-100°F (0.6°C-38°C)  
- **Capacity:** 170 gallons (643.5 liters)  

## Importance  
The Water Filter Cartridge - XWFE is an essential component used in the GE GNE27JYMFS refrigerator, ensuring the purity of the water and ice produced by the appliance. It is mentioned in the context of maintaining and operating the water dispenser.

## Warranty  
The Water Filter Cartridge XWFE is cover
```

**Raw rank-1 excerpt (search evidence):**
```text
gewaterfilters.com

or call GE Appliances Parts and Accessories, 877.959.8688. In Canada, call 800.661.1616.

15

49-1000472 Rev. 9

### Table (PDF page 15)

| Service Flow | 0.5 gpm (1.89 lpm) |
| --- | --- |
| Water Supply | Potable Water |
| Water Pressure | 25-120 psi (172-827 kPa) |
| Water Temperature | 33F-100F  0.6C-38C |
| Capacity | 170 gallons (643.5 liters) |

### Original figure / page illustration (PDF page 15)

![Original PDF page 15 (illustrations and visual labels)](assets/user-guide/page_015.png)


## PDF page 16

### Shelves and Bins

Not all features are on all models.

#### Rearranging the Refrigerator Shelves

Shelves in the refrigerator compartment are adjustable.
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-ge-gne27jymfs-e05-easy" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-E05` (easy)</h3>
**Question:** What cold-water pressure is required for the automatic ice maker?


**Gold:** 25–120 psi (172–827 kPa).


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md/wiki/concepts/automatic-icemaker.md` |

| Raw | False | `brain/retail-md/raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md` |


Wiki top-5: `['wiki/concepts/automatic-icemaker.md', 'wiki/entities/ge-gne27jymfs.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page041--pbfx1e.md', 'wiki/entities/water-filter-cartridge-xwfe.md', 'wiki/sources/13-fridge-docsmd--12-gegne27jymfs--6-assets--10-user-guide--7-page020--1ol3jsv.md']`


Raw top-5: `['raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---  
type: concept  
title: Automatic Icemaker  
created: 2026-10-19  
updated: 2026-10-19  
tags: [icemaker, refrigerator feature, refrigerator, appliance]  
related: [ge-gne27jymfs]  
sources: ["fridge-docs_md/ge_GNE27JYMFS/assets/user-guide/page_020.png", "fridge-docs_md/ge_GNE27JYMFS/assets/user-guide/page_021.png"]  
---  
# Automatic Icemaker  
The automatic icemaker is a device within the GE GNE27JYMFS refrigerator that automatically produces ice. This feature is significant for users who require a steady supply of ice for beverages and food preservation and is essential for modern refrigerators, providing convenience for users.

## Operational Details  
- The icemaker may take 12 to 24 hours to begin producing ice.  
- It can generate approximately 100-130 cubes in a 24-hour period.  
- The icemaker requires a potable water supply and follows an ice production cycle.

## Safety…
```

**Raw rank-1 excerpt (search evidence):**
```text
# user-guide.pdf — extracted Markdown



> Original PDF: `user-guide.pdf`; PDF page references below are 1-based.



> Source fidelity: Text and diagrams are extracted from this PDF only; image links are rasterized views of their original PDF pages.



## PDF page 1

#### FRENCHDOOR BOTTOM MOUNT

#### REFRIGERATOR

#### USE & CARE GUIDE

W W W.KI T C HE N A I D .C OM

WWW. K IT C HENAID. C A

C A N A D A : 1 - 8 0 0 - 8 0 7 - 6 7 7 7

U . S . : 1 - 8 0 0 - 4 2 2 - 1 2 3 0

W11218735B


## PDF page 2

### TABLE OF CONTENTS

Congratulations on your purchase and welcome to the

KitchenAid Brand family o f high-quality appliances. Your new

KitchenAid® French Door Refrigerator combines advanced

cooling technology with simple operation and high efficiency.

Each appliance that leave s our factory is inspected

thoroughly to ensure that it is working properly.

REFRIGERATOR SAFETY............…
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-samsung-rf28k9070sg-e02-easy" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`samsung_RF28K9070SG-E02` (easy)</h3>
**Question:** What freezer temperature settings can I select with the Freezer button?


**Gold:** From 5°F (−15°C) down to −8°F (−23°C).


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md/wiki/concepts/temperature-settings.md` |

| Raw | False | `brain/retail-md/raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md` |


Wiki top-5: `['wiki/concepts/temperature-settings.md', 'wiki/entities/samsung-rf28k9070sg.md', 'wiki/sources/13-fridge-docsmd--18-samsungrf28k9070sg--12-repair-guide--xkh07f.md', 'wiki/sources/13-fridge-docsmd--18-samsungrf28k9070sg--6-assets--10-user-guide--7-page036--1riywkl.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/ge_GNE27JYMFS/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
emphasizes the significance of setting the correct temperature. Users are advised to wait 24 hours before placing food in the refrigerator to ensure that it reaches the desired cooling level. Additionally, it provides specific instructions on how to adjust these settings, including a recommended freezer temperature range of -5°F to 5°F (-21°C to -15°C).

## Samsung RF28K9070SG  
Temperature settings on the Samsung RF28K9070SG refrigerator allow users to set and monitor the temperature for both the freezer and fridge compartments. The recommended settings are -8°F for the freezer and 89°F for the fridge, which are crucial for optimal food preservation. These settings can be managed through t
```

**Raw rank-1 excerpt (search evidence):**
```text
. Use both hands when removing them to avoid

dropping.

NOTE: This refrigerator is intended for use in a location where the

temperature ranges from a minimum of 55°F (13°C) to a maximum

of 110°F (43°C). The preferred room temperature range for

optimum performance, which reduces electricity usage and

provides superior cooling, is between 60°F (15°C) and 90°F

(32°C). It is recommended that you do not install the refrigerator

near a heat source, such as an oven or radiator.

1/2" (1.25 cm)

3¾ " (9.5 cm)

7


## PDF page 8

### INSTALLATION INSTRUCTIONS

#### Remove and Replace Refrigerator Doors

NOTE: Measure the width of your door opening, to see whether or not you need to remove the
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-samsung-rf28k9070sg-e08-easy" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`samsung_RF28K9070SG-E08` (easy)</h3>
**Question:** What water pressure does the ice maker require?


**Gold:** 20–125 psi.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md/wiki/entities/samsung-rf28k9070sg.md` |

| Raw | False | `brain/retail-md/raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md` |


Wiki top-5: `['wiki/entities/samsung-rf28k9070sg.md', 'wiki/entities/ice-maker.md', 'wiki/sources/13-fridge-docsmd--18-samsungrf28k9070sg--10-user-guide--1a8ymzx.md', 'wiki/concepts/installation-instructions-for-samsung-rf28k9070sg.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/samsung_RF28K9070SG/user-guide.md', 'raw/sources/fridge-docs_md/kitchenaid_KRFF507HPS/user-guide.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---  
type: entity  
title: Samsung RF28K9070SG  
created: 2026-10-19  
updated: 2026-10-19  
tags: [samsung, refrigerator, rf28k9070sg, model, appliance, smart home]  
related: [samsung-rf28k9381, samsung-rf28k9380, load-mode, diagnostic-mode, error-codes, diagnostic-methods, refrigerator-troubleshooting, samsung-smart-home, troubleshooting, ice-maker, auger-motor-assembly, ice-bucket-removal, auger-motor-assembly-removal, tdm-4-way-valve, 4-way-valve-operation, main-circuit-board, switch-mode-power-supply, inverter-board, wiring-diagram, electrical-components, refrigerator-components-diagram, user-manual, installation-instructions, freezer-door-detachment, freezer-door-reattachment-instructions, door-height-adjustment, snap-rings, refrigerator-operations-panel, override-mode, smartthings, temperature-settings, installation-instructions-for-wine-rack, flexzone, handling-tempered-glass-s…
```

**Raw rank-1 excerpt (search evidence):**
```text
# user-guide.pdf — extracted Markdown



> Original PDF: `user-guide.pdf`; PDF page references below are 1-based.



> Source fidelity: Text and diagrams are extracted from this PDF only; image links are rasterized views of their original PDF pages.



## PDF page 1

### Refrigerator

### User manual

Free Standing Appliance

2018-07-05 5:53:09

### Original figure / page illustration (PDF page 1)

![Original PDF page 1 (illustrations and visual labels)](assets/user-guide/page_001.png)


## PDF page 2

### Contents

Safety information

4

Important safety symbols and precautions:

4

State of California Proposition 65 Warning (US only)

5

Critical installation warnings

5

Installation cautions

7

Critical usage warnings

8

Usage cautions

11

Cleaning cautions

12

Critical disposal warnings

13

This appliance is intended to be used in household and similar applications such as

13…
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h2 id="test-wr-5-lane-c" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Lane C — plain text (`brain/retail-txt`)</h2>

<h3 id="test-wr-raw-wins-samples" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Raw wins (wiki failed) — samples</h3>

<h3 id="test-wr-ticket-ge-gne27jymfs-h05-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H05` (hard)</h3>
**Question:** My GNE27J shows “tc,” and some food by the back vent is freezing. What does “tc” mean and what should I do about the food?


**Gold:** “tc” means TurboCool is activated. Move food away from the rear air vent; if cooling is still too strong, adjust the refrigerator to a warmer setting incrementally after TurboCool is no longer preventing a refrigerator temperature adjustment.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-txt/wiki/entities/ge-gne27jymfs.md` |

| Raw | True | `brain/retail-txt/raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.txt` |


Wiki top-5: `['wiki/entities/ge-gne27jymfs.md', 'wiki/sources/11-fridge-docs--12-gegne27jymfs--10-user-guide--anda5p.md', 'wiki/sources/11-fridge-docs--20-kitchenaidkrff507hps--10-user-guide--agi3vb.md', 'wiki/entities/samsung-rf28k9070sg.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt', 'raw/sources/fridge-docs/samsung_RF28K9070SG/repair-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: entity
title: GE GNE27JYMFS
created: 2026-10-18
updated: 2026-10-18
tags: [refrigerator, GE]
related: []
sources: ["fridge-docs/ge_GNE27JYMFS/user-guide.txt"]
---

# GE GNE27JYMFS

The GE GNE27JYMFS is a refrigerator model manufactured by General Electric. It is designed to provide efficient cooling and storage solutions for household needs. This model features adjustable shelves, an icemaker, and a water filtration system, making it a versatile choice for modern kitchens.

## Key Features
- Adjustable shelves for customizable storage.
- Icemaker functionality for convenient ice production.
- Water filtration system to ensure clean dri
```

**Raw rank-1 excerpt (search evidence):**
```text
as laundry, lighted candles, lighted cigarettes, dishes, chemicals, metal objects, etc.) on the appliance. This may result in an electric shock, fire, problems with the product, or injury. Do not put a container filled with water on the appliance. - If spilled, there is a risk of fire or electric shock. • Do not use mechanical devices or any other means to accelerate the defrosting process, other than those recommended by the manufacturer. • Do not damage the refrigerant circuit. • Never stare directly at the UV LED lamp for long periods of time. - This may result in eye strain due to the ultraviolet rays. • Do not put a fridge shelf into the refrigerator upside down. The shelf stopper will
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-ge-gne27jymfs-h06-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H06` (hard)</h3>
**Question:** I want to clean the fridge exterior and then pull the appliance out to clean behind it. What cleaning products and moving method should I use?


**Gold:** For fingerprint-resistant or painted finishes, use mild detergent in warm water with a soft or microfiber cloth and wipe dry; avoid abrasive and stainless-steel cleaners on those surfaces. Raise the front leveling legs and pull the refrigerator straight out, then push it straight back rather than si…


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-txt/wiki/sources/11-fridge-docs--12-gegne27jymfs--10-user-guide--anda5p.md` |

| Raw | True | `brain/retail-txt/raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt` |


Wiki top-5: `['wiki/sources/11-fridge-docs--12-gegne27jymfs--10-user-guide--anda5p.md', 'wiki/entities/ge-gne27jymfs.md', 'wiki/sources/11-fridge-docs--20-kitchenaidkrff507hps--10-user-guide--agi3vb.md', 'wiki/entities/kitchenaid-french-door-bottom-mount-refrigerator.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt', 'raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.txt']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: source
title: User Guide for GE GNE27JYMFS Refrigerator
tags: [refrigerator, user guide]
related: []
created: 2026-10-18
updated: 2026-10-18
authors: []
year: 2026
url: ""
venue: ""
sources: ["fridge-docs/ge_GNE27JYMFS/user-guide.txt"]
---

# User Guide for GE GNE27JYMFS Refrigerator

This document serves as the user guide for the GE GNE27JYMFS refrigerator, providing essential information on safety, operation, features, maintenance, care and cleaning, installation instructions, and troubleshooting tips.

## Safety Precautions
- Emphasizes the importance of safety precautions and proper installation to prevent injury and property damage.

## Features and Controls
- Details the features of the GE GNE27JYMFS refrigerator, including adjustable shelves, icemaker functionality, and water filtration system.

## Water Filter Cartridge
- Specifications and maintenance instructions for…
```

**Raw rank-1 excerpt (search evidence):**
```text
mar the finish. DO USE DO NOT USE ✔ Soft, clean cloth ✘ Abrasive cloths ✘ Paper towels or newsprint ✘ Steel-wool pads ✔ Warm, soapy water - use a mild detergent ✘ Abrasive powders or liquids ✘ Window sprays ✘ Ammonia ✘ Acidic or vinegar based cleaners ✘ Oven cleaners ✘ Flammable fluids NOTE: Paper towels scratch and may dull the clear coat of the painted door. To avoid possible damage, use only soft clean cloths to polish and wipe the door. Style 2 - Stainless Steel IMPORTANT: ■ Damage to stainless steel finish due to improper use of cleaning products, or using non-recommended cleaning products, is not covered under the warranty. DO USE DO NOT USE ✔ Soft, clean cloth ✘ Abrasive cloths ✘ Pap
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-kitchenaid-krff507hps-h01-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`kitchenaid_KRFF507HPS-H01` (hard)</h3>
**Question:** My ice cubes are hollow. What inlet water-pressure range is required, and what two water-supply checks does the troubleshooting section recommend?


**Gold:** The supply pressure should be 35–120 psi (241–827 kPa). Check that the shutoff valve is fully open and that the water-source line is not kinked; the guide also advises checking the filter if the problem persists.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-txt/wiki/entities/kitchenaid-french-door-bottom-mount-refrigerator.md` |

| Raw | True | `brain/retail-txt/raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt` |


Wiki top-5: `['wiki/entities/kitchenaid-french-door-bottom-mount-refrigerator.md', 'wiki/sources/11-fridge-docs--20-kitchenaidkrff507hps--10-user-guide--agi3vb.md', 'wiki/sources/11-fridge-docs--12-gegne27jymfs--10-user-guide--anda5p.md', 'wiki/entities/water-filter.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: entity
title: KitchenAid® French Door Bottom Mount Refrigerator
created: 2026-10-18
updated: 2026-10-18
tags: [refrigerator, KitchenAid, appliance]
related: [water-filter, air-filter, produce-preserver, kitchenaid-refrigeration-limited-warranty]
sources: ["fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt"]
---

# KitchenAid® French Door Bottom Mount Refrigerator

The KitchenAid® French Door Bottom Mount Refrigerator (model W11218735B) is a high-efficiency appliance designed to provide advanced cooling technology and energy efficiency. It features a water filtration system, air filtration system, and produce preserver to enhance food preservation.

## Key Features
- Advanced cooling technology
- Energy efficiency
- Water filtration system
- Air filtration system
- Produce preserver

## Maintenance
Regular maintenance is essential for optimal performance, including cleaning the c…
```

**Raw rank-1 excerpt (search evidence):**
```text
Front ..............................................................11 - Replace Drawer Front ..............................................................11 - Final Steps ...............................................................................11 Electrical Requirements .............................................................12 Water Supply Requirements ......................................................12 Connect the Water Supply .........................................................12 - Connect to Water Line .............................................................13 - Connect to Refrigerator ...........................................................13 - Complete t
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-kitchenaid-krff507hps-h04-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`kitchenaid_KRFF507HPS-H04` (hard)</h3>
**Question:** If I keep getting food smells, what kind of filter is described for controlling odors, and what is the replacement interval and indicator colour?


**Gold:** The refrigerator has an air filter intended to reduce common food odours; on models with that filter, replace it every 6 months when its status indicator changes completely from white to red.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-txt/wiki/entities/kitchenaid-french-door-bottom-mount-refrigerator.md` |

| Raw | True | `brain/retail-txt/raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt` |


Wiki top-5: `['wiki/entities/kitchenaid-french-door-bottom-mount-refrigerator.md', 'wiki/sources/11-fridge-docs--20-kitchenaidkrff507hps--10-user-guide--agi3vb.md', 'wiki/entities/air-filter.md', 'wiki/entities/water-filter.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt', 'raw/sources/fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt', 'raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.txt']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: entity
title: KitchenAid® French Door Bottom Mount Refrigerator
created: 2026-10-18
updated: 2026-10-18
tags: [refrigerator, KitchenAid, appliance]
related: [water-filter, air-filter, produce-preserver, kitchenaid-refrigeration-limited-warranty]
sources: ["fridge-docs/kitchenaid_KRFF507HPS/user-guide.txt"]
---

# KitchenAid® French Door Bottom Mount Refrigerator

The KitchenAid® French Door Bottom
```

**Raw rank-1 excerpt (search evidence):**
```text
W11218735B FRENCH DOOR BOTTOM MOUNT REFRIGERATOR USE & CARE GUIDE WWW.KITCHENAID.COM U.S.: 1-800-422-1230 WWW.KITCHENAID.CA CANADA: 1-800-807-6777

2 Congratulations on your purchase and welcome to the KitchenAid Brand family o f high-quality appliances. Your new KitchenAid® French Door Refrigerator combines advanced cooling technology with simple operation and high efficiency. Each
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-samsung-rf28k9070sg-h03-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`samsung_RF28K9070SG-H03` (hard)</h3>
**Question:** I want to use the bottom-right FlexZone for deli meat, but the controls are locked. What mode and temperature do I need, how do I unlock it, and does Control Lock also prevent water or ice dispensing?


**Gold:** Use FlexZone “Chill / Meat,” set to 30°F (−1°C), selected by holding FlexZone for 3 seconds and cycling through its modes. Hold Lighting/Control Lock for 3 seconds to unlock the controls. While Control Lock is enabled, the dispenser also will not deliver water or ice.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-txt/wiki/sources/11-fridge-docs--18-samsungrf28k9070sg--10-user-guide--1c3bihc.md` |

| Raw | True | `brain/retail-txt/raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.txt` |


Wiki top-5: `['wiki/sources/11-fridge-docs--18-samsungrf28k9070sg--10-user-guide--1c3bihc.md', 'wiki/entities/samsung-rf28k9070sg.md', 'wiki/sources/11-fridge-docs--18-samsungrf28k9070sg--12-repair-guide--16k4klu.md', 'wiki/entities/samsung-smart-home.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.txt', 'raw/sources/fridge-docs/samsung_RF28K9070SG/repair-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt', 'raw/sources/fridge-docs/samsung_RF28K9070SG/user-guide.txt', 'raw/sources/fridge-docs/ge_GNE27JYMFS/user-guide.txt']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: source
title: User Manual for Samsung RF28K9070SG Refrigerator
authors: []
year: 2026
url: ""
venue: ""
created: 2026-10-18
updated: 2026-10-18
tags: []
related: []
sources: ["fridge-docs/samsung_RF28K9070SG/user-guide.txt"]
---

# User Manual for Samsung RF28K9070SG Refrigerator

This document serves as the user manual for the Samsung RF28K9070SG refrigerator, outlining safety information, installation instructions, operational guidelines, and warranty details.

## Safety Information
- Emphasizes the importance of following safety precautions to prevent accidents.
- Provides extensive safety warnings and installation cautions.

## Installation Procedures
- Detailed instructions for connecting the water supply line.
- Steps to ensure proper setup and operation.

### Installation Steps
1. Connect the water supply line to the refrigerator.
2. Plug the power cord into the wall soc…
```

**Raw rank-1 excerpt (search evidence):**
```text
s or cabinets. • The refrigerator is level and is sitting firmly on the floor. • The door opens and closes freely, and the interior light turns on automatically when you open the door. Untitled-2 35 2018-07-05 □□ 5:53:16

English36 Operations Feature panel 01 02 03 04 05 07 08 06 09 01 Freezer / Power Freeze 02 Fridge / Power Cool 03 Door Alarm 04 FlexZone 05 Lighting / Control Lock 06 Ice Maker Off 07 Cubed Ice / Override 08 Crushed Ice / Filter Reset 09 Network connection NOTE When you change the temperature on the panel, the panel displays the actual temperature inside the refrigerator until the temperature matches the temperature you set. Then, the panel displays the new set temperature.
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-wiki-wins-samples" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Wiki wins (raw failed) — samples</h3>

<h2 id="test-wr-6-lane-d" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">6. Lane D — learned (`brain/retail-md-learned`)</h2>

<h3 id="test-wr-raw-wins-samples" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Raw wins (wiki failed) — samples</h3>

<h3 id="test-wr-ticket-ge-gne27jymfs-h04-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H04` (hard)</h3>
**Question:** My water filter is unavailable, but I still want water and ice. What must be installed instead of the filter, and what water-pressure range does the guide require?


**Gold:** Install the designated filter bypass plug; neither the dispenser nor the ice maker will operate without a filter or bypass plug. The required cold-water pressure for the ice maker is 25–120 psi (172–827 kPa).


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--36-user-guide-part-04-water-ice-filter--612x3m.md` |

| Raw | True | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--36-user-guide-part-04-water-ice-filter--612x3m.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--36-user-guide-part-04-water-ice-filter--1gfp1gh.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--32-user-guide-part-02-installation--jcvco2.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--32-user-guide-part-02-installation--xofqwp.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-02-installation.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-02-installation.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
urge air and impurities.

**Note:** Use only Samsung-provided or approved replacement filters.

## Ice Bucket Management

To prevent clumping and ensure proper ice production, follow these instructions for removing and reseating the ice bucket:

1. Hold the bottom and side of the bucket; gently lift and pull it out.
2. Remove remaining cubes and reinstall.
3. If the bucket cannot seat firmly, turn the **ice screw 90 degrees** and try again.

## Reverse Osmosis Water Pressure Requirements

When using a reverse osmosis system with the refrigerator, ensure the following water pressure conditions:

- The supply to the reverse-osmosis system must be **35–120 psi (241–827 kPa)**.
- The filtered li
```

**Raw rank-1 excerpt (search evidence):**
```text
## Dispenser, ice maker, water filters and performance

**Original manual:** *Refrigerators — Bottom Freezer: Owner’s Manual & Installation Instructions*. **Source file:** `user-guide.pdf`.

### GE-DISPENSER-001 — External and internal dispenser operation, initial purge

**Knowledge ID:** `GE-DISPENSER-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** GE / GE Profile bottom-freezer refrigerators of 18, 19, 21, 22, 24, 25, 26 and 27 cu ft in publication 49-1000472 Rev. 9;
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-ge-gne27jymfs-h08-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H08` (hard)</h3>
**Question:** After replacing my XWFE filter, I see water spurting at the dispenser. How much water should I run, and when does the manual say to replace the filter again?


**Gold:** Run the dispenser for about 3 minutes (approximately 1½ gallons) after installing a new cartridge. Replace an XWFE cartridge about every 6 months or at its 170-gallon rated capacity, and sooner if flow noticeably decreases.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--36-user-guide-part-04-water-ice-filter--1td0v6v.md` |

| Raw | True | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--36-user-guide-part-04-water-ice-filter--1td0v6v.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--36-user-guide-part-04-water-ice-filter--1gfp1gh.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--36-user-guide-part-04-water-ice-filter--612x3m.md', 'wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--41-user-guide-part-06-troubleshooting-other--u3xq2c.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-06-troubleshooting-other.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: source
title: Dispenser, ice maker, water filters and performance
tags: [water filter, ice maker, dispenser]
related: [water-dispenser-operation, ice-maker-operation, water-filter-performance]
created: 2026-10-19
updated: 2026-10-19
sources: ["fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md"]
authors: []
year: 2026
url: ""
```

**Raw rank-1 excerpt (search evidence):**
```text
## Dispenser, ice maker, water filters and performance

**Original manual:** *Refrigerators — Bottom Freezer: Owner’s Manual & Installation Instructions*. **Source file:** `user-guide.pdf`.

### GE-DISPENSER-001 — External and internal dispenser operation, initial purge

**Knowledge ID:** `GE-DISPENSER-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-kitchenaid-krff507hps-h01-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`kitchenaid_KRFF507HPS-H01` (hard)</h3>
**Question:** My ice cubes are hollow. What inlet water-pressure range is required, and what two water-supply checks does the troubleshooting section recommend?


**Gold:** The supply pressure should be 35–120 psi (241–827 kPa). Check that the shutoff valve is fully open and that the water-source line is not kinked; the guide also advises checking the filter if the problem persists.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--32-user-guide-part-02-installation--xofqwp.md` |

| Raw | True | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-02-installation.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--32-user-guide-part-02-installation--xofqwp.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--41-user-guide-part-06-troubleshooting-other--1o0awky.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--40-user-guide-part-05-troubleshooting-core--bf8bd6.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--36-user-guide-part-04-water-ice-filter--1gfp1gh.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-02-installation.md', 'raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-05-troubleshooting.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-02-installation.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: source
title: Installation, water pressure, doors and leveling
tags: []
related: [installation-instructions, water-pressure-requirements, door-removal-and-reattachment, leveling-and-door-alignment]
created: 2026-10-19
updated: 2026-10-19
sources: ["fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-02-installation.md"]
---
# Installation, Water Pressure, Doors
```

**Raw rank-1 excerpt (search evidence):**
```text
o see whether or not you need to remove the refrigerator doors to move the refrigerator
- into your home. If door removal is necessary, see the following instructions.
- IMPORTANT: If the refrigerator was previously installed and you are moving it out of the home, before you begin, turn the refrigerator

### KA-WATER-PRESSURE-001 — Household water supply, pressure and RO considerations

**Knowledge ID:** `KA-WATER-PRESSURE-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** KitchenAid French Door Bottom Mount Refrigerator models to which guide W11218735B applies; features marked “on some models” require inspection of fitted options  
**Source:** French Door Bottom Mount Refrigerator — Use &
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-kitchenaid-krff507hps-h06-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`kitchenaid_KRFF507HPS-H06` (hard)</h3>
**Question:** The water from my dispenser is warm after I have filled several large jugs. How long should I wait for it to cool again, and what button sequence starts Measured Fill calibration?


**Gold:** After a large draw of water, allow about 3 hours for the supply to cool completely. To initiate Measured Fill calibration, press and hold OPTIONS and LOCK simultaneously for 3 seconds (after flushing the dispenser system).


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--36-user-guide-part-04-water-ice-filter--1gfp1gh.md` |

| Raw | True | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-04-water-ice-filter.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--36-user-guide-part-04-water-ice-filter--1gfp1gh.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--41-user-guide-part-06-troubleshooting-other--1o0awky.md', 'wiki/concepts/water-ice-dispenser-calibration.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--32-user-guide-part-02-installation--xofqwp.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
e measured fill feature of the water and ice dispensers.

1. **Check the filter and water supply** before calibration.
2. **Use a measuring cup** to dispense water accurately.
3. **Follow the control panel sequence** for calibration.

**Troubleshooting Tips**:
- Ensure the door is closed and the control lock is disengaged.
- Flush the water system after connecting to a new water source.

## Ice Maker Operation

The guide outlines the operation and maintenance of the ice maker.

1. **Confirm the ice maker is ON** and that the water supply is connected.
2. **Check the ice storage bin** for proper seating.
3. **Follow the printed instructions** for cleaning and maintenance.

**Important Notes**
```

**Raw rank-1 excerpt (search evidence):**
```text
em” on printed pages 17–18 show the locking direction and correct seating.

**Additional documented conditions — printed page 17:**
- 5. Turn the filter clockwise 90 degrees (1/4 turn), until it locks
- Do not use with water that is microbiologically unsafe or into the housing.
- NOTE: If the filter is not correctly locked into the housing, the or after the system. Systems certified for cyst reduction
- water dispenser will not operate. Water will not flow from the may be used on disinfected waters that may contain
- 1. Locate the accessory packet in the refrigerator and remove
- 2. Take the water filter out of its packaging and remove the cover
- 6. While the compartment door is still open,
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-ticket-samsung-rf28k9070sg-h10-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`samsung_RF28K9070SG-H10` (hard)</h3>
**Question:** A technician mentions compressor error 81, and I am wondering whether I should attempt a repair myself. What checks does that error call for and what safety limitation does the service sheet state?


**Gold:** Error 81 is a compressor-run error. The technician sheet calls for checking inverter-PCB soldering/shorts, whether its 15 V DC output is below 13.5 V, and the compressor/refrigeration cycle. The sheet explicitly says it is for qualified technicians with electrical, electronic and mechanical experien…


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | False | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--12-repair-guide--28-repair-guide-part-01-safety--1rb7f19.md` |

| Raw | True | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--12-repair-guide--28-repair-guide-part-01-safety--1rb7f19.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--12-repair-guide--33-repair-guide-part-02-diagnostics--1d667m8.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--12-repair-guide--37-repair-guide-part-05-troubleshooting--6fgjk9.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--12-repair-guide--40-repair-guide-part-06-electronics-wiring--nljgbe.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
---
type: source
title: Technician safety and service authorization boundaries
authors: []
year: 2026
url: ""
venue: ""
tags: [safety, repair, technician-only]
related: []
sources: ["fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-01-safety.md"]
created: 2026-10-19
updated: 2026-10-19
---
# Samsung RF28K9070SG Repair Guide: Part 01 - Safety

This document serves as a safety guide for the Samsung RF28K9070SG refrigerator model, emphasizing the importance of professional handling for repairs. It outlines critical safety protocols and the boundaries of consumer-level repairs.

## Technician-only Safety Boundary

- **Definition**: Guidelines indicating that certain repair procedures are restricted to trained technicians due to safety risks.
- **Importance**: Emphasizes the need for professional handling of complex repairs to prevent injury or damage.
- **Evidence**…
```

**Raw rank-1 excerpt (search evidence):**
```text
## Diagnostic mode and error-code troubleshooting

**Original manual:** *Fast Track Troubleshooting*. **Source file:** `repair-guide.pdf`.

### SFT-CONTROL-001 — Demo mode, load mode and diagnostic mode buttons

**Knowledge ID:** `SFT-CONTROL-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; in
```

_Analysis:_ Wiki hybrid often surfaces **compiled abstractions** (concepts/entities) or **partial OCR shards**; raw chunk still contains **manual sentences** matching gold numbers/phrasing.


<h3 id="test-wr-wiki-wins-samples" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">Wiki wins (raw failed) — samples</h3>

<h3 id="test-wr-ticket-ge-gne27jymfs-h05-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H05` (hard)</h3>
**Question:** My GNE27J shows “tc,” and some food by the back vent is freezing. What does “tc” mean and what should I do about the food?


**Gold:** “tc” means TurboCool is activated. Move food away from the rear air vent; if cooling is still too strong, adjust the refrigerator to a warmer setting incrementally after TurboCool is no longer preventing a refrigerator temperature adjustment.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--41-user-guide-part-06-troubleshooting-other--u3xq2c.md` |

| Raw | False | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-06-troubleshooting-other.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--41-user-guide-part-06-troubleshooting-other--u3xq2c.md', 'wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--40-user-guide-part-05-troubleshooting-core--ouzaxc.md', 'wiki/entities/gne27jymfs.md', 'wiki/entities/ge-profile.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-05-troubleshooting-core.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-05-troubleshooting-core.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
E-SYMPTOM-033 — My Display is Showing tc

**Knowledge ID:** `GE-SYMPTOM-033`  
**Applies to:** GE / GE Profile bottom-freezer refrigerators of 18, 19, 21, 22, 24, 25, 26, and 27 cu ft in publication 49-1000472 Rev. 9.  
**Customer symptom:** My display is showing tc.  

**Documented cause/check pairs:**
- **Possible cause:** Turbo Cool function is activated.  
  **Documented check/action:** See Controls section.

### GE-SYMPTOM-034 — Water Filter Indicator Light Changed Color

**Knowledge ID:** `GE-SYMPTOM-034`  
**Applies to:** GE / GE Profile bottom-freezer refrigerators of 18, 19, 21, 22, 24, 25, 26, and 27 cu ft in publication 49-1000472 Rev. 9.  
**Customer symptom:** Water filter indic
```

**Raw rank-1 excerpt (search evidence):**
```text
ely  
**Source:** Refrigerators — Bottom Freezer: Owner’s Manual & Installation Instructions, PDF page(s) 47.  
**Customer phrasing:** My display is showing tc; GE refrigerator my display is showing tc.  

**Customer symptom:** My display is showing tc.

**Documented cause/check pairs from the manual:**
- **Possible cause:** Turbo Cool function is activated.  **Documented check/action:** See Controls section

**Expected result/limits:** Perform relevant customer-safe checks first. A listed possible cause is not an established diagnosis; if a cause/action line has unreadable font content, use the printed original table before giving unsafe instructions.

### GE-SYMPTOM-034 — Water filter indi
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-ge-gne27jymfs-h09-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H09` (hard)</h3>
**Question:** If the XWFE filter fails from a manufacturing defect shortly after I buy the fridge, how long is the limited filter warranty, and what is the ordinary replacement interval?


**Gold:** The refrigerator warranty gives the included water filter a 30-day limited warranty from the refrigerator’s original purchase date for defects in materials or workmanship. Separately, the XWFE filter is normally replaced about every 6 months or sooner if flow decreases.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--36-user-guide-part-07-warranty-support--107uu9u.md` |

| Raw | False | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-07-warranty-support.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--36-user-guide-part-07-warranty-support--107uu9u.md', 'wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--36-user-guide-part-04-water-ice-filter--1td0v6v.md', 'wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--41-user-guide-part-06-troubleshooting-other--u3xq2c.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--36-user-guide-part-04-water-ice-filter--1gfp1gh.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-07-warranty-support.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-07-warranty-support.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-06-troubleshooting-other.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
upport, GE Appliances]
related: [ge-appliances, limited-warranty, water-filter-warranty, consumer-support]
sources: ["fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-07-warranty-support.md"]
authors: []
year: 2026
url: ""
venue: ""
---

## Warranty Overview

This document provides warranty and support information for GE Appliances refrigerators, specifically focusing on the limited warranty, water filter warranty, and consumer support options.

### Limited Warranty

- **Coverage**: One-year limited warranty on parts that fail due to defects in materials or workmanship.
- **Exclusions**: Labor and related service as specified.
- **Extended Coverage**: Five-year sealed system
```

**Raw rank-1 excerpt (search evidence):**
```text
## Warranty, regulatory information and support

**Original manual:** *Refrigerators — Bottom Freezer: Owner’s Manual & Installation Instructions*. **Source file:** `user-guide.pdf`.

### GE-WARRANTY-001 — GE Appliances refrigerator limited warranty and regional applicability

**Knowledge ID:** `GE-WARRANTY-001`  
**Evidence:** [DOCUMENTED]  
**Applies to:** GE / GE Profile bottom-freezer refrigerators of 18, 19, 21,
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-ge-gne27jymfs-h10-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`ge_GNE27JYMFS-H10` (hard)</h3>
**Question:** The GNE27J refrigerator seems too warm after I changed the settings and the icemaker is not making ice yet. What stabilization time applies to the temperature setting, and what separate initial ice-maker delay is normal?


**Gold:** Allow 24 hours for the refrigerator temperature to stabilize at the selected recommended setting. A newly installed refrigerator can separately take 12–24 hours to start making ice.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--38-user-guide-part-03-controls-operation--unr63u.md` |

| Raw | False | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--38-user-guide-part-03-controls-operation--unr63u.md', 'wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--36-user-guide-part-04-water-ice-filter--1td0v6v.md', 'wiki/sources/22-fridge-docs-split-less--12-gegne27jymfs--10-user-guide--41-user-guide-part-06-troubleshooting-other--u3xq2c.md', 'wiki/concepts/ice-maker-operation.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-05-troubleshooting-core.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-04-service-procedures.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-05-troubleshooting-core.md', 'raw/sources/fridge-docs-split-less/ge_GNE27JYMFS/user-guide/user-guide--part-05-troubleshooting-core.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
, top, and external controls.

## Rotary Control

### Overview
- **Models:** GBE21D / GBE21A
- **Functionality:** Adjusts refrigerator/freezer settings at dedicated internal controls.
- **Stabilization Time:** 24 hours for temperatures to stabilize after adjustment.

### Instructions
1. Set the knob to the desired position.
2. Wait for 24 hours to allow the temperature to stabilize.

### Electrical Precaution
- Power cannot be disconnected by any setting on the control panel.

### Visual Reference
- Refer to **Figure B** on printed page 8 of the owner's manual for knob-position guidance.

## Top Control

### Overview
- **Models:** GNE27J / GNE27E and others in the GDE and GWE families.
- **F
```

**Raw rank-1 excerpt (search evidence):**
```text
D replacement indicator light for the water filter
- cartridge on the dispenser, the red filter light will start

**Additional verified text-layer details — printed page 15:**
- Water Filter Cartridge - XWFE (on some models)(Cont.)
- USING THE REFRIGERATOR: Water Filter Cartridge - XWFE
- WARNING To reduce the risk associated with choking, do not allow children under 3 years of age to
- have access to small parts during the installation of this product. The disposable filter cartridge should be
- replaced every 6 months at the rated capacity, or sooner if a noticeable reduction in flow rate occurs.
- important for products that are filtering your water. GE Appliances has not qualified non-G
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-samsung-rf28k9070sg-h01-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`samsung_RF28K9070SG-H01` (hard)</h3>
**Question:** I have just replaced the Samsung water filter but the water dispenser still will not work. How do I reset and flush after replacement, and what panel control might be blocking dispensing?


**Gold:** Hold Crushed Ice for 3 seconds to reset the filter life detector, reopen the water valve, and dispense water for about 7 minutes to clear air and impurities. If Control Lock is enabled, hold Lighting/Control Lock for 3 seconds to unlock; Control Lock prevents water and ice dispensing even if the lev…


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--36-user-guide-part-04-water-ice-filter--612x3m.md` |

| Raw | False | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--36-user-guide-part-04-water-ice-filter--612x3m.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--32-user-guide-part-02-installation--jcvco2.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--41-user-guide-part-03-controls-connectivity--kv4x03.md', 'wiki/sources/22-fridge-docs-split-less--20-kitchenaidkrff507hps--10-user-guide--36-user-guide-part-04-water-ice-filter--1gfp1gh.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/kitchenaid_KRFF507HPS/user-guide/user-guide--part-06-troubleshooting-other.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-04-water-ice-filter.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-04-water-ice-filter.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
icator:

1. Unlock the old cartridge by turning its knob **90° counterclockwise**.
2. Pull it straight out, keeping it aligned to avoid leaks.
3. Insert the replacement and turn clockwise to lock.
4. Hold **Crushed Ice for 3 seconds** to reset the filter-life detector.
5. Open the water valve and run water through the dispenser for approximately **7 minutes** to purge air and impurities.

**Note:** Use only Samsung-provided or approved replacement filters.

## Ice Bucket Management

To prevent clumping and ensure proper ice production, follow these instructions for removing and reseating the ice bucket:

1. Hold the bottom and side of the bucket; gently lift and pull it out.
2. Remove remain
```

**Raw rank-1 excerpt (search evidence):**
```text
d delivery chute every 2 weeks.

**Applicability and answerability:** A listed cause is not a confirmed diagnosis. These are the issue-specific manufacturer troubleshooting rows; if a source table continues across pages, check the referenced printed page and model options before acting.

### KA-SYMPTOM-027 — The ice dispenser jams while dispensing crushed ice

**Knowledge ID:** `KA-SYMPTOM-027`  
**Evidence:** [DOCUMENTED]  
**Applies to:** KitchenAid French Door Bottom Mount Refrigerator models to which guide W11218735B applies; features marked “on some models” require inspection of fitted options  
**Source:** French Door Bottom Mount Refrigerator — Use & Care Guide, PDF page(s) 38.  
**Cu
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h3 id="test-wr-ticket-samsung-rf28k9070sg-h04-hard" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">`samsung_RF28K9070SG-H04` (hard)</h3>
**Question:** My freezer is not as cold as I want. What temperature range can I select, and what basic operating checks should I make before requesting repair?


**Gold:** The Freezer button lets you select temperatures from 5°F (−15°C) to −8°F (−23°C). Before requesting repair, check power connection, the temperature setting, direct sunlight/nearby heat sources, ventilation clearance and whether too much food is blocking air circulation.


| Arm | Pass | Rank-1 base file |
|-----|------|------------------|

| Wiki | True | `brain/retail-md-learned/wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--41-user-guide-part-03-controls-connectivity--kv4x03.md` |

| Raw | False | `brain/retail-md-learned/raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md` |


Wiki top-5: `['wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--41-user-guide-part-03-controls-connectivity--kv4x03.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--12-repair-guide--33-repair-guide-part-02-diagnostics--1d667m8.md', 'wiki/sources/22-fridge-docs-split-less--18-samsungrf28k9070sg--10-user-guide--45-user-guide-part-05-troubleshooting-appliance--x2hw9n.md', 'wiki/entities/samsung-rf28k9070sg.md', 'wiki/index.md']`


Raw top-5: `['raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/user-guide/user-guide--part-05-troubleshooting-appliance.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-02-diagnostics.md', 'raw/sources/fridge-docs-split-less/samsung_RF28K9070SG/repair-guide/repair-guide--part-05-troubleshooting.md']`


**Wiki rank-1 excerpt (search evidence):**
```text
the panel continues to show the measured compartment temperature until it reaches the set target, then displays the chosen value. This delay is normal; repeated adjustments are unnecessary.

## Temperature Control Features

### Freezer Setting and Power Freeze
- **Set Temperature:** Press **Freezer** repeatedly to select a temperature from **5°F (−15°C) to −8°F (−23°C)**.
- **Power Freeze Activation:** Hold **Freezer** for **3 seconds** to activate; hold again for 3 seconds to deactivate. It runs the freezer at full power temporarily.

### Fridge Temperature and Power Cool
- **Set Temperature:** Press **Fridge** repeatedly; selectable values are **34–44°F (1–7°C)**.
- **Power Cool Activation
```

**Raw rank-1 excerpt (search evidence):**
```text
plies to:** Models RF28K9070, RF22K9381 and RF28K9380 as printed on this service sheet; individual procedures may be feature-specific  
**Source:** Fast Track Troubleshooting, PDF page(s) 1.  
**Customer phrasing:** Why does my fridge show 0 FF?; How to enter diagnostic mode?; Which buttons show load status?.  

**Demo / cooling-off mode:** Hold **Freezer + Fridge + Door Alarm** for **6 seconds** until the display shows **0–FF**. Repeat to exit.

**Load mode:** Hold **Freezer + Fridge + Flex Zone** for **6 seconds**. The on/off LEDs blink. Release the buttons to see load status, then use the load-display mapping in `SFT-LOAD-001` (printed page 3).

**Diagnostic mode:** Hold **Freezer + Fridg
```

_Analysis:_ Wiki **source shard** or graph-assisted path includes the fact; raw top chunk is **off-topic**, **wrong SKU**, or **missing** the gold span in the 8k window.


<h2 id="test-wr-7-appendix" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">7. Appendix — full ticket lists</h2>

**Lane B raw-only (24):** `ge_GNE27JYMFS-E02`, `ge_GNE27JYMFS-E07`, `ge_GNE27JYMFS-E08`, `ge_GNE27JYMFS-E09`, `ge_GNE27JYMFS-H05`, `ge_GNE27JYMFS-H06`, `kitchenaid_KRFF507HPS-E01`, `kitchenaid_KRFF507HPS-E03`, `kitchenaid_KRFF507HPS-E04`, `kitchenaid_KRFF507HPS-E06`, `kitchenaid_KRFF507HPS-E07`, `kitchenaid_KRFF507HPS-E08`, `kitchenaid_KRFF507HPS-E09`, `kitchenaid_KRFF507HPS-E10`, `kitchenaid_KRFF507HPS-H06`, `kitchenaid_KRFF507HPS-H09`, `kitchenaid_KRFF507HPS-H10`, `samsung_RF28K9070SG-E01`, `samsung_RF28K9070SG-E03`, `samsung_RF28K9070SG-E05` …


**Lane B wiki-only (5):** `ge_GNE27JYMFS-E04`, `ge_GNE27JYMFS-E05`, `ge_GNE27JYMFS-H04`, `samsung_RF28K9070SG-E02`, `samsung_RF28K9070SG-E08`


**Lane C raw-only (26):** `ge_GNE27JYMFS-E01`, `ge_GNE27JYMFS-E04`, `ge_GNE27JYMFS-E05`, `ge_GNE27JYMFS-E06`, `ge_GNE27JYMFS-E08`, `ge_GNE27JYMFS-E09`, `ge_GNE27JYMFS-E10`, `ge_GNE27JYMFS-H05`, `ge_GNE27JYMFS-H06`, `kitchenaid_KRFF507HPS-E01`, `kitchenaid_KRFF507HPS-E02`, `kitchenaid_KRFF507HPS-E04`, `kitchenaid_KRFF507HPS-E05`, `kitchenaid_KRFF507HPS-E06`, `kitchenaid_KRFF507HPS-E07`, `kitchenaid_KRFF507HPS-E09`, `kitchenaid_KRFF507HPS-H01`, `kitchenaid_KRFF507HPS-H04`, `samsung_RF28K9070SG-E03`, `samsung_RF28K9070SG-E05` …


**Lane C wiki-only (0):** ``


**Lane D raw-only (9):** `ge_GNE27JYMFS-E07`, `ge_GNE27JYMFS-E08`, `ge_GNE27JYMFS-H04`, `ge_GNE27JYMFS-H08`, `kitchenaid_KRFF507HPS-E06`, `kitchenaid_KRFF507HPS-H01`, `kitchenaid_KRFF507HPS-H06`, `samsung_RF28K9070SG-E08`, `samsung_RF28K9070SG-H10`


**Lane D wiki-only (11):** `ge_GNE27JYMFS-H05`, `ge_GNE27JYMFS-H09`, `ge_GNE27JYMFS-H10`, `kitchenaid_KRFF507HPS-E01`, `samsung_RF28K9070SG-E05`, `samsung_RF28K9070SG-E10`, `samsung_RF28K9070SG-H01`, `samsung_RF28K9070SG-H04`, `samsung_RF28K9070SG-H05`, `samsung_RF28K9070SG-H08`, `samsung_RF28K9070SG-H09`

