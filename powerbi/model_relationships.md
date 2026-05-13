# Model Relationships
Use single-direction filters from dimensions to facts.

- dim_study[study_id] 1:* all fact tables on study_id.
- dim_site[site_id] 1:* all fact tables on site_id.
- dim_date[date] 1:* fact_recruitment[date], fact_adoption[date].
- dim_document_type[document_type_id] 1:* fact_documents[document_type_id].
- dim_user[user_id] 1:* fact_adoption[user_id].

For other date fields in facts, use inactive relationships and `USERELATIONSHIP()` in DAX.

## Ambiguous Path Warning
Because `dim_site` includes `study_id`, avoid bidirectional cross-filtering between `dim_study` and `dim_site` through facts. Keep one-way filtering from dimensions to facts unless intentionally implementing study-site bridge logic.
