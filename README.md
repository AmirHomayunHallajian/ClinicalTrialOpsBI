# ClinicalTrialOpsBI: Power BI Dashboard for Clinical Trial Operations

## Overview
This project demonstrates a full clinical-trial operations analytics portfolio build using **fully synthetic/mock data**. No real patient data or PHI is used.

## Problem
Clinical operations teams must track recruitment, site activation, query resolution, missing documents, cycle time, and digital adoption across studies and countries.

## Solution
Synthetic data is generated with Python and modeled as a star schema for Power BI, with KPI definitions, DAX measures, and dashboard wireframes.

## Why This Project Matters
- BI dashboard design
- KPI definition
- Clinical operations analytics
- Star-schema modeling
- DAX measure design
- Business storytelling for pharma/CRO operations

## Dataset
Tables: dim_date, dim_study, dim_site, dim_document_type, dim_user, fact_recruitment, fact_site_activation, fact_queries, fact_documents, fact_cycle_time, fact_adoption.

## Business Questions Answered
Are studies recruiting on target? Which sites/countries are delayed? Are queries within SLA? Which critical documents are missing? Are users adopting trial systems?

## Dashboard Pages
1. Executive Overview
2. Recruitment Performance
3. Site Activation and Start-Up
4. Data Quality and Query Management
5. Document Completeness / TMF Readiness
6. Adoption and Operational Behavior

## Tech Stack
Power BI, DAX, Power Query, Python, pandas, numpy, CSV.

## Repository Structure
See folders under `data/`, `scripts/`, `powerbi/`, `docs/`, `assets/`, and `tests/`.


## Website Preview
A redesigned static landing page is available at `index.html` for portfolio presentation and stakeholder review. It summarizes the project narrative, dashboard pages, data model, and reproducible workflow in a responsive web format.

Open it locally from the repository root:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000/`.

## Quickstart
1. `python -m venv .venv`
2. `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. `python scripts/generate_mock_clinical_ops_data.py`
5. `python scripts/validate_data.py`
6. Build in Power BI from `data/processed/` and follow `powerbi/*.md` docs.

## Suggested Power BI Visuals
KPI cards, trends, stacked bars, backlog tables, funnels, country comparisons, and role-based adoption charts.

## KPI Definitions
See `docs/clinical_ops_kpi_definitions.md`.

## Screenshots
Add report screenshots to `screenshots/` after building the `.pbix` locally.

## Future Improvements
Forecast enrollment, anomaly detection, RLS, incremental refresh, Service publish, drill-through pages, automated refresh simulation, advanced cohort analytics, and study risk scoring.

