<h1 id="fridge-docs-title" style="color:#0d47a1;font-size:1.5em;font-weight:700;border-bottom:2px solid #90caf9;padding-bottom:0.25em;margin-top:0">Fridge PDF sources (FRU catalog — 3 models)</h1>

Mirrors `brain/retail/raw/sources/samsung-docs/` layout: each folder is **`<brand>_<model>`** with `user-guide.pdf` and `repair-guide.pdf`.

<h2 id="outline" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">Document outline</h2>

1. [Manual inventory](#inventory) — folders and download sources.
2. [FRU CSV note](#fru-note) — Samsung SKU in sales data.

<h2 id="inventory" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">1. Manual inventory</h2>

<table>
<thead>
<tr style="background:#1565c0;color:white"><th>Folder</th><th>FRU SKU</th><th>File</th><th>Source (fetched from)</th></tr>
</thead>
<tbody>
<tr><td style="background:#e3f2fd" rowspan="2"><code>samsung_RF28K9070SG/</code></td><td rowspan="2">RF28K9070SG</td><td><code>user-guide.pdf</code></td><td style="background:#e8f5e9"><a href="https://downloadcenter.samsung.com/content/UM/201904/20190416171610412/T-TYPE_RF9000K_DA68-03378A-06_EN_MES_CFR.pdf">Samsung Download Center — RF28K9070SR/SG family user manual</a> · <a href="https://www.samsung.com/us/support/model/RF28K9070SG/AA/">model support page</a></td></tr>
<tr><td><code>repair-guide.pdf</code></td><td style="background:#fff8e1"><a href="https://documents.cdn.ifixit.com/CjlaUWPD1NqHvip5.pdf">Fast Track troubleshooting (RF28K9070; technician data sheet)</a></td></tr>
<tr><td style="background:#e3f2fd" rowspan="2"><code>ge_GNE27JYMFS/</code></td><td rowspan="2">GNE27JYMFS</td><td><code>user-guide.pdf</code></td><td style="background:#e8f5e9"><a href="https://assets.unilogcorp.com/267/ITEM/DOC/GE_Appliances_GNE27JYMFS_Owners_User_Manual.pdf">GE Appliances GNE27JYMFS owner’s manual (CDN)</a> · <a href="https://products.geappliances.com/appliance/gea-specs/GNE27JYMFS/support">GE support page</a></td></tr>
<tr><td><code>repair-guide.pdf</code></td><td style="background:#fff8e1">Same file as user guide (troubleshooting &amp; care are in the owner manual)</td></tr>
<tr><td style="background:#e3f2fd" rowspan="2"><code>kitchenaid_KRFF507HPS/</code></td><td rowspan="2">KRFF507HPS</td><td><code>user-guide.pdf</code></td><td style="background:#e8f5e9"><a href="https://linqcdn.avbportal.com/documents/8948d3ce-8d51-4bc4-abc4-728d39b4d980.pdf">W11218735 Use &amp; Care (dealer CDN mirror)</a> · official doc: <a href="https://www.kitchenaid.com/content/dam/global/documents/201901/owners-manual-w11218735-revB.pdf">KitchenAid content/dam PDF</a> · <a href="https://www.kitchenaid.com/major-appliances/refrigeration/refrigerators/p.KRFF507HPS.html">KRFF507HPS product page</a></td></tr>
<tr><td><code>repair-guide.pdf</code></td><td style="background:#fff8e1">Same file as user guide (troubleshooting is in Use &amp; Care)</td></tr>
</tbody>
</table>

<h2 id="fru-note" style="color:#1565c0;font-size:1.22em;font-weight:650;border-left:4px solid #42a5f5;padding-left:10px;margin-top:1.1em">2. FRU CSV note</h2>

The only Samsung refrigerator in `ultra-fru-genai-analytics-new` is **RF28K9070SG** (no alternate Samsung SKU without changing the sales CSV).

Rescan / ingest after adding or replacing PDFs.
