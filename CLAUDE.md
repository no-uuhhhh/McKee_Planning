# McKeesport Parcel Map — Claude Context

## Project Goal
Interactive parcel lookup tool for McKeesport, PA. Intended for a team to identify key parcels, their owner, use, assessed value, and sale history. Delivered as a self-contained HTML file rendered from a Quarto document using R.

## Current State
The working deliverable is `mckeesport_parcel_map.qmd`, which renders to `mckeesport_parcel_map.html`.

The map shows:
- ~11,495 parcel polygons for all of McKeesport (wards 1–12)
- Parcels color-coded by land use CLASS (residential=blue, commercial=orange, government=purple, industrial=dark red, farm/forest=green, other=slate)
- Exempt parcels (TAXCODE = "E") rendered at lower opacity
- Hover labels with: address, PIN, classification, tax status, homestead flag, neighborhood, assessed values (county + fair market), 3 sale records, physical details (style, year built, condition, beds/baths, sq ft, lot size), mailing address
- 3 basemap options (CartoDB light, OpenStreetMap, Satellite)
- Scale bar and layer control
- Notes section at the bottom explaining data fields

Styled after `Example/Revere_Climate_Risk_Explore.qmd` — same CSS conventions, pipe-chained Leaflet calls, `lapply(label_html, HTML)` pattern for hover labels.

## Rendering
```bash
cd "/Users/njohnson/Desktop/McKee Parcel Map"
/Users/njohnson/.local/quarto/bin/quarto render "mckeesport_parcel_map.qmd"
```
Always `cd` into the directory first — Quarto CLI breaks on paths with spaces.

## Data Sources & Structure

### 1. Parcel Boundaries (Shapefile)
**Path:** `AlleghenyCounty_Parcels/AlleghenyCounty_Parcels202510.shp`
- 585,977 total Allegheny County parcels
- CRS: EPSG:2272 (PA State Plane South, survey feet) — must `st_transform(4326)` for Leaflet
- McKeesport is MUNICODE 401–412 (12 wards) — filtered at read time via SQL `WHERE MUNICODE BETWEEN 401 AND 412`
- Key field: `PIN` (16-char parcel ID, e.g. `0381K00071000000`) — join key to assessment CSV
- Other fields: MAPBLOCKLOT, CALCACREAGE, NOTES — mostly spatial metadata, not used in map

### 2. Assessment Attributes (CSV)
**Path:** `Parcel Data/data/property-assessments.csv`
- Source: WPRDC (wprdc.org/parcels-n-at), generated October 30, 2025
- ~11,495 McKeesport rows (MUNICODE 401–412), 84 columns
- Read with `col_types = cols(DEEDBOOK=col_character(), DEEDPAGE=col_character(), STYLE=col_character())` — these must be forced to character or they parse incorrectly
- All string columns need `str_trim()` — data has heavy whitespace padding

**Key columns used in map:**
| Column | Description |
|--------|-------------|
| PIN | Join key (matches shapefile PIN) |
| PROPERTYHOUSENUM, PROPERTYADDRESS | Street address |
| MUNICODE / MUNIDESC | Ward number / description (401–412 = McKeesport wards) |
| NEIGHDESC | Neighborhood name |
| TAXCODE | T=Taxable, E=Exempt, P=PURTA |
| TAXDESC | Human-readable tax status |
| CLASS / CLASSDESC | Broad use class (R/C/G/I/U/F/O) |
| USECODE / USEDESC | Detailed use (~200 categories) |
| LOTAREA | Lot size in sq ft |
| HOMESTEADFLAG | "HOM" if homestead exemption applies |
| SALEDATE, SALEPRICE, SALECODE, SALEDESC | Most recent sale |
| PREVSALEDATE, PREVSALEPRICE | 2nd most recent sale |
| PREVSALEDATE2, PREVSALEPRICE2 | 3rd most recent sale |
| CHANGENOTICEADDRESS1–4 | Owner mailing address (split across 4 fields) |
| COUNTYLAND, COUNTYBUILDING, COUNTYTOTAL | County assessed values |
| FAIRMARKETLAND, FAIRMARKETBUILDING, FAIRMARKETTOTAL | Fair market values |
| STYLEDESC | Architectural style |
| YEARBLT | Year built (0 = vacant/unknown) |
| CONDITIONDESC, GRADEDESC | Condition and grade descriptions |
| BEDROOMS, FULLBATHS, HALFBATHS | Room counts |
| FINISHEDLIVINGAREA | Finished living area in sq ft (0 = vacant) |

**Note:** PROPERTYOWNER is NOT in this CSV. It exists in `County Assessor Data/1_AC Property Assessments_20251001.xlsx` (298MB, join on PARID=PIN) but was skipped for v1 due to file size. Owner identity currently inferred from mailing address fields only.

### 3. County Assessor Data (Excel — not yet used)
**Path:** `County Assessor Data/1_AC Property Assessments_20251001.xlsx`
- Full Allegheny County assessment data (298MB), join key = PARID (equivalent to PIN)
- Contains PROPERTYOWNER field — the main reason to use this file in a future version
- Also: `3_AC Property Sale Transactions_20251001.xlsx` (56MB) for extended sale history

### 4. Example / Reference
**Path:** `Example/Revere_Climate_Risk_Explore.qmd`
- Flood risk explorer for Revere, MA — the style template for this project
- Patterns to follow: YAML front matter, CSS block structure, pipe-chained Leaflet calls, `lapply(label_html, HTML)` for hover labels, `addGroupedLayersControl` for complex layer panels, `hideGroup` + JS `onRender` for exclusive layer groups

## Known Gotchas
- McKeesport spans **12 wards** (MUNICODE 401–412) — easy to accidentally filter to just one ward (407 was the original mistake)
- YEARBLT=0 and SALEPRICE=0 should display as "—" not literal 0
- Shapefile MUNICODE is numeric; CSV MUNICODE is also numeric — no type mismatch on join
- `st_read()` SQL filter syntax: table name must be quoted if it contains numbers (e.g. `"AlleghenyCounty_Parcels202510"`)
