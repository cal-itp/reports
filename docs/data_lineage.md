# Where each part of a report page comes from

This document traces every visible element of a monthly agency report on
[reports.calitp.org](https://reports.calitp.org) back to its **source of truth** —
the JSON file, the reports-repo query, the BigQuery mart, and ultimately whether
the value is *measured from the agency's GTFS feeds* or *typed by hand into the
Cal-ITP Airtable*.

**Why this matters:** the machine-measured parts self-correct on every run. The
Airtable-sourced parts (agency name, source URLs, and **technology vendors**) are
human-maintained and can silently go stale — that is the root of every
"the report shows the wrong X" report we get. See
[The Airtable-sourced parts](#the-airtable-sourced-parts--the-ones-that-go-stale).

> An annotated visual version of this map (`reports-data-lineage.html` / `.png`)
> can be generated alongside this doc if a picture is preferred.

## Source-of-truth legend

| Tag | Meaning |
|-----|---------|
| **Schedule** | Parsed from the agency's downloaded **GTFS Schedule** zip (routes, stops, calendar, etc.) |
| **RT** | Measured from fetched **GTFS-Realtime** messages (trip updates, vehicle positions) |
| **Airtable** ★ | Typed/maintained by people in the Cal-ITP **"California Transit" Airtable** base |
| **External** | Scraped from another Cal-ITP website |
| **Derived** | Computed in the reports code itself (dates) |
| **＋Airtable** | Value is feed-measured, but still relies on Airtable for the org ↔ feed ↔ ITP-ID mapping |

## Full lineage table

| # | Page element | JSON file · reports fn | BigQuery mart → upstream | Source |
|---|--------------|------------------------|--------------------------|--------|
| 1 | Agency name + website link | `1_feed_info` · `_feed_info()` | `idx_monthly_reports_site` → `dim_organizations` | **Airtable** — Organizations |
| 2 | Report month · Prev/Next links | `get_dates_year_month()` + LAG/LEAD; `publish_date` | `idx_monthly_reports_site` (publish cadence) | Derived — report code / run date |
| 3 | Feed End Date | `1_feed_info` · `_feed_info()` | `idx…`.earliest_feed_end_date → `dim_feed_info` | Schedule — feed_info.txt / calendar |
| 4 | Days With No Service | `1_feed_info` | `idx…` → `fct_daily_reports_site_organization_scheduled_service_summary` | Schedule — parsed trips/calendar |
| 5 | Routes count | `1_feed_info` | `idx…`.route_ct → `dim_routes` | Schedule — routes.txt |
| 6 | Stops count | `1_feed_info` | `idx…`.stop_ct → `dim_stops` | Schedule — stops.txt |
| 7 | Has RT Feed ✓/✗ | `rt_feed_ids.json` · `generate_rt_feeds.py` | `idx…` (had_rt_files / check_rt) | RT **＋Airtable** — RT files fetched + dataset registered |
| 8 | "Show Source URLs" — feed names + download URLs | `index_report.json` · `generate_index_report.py` | `idx…`.feeds (gtfs_dataset_name + base64_url) | **Airtable** — GTFS datasets |
| 9 | "View Speedmap" button | `speedmap_urls.json` · `get_speedmap_urls()` | scrapes `analysis.calitp.org/rt/README.html` | External — matched to ITP id by org name |
| 10 | Trip Updates Completeness chart | `2_gtfs_rt_completeness` · `_rt_completeness()` | `fct_daily_trip_updates_vehicle_positions_completeness` | RT — RT vs schedule trips |
| 11 | Vehicle Positions Completeness chart | `2_gtfs_rt_completeness` | `fct_daily_trip_updates_vehicle_positions_completeness` | RT — RT vs schedule trips |
| 12 | Median TU Message Age chart | `2_ave_median_tu_age` · `_median_tu_age()` | `fct_daily_trip_updates_message_age_summary` + `dim_gtfs_datasets`/`dim_provider_gtfs_data` | RT **＋Airtable** — age measured; org via Airtable map |
| 13 | Median VP Message Age chart | `2_ave_median_vp_age` · `_median_vp_age()` | `fct_daily_vehicle_positions_latency_statistics` + `dim_provider_gtfs_data` | RT **＋Airtable** — latency measured; org via Airtable map |
| **14** | **Technology Vendors (Static / Realtime)** ★ | `1_feed_info` · `_feed_info()` (rt_vendors / schedule_vendors) | `fct_monthly_reports_site_organization_gtfs_vendors` → `dim_service_components` | **Airtable** — Service Components → Products → Organizations |
| 15 | Daily Service Level charts (Wkdy/Sat/Sun) | `2_daily_service_hours` · `_daily_service_hours()` | `fct_daily_reports_site_organization_scheduled_service_summary` | Schedule — parsed stop_times |
| 16 | Identifier Change charts (routes / stops) | `3_routes_changed` / `3_stops_changed` | `fct_monthly_route_id_changes` / `fct_monthly_stop_id_changes` | Schedule — month-over-month IDs |
| 17 | Guidelines — Schedule Compliance checks | `4_guideline_checks_schedule` · `_guideline_check()` | `fct_monthly_reports_site_organization_guideline_checks` (Compliance (Schedule)) | Schedule **＋manual\*** |
| 18 | Guidelines — RT Compliance checks | `4_guideline_checks_rt` · `_guideline_check()` | `fct_monthly_reports_site_organization_guideline_checks` (Compliance (RT)) | RT **＋manual\*** |
| 19 | MobilityData Validator notices | `5_validation_codes` · `_validation_codes()` | `fct_monthly_reports_site_organization_validation_codes` | Schedule — MobilityData Schedule Validator output |

\* Checks marked with an asterisk on the site are entered/updated by hand (`is_manual`), not computed from the feed.

## The Airtable-sourced parts — the ones that go stale

Only **three** visible elements are read from the human-maintained Airtable, and
they are exactly the ones prone to being wrong with **no code change**:

- **#1 — Agency name & website** (Organizations table)
- **#8 — Source-feed URLs & dataset names** (GTFS datasets table)
- **#14 — Technology Vendors** (Service Components → Products → Organizations)

Everything else is measured from the real GTFS / GTFS-RT feeds and re-derives
itself each run. (The `＋Airtable` rows are feed-measured *values* that still lean
on Airtable only for the org ↔ feed ↔ ITP-ID mapping.)

### Why the vendor field (#14) is especially fragile

- It surfaces the **vendor _organization_** linked to each service's components —
  `product_vendor_organization_name`, **not** the product name. So after an
  acquisition/rebrand the site shows the legacy company (e.g. `DoubleMap Inc.`
  even though the product is now "Passio Go").
- The model is **not historical** (`int_transit_database__service_components_dim`
  still carries a `TODO: make this table actually historical`; it forces
  `_valid_from = universal_first_val … _valid_to = 2099`). The **current** Airtable
  value is stamped onto **every** month, so one stale record makes every past
  report wrong at once — and one fix flips them all back.
- The reports mart does **not** filter on `is_active` / `end_date`, so adding a new
  vendor component without deactivating the old one makes the site list **both**.

### Worked examples (observed 2026-09)

| Agency | Site shows | Airtable Service Component still points at | Should be |
|--------|-----------|--------------------------------------------|-----------|
| Marin County Transit District (ITP 194) | `GMV Syncromatics Inc` | "Arrival predictions" → product `GMV/Syncromatics Sync` (record `recJ0Hv1WayoTt8gc`) | a **Swiftly** product |
| City of Arcadia (ITP 17) | `DoubleMap Inc.` | "Real-time info" → product `DoubleMap RealTime` (record `recMguIcQdpPEGCUp`) | **Passio Go!** / Passio Technologies |

In both cases the correct vendor already exists in Airtable (`Passio Technologies`,
`Swiftly Inc.`) — the service-component records just need repointing. **No code or
GTFS feed is wrong.**

## How a change propagates to the site

```
Airtable edit
  → daily warehouse sync (external_airtable → staging → dim_service_components)
  → mart rebuild (fct_monthly_reports_site_organization_gtfs_vendors)
  → reports-site regeneration (Refresh Data GitHub Action, or a manual run)
  → reports.calitp.org
```

The site will not change until that regeneration runs, even after Airtable is fixed.
Because the vendor model is not historical, when it does run **all** months update.

## Key references

- Reports queries: [`reports/generate_reports_data.py`](../reports/generate_reports_data.py),
  [`reports/generate_index_report.py`](../reports/generate_index_report.py),
  [`reports/generate_rt_feeds.py`](../reports/generate_rt_feeds.py)
- Page template: [`templates/report.html.jinja`](../templates/report.html.jinja)
- Vendor mart (in `data-infra`): `warehouse/models/mart/gtfs_quality/fct_monthly_reports_site_organization_gtfs_vendors.sql`
- Vendor dimension (in `data-infra`): `warehouse/models/intermediate/transit_database/dimensions/int_transit_database__service_components_dim.sql`
