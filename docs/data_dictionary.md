# Data Dictionary
All tables are synthetic and for demonstration only.

## Dimensions
- **dim_date**: date grain calendar table with year/quarter/month/week/day attributes.
- **dim_study**: study metadata (phase, therapeutic area, sponsor, target enrollment).
- **dim_site**: site metadata and activation planning/outcomes.
- **dim_document_type**: TMF/operational document taxonomy with criticality flag.
- **dim_user**: synthetic user records by role, site, and study.

## Facts
- **fact_recruitment**: site-study-month recruitment counts and targets.
- **fact_site_activation**: site start-up milestones and cycle durations.
- **fact_queries**: data query lifecycle, SLA, and priority.
- **fact_documents**: site-document completeness and overdue tracking.
- **fact_cycle_time**: cross-process operational durations vs target.
- **fact_adoption**: user-month digital behavior and adoption scoring.

Refer to column names in CSV headers in `data/processed/` for exact fields and definitions.
