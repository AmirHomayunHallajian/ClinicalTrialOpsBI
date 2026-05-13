# DAX Measures
```DAX
Total Screened = SUM(fact_recruitment[screened_count])
Total Randomized = SUM(fact_recruitment[randomized_count])
Total Withdrawn = SUM(fact_recruitment[withdrawn_count])
Screen Failure Rate = DIVIDE(SUM(fact_recruitment[screen_failed_count]), [Total Screened])
Randomization Rate = DIVIDE([Total Randomized], [Total Screened])
Enrollment Target = SUM(fact_recruitment[monthly_target])
Enrollment Attainment % = DIVIDE([Total Randomized], [Enrollment Target])
Monthly Recruitment Velocity = AVERAGE(fact_recruitment[randomized_count])
Sites Below Target = CALCULATE(DISTINCTCOUNT(fact_recruitment[site_id]), FILTER(VALUES(fact_recruitment[site_id]), CALCULATE(SUM(fact_recruitment[randomized_count])) < CALCULATE(SUM(fact_recruitment[monthly_target]))))
```
```DAX
Planned Sites = DISTINCTCOUNT(fact_site_activation[site_id])
Activated Sites = CALCULATE(DISTINCTCOUNT(fact_site_activation[site_id]), fact_site_activation[activation_status] = "Activated")
Activation Rate = DIVIDE([Activated Sites], [Planned Sites])
Delayed Sites = CALCULATE(DISTINCTCOUNT(fact_site_activation[site_id]), fact_site_activation[activation_status] = "Delayed")
Avg Activation Delay Days = AVERAGE(fact_site_activation[activation_delay_days])
Median Selection to Activation Days = MEDIAN(fact_site_activation[selection_to_activation_days])
Median Contract Cycle Days = MEDIAN(fact_site_activation[contract_cycle_days])
Median Regulatory Cycle Days = MEDIAN(fact_site_activation[regulatory_cycle_days])
```
```DAX
Total Queries = DISTINCTCOUNT(fact_queries[query_id])
Open Queries = CALCULATE([Total Queries], fact_queries[query_status] = "Open")
Resolved Queries = CALCULATE([Total Queries], fact_queries[query_status] = "Resolved")
Overdue Queries = CALCULATE([Total Queries], fact_queries[query_status] = "Overdue")
Avg Query Resolution Days = AVERAGE(fact_queries[resolution_days])
Median Query Resolution Days = MEDIAN(fact_queries[resolution_days])
Query SLA Compliance % = DIVIDE(CALCULATE([Total Queries], fact_queries[sla_met] = TRUE()), [Total Queries])
High Priority Open Queries = CALCULATE([Total Queries], fact_queries[query_priority] = "High", fact_queries[query_status] <> "Resolved")
```
```DAX
Required Documents = CALCULATE(COUNTROWS(fact_documents), fact_documents[required_flag] = TRUE())
Received Documents = CALCULATE(COUNTROWS(fact_documents), fact_documents[received_flag] = TRUE())
Approved Documents = CALCULATE(COUNTROWS(fact_documents), fact_documents[approved_flag] = TRUE())
Missing Documents = CALCULATE(COUNTROWS(fact_documents), fact_documents[document_status] = "Missing")
Overdue Documents = CALCULATE(COUNTROWS(fact_documents), fact_documents[document_status] = "Overdue")
Critical Missing Documents = CALCULATE([Missing Documents], dim_document_type[is_critical] = TRUE())
Document Completion % = DIVIDE([Approved Documents], [Required Documents])
Critical Document Completion % = DIVIDE(CALCULATE([Approved Documents], dim_document_type[is_critical] = TRUE()), CALCULATE([Required Documents], dim_document_type[is_critical] = TRUE()))
```
```DAX
Avg Cycle Days = AVERAGE(fact_cycle_time[cycle_days])
Median Cycle Days = MEDIAN(fact_cycle_time[cycle_days])
Target Met % = DIVIDE(CALCULATE(COUNTROWS(fact_cycle_time), fact_cycle_time[target_met] = TRUE()), COUNTROWS(fact_cycle_time))
Avg Days Over Target = AVERAGEX(fact_cycle_time, MAX(0, fact_cycle_time[cycle_days] - fact_cycle_time[target_days]))
Active Users = CALCULATE(DISTINCTCOUNT(fact_adoption[user_id]), fact_adoption[active_user_flag] = TRUE())
Training Completion % = DIVIDE(CALCULATE(COUNTROWS(fact_adoption), fact_adoption[training_completed_flag] = TRUE()), COUNTROWS(fact_adoption))
Average Adoption Score = AVERAGE(fact_adoption[adoption_score])
Average EDC Usage Score = AVERAGE(fact_adoption[edc_usage_score])
Average eTMF Usage Score = AVERAGE(fact_adoption[etmf_usage_score])
Average Days Since Last Login = AVERAGE(fact_adoption[days_since_last_login])
Low Adoption Users = CALCULATE(DISTINCTCOUNT(fact_adoption[user_id]), fact_adoption[adoption_score] < 50)
```
