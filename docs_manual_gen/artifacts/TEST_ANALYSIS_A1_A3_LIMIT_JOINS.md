<h1 id="limit-join-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">A1 vs A3 — limit-join questions</h1>

**Status:** Run `limit-join-l10-20261112`, 12 November 2026. Questions were locked in `tests/retail_multi_profiles/data/retail-limit-join-l10.json` before any score was visible. Answer model `gpt-4o-mini`. Judge `gemini-4-carbon`. Ranking, top-k, and prompts were left unchanged. Questions use bare model codes, so A3’s model filter stayed off.

<h2 id="limit-join-outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Headline](#limit-join-headline) — mean score and where each arm led.
2. [Pattern](#limit-join-pattern) — when the compiled page beats chunk search.
3. [Scoreboard](#limit-join-scoreboard) — ten rows, gold limit, and scores.
 3.1 [Answer matrix](#limit-join-matrix) — question, gold, scores, and excerpts.
4. [What each arm said](#limit-join-said) — one-line retrieval notes.
5. [Run notes](#limit-join-notes) — restart and file paths.

<h2 id="limit-join-headline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Headline</h2>

<p>A1 is compiled wiki search. A3 is chunk search over the manuals and the three news files. The graded score is 0–100. Correctness confidence stayed high on both arms, including wrong answers.</p>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Result</th><th>A1 wiki</th><th>A3 bundled</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">Mean graded score</td><td style="background:#e8f5e9"><strong>68.5</strong></td><td style="background:#ffebee"><strong>30.9</strong></td></tr>
<tr><td style="background:#e3f2fd">Rows ahead</td><td style="background:#e8f5e9"><strong>8 / 10</strong></td><td style="background:#fff3e0">2 / 10 (L03, L07)</td></tr>
<tr><td style="background:#e3f2fd">Mean correctness confidence</td><td>0.93</td><td>0.93</td></tr>
</tbody>
</table>

<h2 id="limit-join-pattern" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. Pattern</h2>

<p>A1 leads when the question names <strong>one model</strong>, the user guide still describes a feature, and a compiled page already states the limit in one place. That page is a news summary or a short entity line such as “the RF28K9070SG is not included in this update.” A3 then opens the guide, or another brand’s news, and answers from that text.</p>

<p>The pattern breaks when one question asks for three models at once. On L03, A1 opened three entity pages and the generic user-guide page, and missed the three news summaries. A3 scored higher there, and both answers still missed the gold refusals.</p>

<p>L01 is the earlier J02. L02 is J03. L03 is J04.</p>

<h2 id="limit-join-scoreboard" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">3. Scoreboard</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Id</th><th>Gold limit</th><th>A1</th><th>A3</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">L01</td><td>Scan-to-List, the inventory camera, and the new display cannot be added to an owned GNE27JYMFS.</td><td style="background:#e8f5e9">69</td><td>51</td></tr>
<tr><td style="background:#e3f2fd">L02</td><td>The KRFF507HPS door dispenser is not Intelligent Auto Fill.</td><td style="background:#e8f5e9">91</td><td style="background:#ffebee">22</td></tr>
<tr><td style="background:#e3f2fd">L03</td><td>Refuse the 2026 add-ons on all three models.</td><td style="background:#ffebee">14</td><td style="background:#fff3e0">24</td></tr>
<tr><td style="background:#e3f2fd">L04</td><td>The RF28K9070SG is not a target for Tizen 10.0, Gemini food identification, or a Family Hub display.</td><td style="background:#e8f5e9">100</td><td style="background:#ffebee">29</td></tr>
<tr><td style="background:#e3f2fd">L05</td><td>AutoView and Sphere Ice are not a retrofit, and the 2026 three-door models are not a direct replacement.</td><td style="background:#e8f5e9">66</td><td style="background:#ffebee">5</td></tr>
<tr><td style="background:#e3f2fd">L06</td><td>The Best Buy 4.3 and Home Depot 3.6 scores are not a failure rate and not a recall.</td><td>28</td><td>24</td></tr>
<tr><td style="background:#e3f2fd">L07</td><td>Drying produce is not automatic proof of a cooling failure.</td><td>79</td><td style="background:#e8f5e9">85</td></tr>
<tr><td style="background:#e3f2fd">L08</td><td>Discontinuation is not a recall, and it does not prove that parts or service are unavailable.</td><td style="background:#e8f5e9">91</td><td style="background:#ffebee">28</td></tr>
<tr><td style="background:#e3f2fd">L09</td><td>The Lowe’s 4.3 rating does not mean the KRFF507HPS includes Intelligent Auto Fill.</td><td style="background:#e8f5e9">62</td><td style="background:#ffebee">12</td></tr>
<tr><td style="background:#e3f2fd">L10</td><td>The ice bin using freezer space is not a failed freezer, and the GNE27JYMFS is no longer manufactured.</td><td style="background:#e8f5e9">85</td><td style="background:#ffebee">29</td></tr>
</tbody>
</table>

<h3 id="limit-join-matrix" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">3.1 Answer matrix</h3>

<p><strong>Legend:</strong> Green score cell = higher on that row. Gold and answer columns show about 35 words, then <code>...</code>. Full text is in the results file.</p>

<table>
<thead><tr style="background:#1565c0;color:white"><th>① Id</th><th>Question</th><th>Gold answer<br><small>reference</small></th><th>A1 score</th><th>A3 score</th><th>A1 answer<br><small>key excerpt</small></th><th>A3 answer<br><small>key excerpt</small></th></tr></thead>
<tbody>
<tr>
<td style="background:#e3f2fd"><code>L01</code></td>
<td style="background:#fafafa">A shopper has the GNE27JYMFS user guide open, then reads GE&#x27;s 2026 Kitchen Assistant announcement. Which of the announced features can be added to an owned GNE27JYMFS?</td>
<td style="background:#f3e5f5">None. Scan-to-List, the inventory camera, and the new display cannot be added to an owned GNE27JYMFS. The announcement describes a different GE Profile refrigerator, and the cited release does not identify that ...</td>
<td style="background:#e8f5e9"><strong>69</strong></td>
<td style="background:#ffebee"><strong>51</strong></td>
<td style="background:#e3f2fd">The GE GNE27JYMFS is no longer manufactured, and as such, it cannot be upgraded with the new features announced for the GE Profile Smart 4-Door Refrigerator with Kitchen Assistant. The new features include a built-in barcode scanner for ...</td>
<td style="background:#ede7f6">Based on the provided excerpts, the GNE27JYMFS refrigerator does not have the advanced features announced in GE&#x27;s 2026 Kitchen Assistant announcement. The new features, such as the built-in barcode scanner for grocery lists, the FridgeFocus interior camera, and ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L02</code></td>
<td style="background:#fafafa">The KRFF507HPS user guide describes a through-the-door dispenser. A 2026 KitchenAid note describes Intelligent Auto Fill. Are those the same feature on the KRFF507HPS?</td>
<td style="background:#f3e5f5">No. The KRFF507HPS has a through-the-door dispenser and does not include Intelligent Auto Fill. Intelligent Auto Fill is a hands-free system on newer KitchenAid refrigerators, and KitchenAid has not announced an upgrade ...</td>
<td style="background:#e8f5e9"><strong>91</strong></td>
<td style="background:#ffebee"><strong>22</strong></td>
<td style="background:#e3f2fd">The through-the-door dispenser feature on the KitchenAid KRFF507HPS refrigerator is not the same as the Intelligent Auto Fill feature mentioned in the 2026 KitchenAid note. The KRFF507HPS includes a traditional water dispenser that allows users to dispense a ...</td>
<td style="background:#ede7f6">The KRFF507HPS user guide describes a feature called &quot;Measured Fill,&quot; which allows users to dispense a specified amount of water with the touch of a few buttons. This feature requires calibration for optimal performance and can dispense water ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L03</code></td>
<td style="background:#fafafa">One briefing has to cover the GNE27JYMFS, the KRFF507HPS, and the RF28K9070SG. What must it refuse to promise from the 2026 announcements, even though each user guide is still in the file set?</td>
<td style="background:#f3e5f5">Refuse three promises. Scan-to-List, the inventory camera, and the new display cannot be added to the GNE27JYMFS. Intelligent Auto Fill cannot be promised for the KRFF507HPS. The September 2026 AI software update, ...</td>
<td style="background:#ffebee"><strong>14</strong></td>
<td style="background:#e8f5e9"><strong>24</strong></td>
<td style="background:#e3f2fd">In preparing the briefing for the GE GNE27JYMFS, KitchenAid KRFF507HPS, and Samsung RF28K9070SG, it is essential to clarify what cannot be promised regarding the 2026 announcements, despite the availability of user guides for each model. 1. **GE GNE27JYMFS**: ...</td>
<td style="background:#ede7f6">In the upcoming briefing covering the GNE27JYMFS, KRFF507HPS, and RF28K9070SG, it is essential to clarify that while user guides for these models are available, the briefing must refuse to promise any features or specifications related to the 2026 ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L04</code></td>
<td style="background:#fafafa">The RF28K9070SG guide describes the controls on that refrigerator. Does Samsung&#x27;s September 2026 AI software announcement add Tizen 10.0, Gemini food identification, or a Family Hub display to this model?</td>
<td style="background:#f3e5f5">No. Samsung&#x27;s September 2026 announcement does not name the RF28K9070SG as a supported update target. Those software features are described for selected newer Family Hub models. Staff must not promise Tizen 10.0, ...</td>
<td style="background:#e8f5e9"><strong>100</strong></td>
<td style="background:#ffebee"><strong>29</strong></td>
<td style="background:#e3f2fd">The Samsung RF28K9070SG refrigerator does not include the updates mentioned in Samsung&#x27;s September 2026 AI software announcement, specifically Tizen 10.0, Gemini food identification, or a Family Hub display. The announcement pertains to newer Family Hub refrigerator models, and ...</td>
<td style="background:#ede7f6">Based on the provided excerpts, there is no specific mention of Samsung&#x27;s September 2026 AI software announcement adding Tizen 10.0, Gemini food identification, or a Family Hub display to the RF28K9070SG model. The excerpts primarily focus on troubleshooting ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L05</code></td>
<td style="background:#fafafa">A buyer likes the RF28K9070SG FlexZone and asks whether the 2026 Bespoke three-door models are a direct replacement that adds AutoView and Sphere Ice to this unit.</td>
<td style="background:#f3e5f5">No. The 2026 Bespoke announcement describes three-door refrigerators, not a retrofit of the four-door RF28K9070SG. It does not call those models direct replacements, and it does not promise to add AutoView or ...</td>
<td style="background:#e8f5e9"><strong>66</strong></td>
<td style="background:#ffebee"><strong>5</strong></td>
<td style="background:#e3f2fd">The Samsung RF28K9070SG FlexZone is a well-regarded refrigerator known for its spacious interior and customizable storage options, particularly the FlexZone compartment that can be adjusted for different storage needs. However, it is important to note that this model ...</td>
<td style="background:#ede7f6">Based on the available excerpts, it is unclear whether the 2026 Bespoke three-door models are a direct replacement for the RF28K9070SG FlexZone. The excerpts do not provide specific information about the features of the 2026 models, such as ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L06</code></td>
<td style="background:#fafafa">Best Buy shows the RF28K9070SG at 4.3/5 and Home Depot shows 3.6/5, and both pools mention ice and cooling complaints. The service guide also has ice-maker pages. What may staff treat those two scores as?</td>
<td style="background:#f3e5f5">The two scores are separate retailer review pools, not a hardware failure rate and not a recall. Best Buy is 4.3/5 from 597 reviews with 84% recommending, and Home Depot is 3.6/5 ...</td>
<td style="background:#e8f5e9"><strong>28</strong></td>
<td style="background:#ffebee"><strong>24</strong></td>
<td style="background:#e3f2fd">Staff may treat the differing scores from Best Buy (4.3/5) and Home Depot (3.6/5) as indicative of varying consumer satisfaction levels with the Samsung RF28K9070SG refrigerator. The higher rating at Best Buy, where 84% of reviewers recommend the ...</td>
<td style="background:#ede7f6">Based on the provided excerpts, staff may treat the differing scores from Best Buy (4.3/5) and Home Depot (3.6/5) as indicative of varying customer satisfaction levels regarding the RF28K9070SG refrigerator. The presence of ice and cooling complaints mentioned ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L07</code></td>
<td style="background:#fafafa">An owner says vegetables are drying out in a GNE27JYMFS and points at the temperature-control pages in the user guide. How should staff use the RTINGS review before treating that as a cooling failure?</td>
<td style="background:#f3e5f5">RTINGS scores everyday use at 7.4/10 and produce preservation at 6.7/10. It attributes drying to a comparatively dry main compartment and crispers that do not fully stop leafy vegetables from drying. Drying ...</td>
<td style="background:#ffebee"><strong>79</strong></td>
<td style="background:#e8f5e9"><strong>85</strong></td>
<td style="background:#e3f2fd">To address the owner&#x27;s concern about vegetables drying out in the GE GNE27JYMFS refrigerator, staff should utilize the RTINGS review to provide context before concluding that there is a cooling failure. Here’s how to approach the situation: 1. ...</td>
<td style="background:#ede7f6">When addressing the owner&#x27;s concern about vegetables drying out in the GE GNE27JYMFS, staff should refer to the RTINGS review to provide context before concluding that there is a cooling failure. The review indicates that while the refrigerator ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L08</code></td>
<td style="background:#fafafa">The GNE27JYMFS user guide still lists Turbo Cool, the ice maker, and the water filter. A shopper asks whether that means GE is still manufacturing the model and whether a recall is underway.</td>
<td style="background:#f3e5f5">No. GE&#x27;s listing says the GNE27JYMFS is no longer being manufactured. Discontinuation is not a recall, and it does not prove that parts or service are unavailable. The user guide remains the ...</td>
<td style="background:#e8f5e9"><strong>91</strong></td>
<td style="background:#ffebee"><strong>28</strong></td>
<td style="background:#e3f2fd">The GE GNE27JYMFS model is no longer being manufactured, as confirmed by GE&#x27;s official product page. This means that while the user guide still lists features such as Turbo Cool, the ice maker, and the water filter, these ...</td>
<td style="background:#ede7f6">Based on the provided excerpts, it appears that the GNE27JYMFS user guide still includes references to features such as Turbo Cool, the ice maker, and the water filter. This suggests that the model is still supported in terms ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L09</code></td>
<td style="background:#fafafa">Lowe&#x27;s lists the KRFF507HPS at 4.3/5 from 1,908 reviews. A buyer asks whether that rating means the model includes the 2026 Intelligent Auto Fill dispenser.</td>
<td style="background:#f3e5f5">No. The 4.3/5 score is owner sentiment about the KRFF507HPS, with 84% of those reviewers recommending it. The KRFF507HPS does not include Intelligent Auto Fill, and a retailer rating is not an ...</td>
<td style="background:#e8f5e9"><strong>62</strong></td>
<td style="background:#ffebee"><strong>12</strong></td>
<td style="background:#e3f2fd">The KitchenAid® French Door Refrigerator (Model KRFF507HPS) does not include the 2026 Intelligent Auto Fill dispenser. While it features a through-the-door ice and water dispenser, it lacks the newer Intelligent Auto Fill technology that allows for hands-free water ...</td>
<td style="background:#ede7f6">Based on the available excerpts, there is no explicit mention of the 2026 Intelligent Auto Fill dispenser being included in the KitchenAid KRFF507HPS model. The excerpts primarily focus on the water and ice dispensing features, including instructions for ...</td>
</tr>
<tr>
<td style="background:#e3f2fd"><code>L10</code></td>
<td style="background:#fafafa">Staff have the GNE27JYMFS user guide open on the ice-maker pages. A caller says the ice bin takes too much freezer space and asks whether to treat that as a failed freezer and whether the model is still a current production refrigerator.</td>
<td style="background:#f3e5f5">Do not treat the ice bin&#x27;s use of freezer space as a failed freezer. RTINGS scored ice making 8.4/10 and noted that the bin consumes noticeable freezer-drawer space. Separately, the GNE27JYMFS is ...</td>
<td style="background:#e8f5e9"><strong>85</strong></td>
<td style="background:#ffebee"><strong>29</strong></td>
<td style="background:#e3f2fd">### Organizational Orientation on GNE27JYMFS Inquiry **Current Production Status:** The GE GNE27JYMFS model is **no longer manufactured** as of the latest status check on November 12, 2026. It is categorized as a clearance item and may still be ...</td>
<td style="background:#ede7f6">**Organizational Orientation:** Regarding the caller&#x27;s concern about the ice bin taking up too much freezer space, it is important to note that the ice storage bin is designed to be used specifically for ice and should not store ...</td>
</tr>
</tbody>
</table>

<h2 id="limit-join-said" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">4. What each arm said</h2>

<p>Full wording is in the results file. These lines keep the decisive sentence.</p>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Id</th><th>A1</th><th>A3</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd">L01</td><td style="background:#e8f5e9">Opened the GE news summary. Said the owned model cannot gain the barcode scanner or interior camera.</td><td>Also opened the GE news file, plus the user guide. Said the announced features are absent, with less of the successor limit.</td></tr>
<tr><td style="background:#e3f2fd">L02</td><td style="background:#e8f5e9">Opened the KitchenAid news summary. Said the door dispenser and Intelligent Auto Fill are different features.</td><td style="background:#ffebee">Opened only KitchenAid guide pages. Described Measured Fill. Confidence 0.95, correctness 0.</td></tr>
<tr><td style="background:#e3f2fd">L03</td><td style="background:#ffebee">Opened entity pages and the generic user-guide page. Missed the three news summaries.</td><td>Opened the GE news file and the three guides. Still missed the specific refusals.</td></tr>
<tr><td style="background:#e3f2fd">L04</td><td style="background:#e8f5e9">The Samsung entity page states that the RF28K9070SG is not in the Family Hub update. Score 100.</td><td style="background:#ffebee">Opened the GE news file and the Samsung repair guide. Said the excerpts do not mention the update.</td></tr>
<tr><td style="background:#e3f2fd">L05</td><td style="background:#e8f5e9">Opened the Samsung news summary. Kept the new-model features off this unit.</td><td style="background:#ffebee">Opened the GE news file and the GE guide. Said the 2026 Bespoke relationship was unclear. Confidence 0.95.</td></tr>
<tr><td style="background:#e3f2fd">L06</td><td>Opened the Samsung news summary, then described the two scores as satisfaction and skipped “not a failure rate.”</td><td>Opened Samsung guide pages only and gave the same satisfaction reading.</td></tr>
<tr><td style="background:#e3f2fd">L07</td><td>Opened the GE news summary and used the RTINGS drying note.</td><td style="background:#e8f5e9">Also opened the GE news file and scored slightly higher on the same limit.</td></tr>
<tr><td style="background:#e3f2fd">L08</td><td style="background:#e8f5e9">Opened the GE news summary. Said manufacture has stopped, and the guide features belong to the installed unit.</td><td style="background:#ffebee">Opened only user-guide pages. Treated the feature list as a sign the model is still supported.</td></tr>
<tr><td style="background:#e3f2fd">L09</td><td style="background:#e8f5e9">Opened the KitchenAid news summary and the Intelligent Auto Fill page. Said the rating does not add that feature.</td><td style="background:#ffebee">Opened only the KitchenAid guide. Said the excerpts never mention Auto Fill. Confidence 0.95, correctness 0.</td></tr>
<tr><td style="background:#e3f2fd">L10</td><td style="background:#e8f5e9">Opened the GE news summary. Said the model is no longer manufactured and separated that from the ice-bin complaint.</td><td style="background:#ffebee">Opened other brands’ guides and one GE guide page. Talked about what may be stored in the ice bin.</td></tr>
</tbody>
</table>

<h3 id="limit-join-questions" style="color:#00695c;font-size:1.05em;font-weight:600;margin-top:0.85em">4.1 Locked questions</h3>

1. **L01.** A shopper has the GNE27JYMFS user guide open, then reads GE’s 2026 Kitchen Assistant announcement. Which announced features can be added to an owned GNE27JYMFS?
2. **L02.** The KRFF507HPS user guide describes a through-the-door dispenser. A 2026 KitchenAid note describes Intelligent Auto Fill. Are those the same feature on the KRFF507HPS?
3. **L03.** One briefing has to cover the GNE27JYMFS, the KRFF507HPS, and the RF28K9070SG. What must it refuse to promise from the 2026 announcements, even though each user guide is still in the file set?
4. **L04.** The RF28K9070SG guide describes the controls on that refrigerator. Does Samsung’s September 2026 AI software announcement add Tizen 10.0, Gemini food identification, or a Family Hub display to this model?
5. **L05.** A buyer likes the RF28K9070SG FlexZone and asks whether the 2026 Bespoke three-door models are a direct replacement that adds AutoView and Sphere Ice to this unit.
6. **L06.** Best Buy shows the RF28K9070SG at 4.3/5 and Home Depot shows 3.6/5, and both pools mention ice and cooling complaints. What may staff treat those two scores as?
7. **L07.** An owner says vegetables are drying out in a GNE27JYMFS and points at the temperature-control pages. How should staff use the RTINGS review before treating that as a cooling failure?
8. **L08.** The GNE27JYMFS user guide still lists Turbo Cool, the ice maker, and the water filter. Does that mean GE is still manufacturing the model, and is a recall underway?
9. **L09.** Lowe’s lists the KRFF507HPS at 4.3/5 from 1,908 reviews. Does that rating mean the model includes the 2026 Intelligent Auto Fill dispenser?
10. **L10.** Staff have the GNE27JYMFS ice-maker pages open. The caller says the ice bin takes too much freezer space. Is that a failed freezer, and is the model still in production?

<h2 id="limit-join-notes" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">5. Run notes</h2>

<p>Wiki search timed out once, on the first attempt at L07. The local wiki process was restarted, and the run resumed with <code>--resume</code>. All 20 rows are in the results file. Question text was not edited after scores appeared.</p>

<p>Suite: <code>tests/retail_multi_profiles/data/retail-limit-join-l10.json</code>. Rows: <code>ops/runs/retail-cos-insight/limit-join-l10-20261112/results.jsonl</code>.</p>
