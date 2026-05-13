"""Generate synthetic clinical trial operations data for Power BI demos."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

RANDOM_SEED = 42
N_STUDIES = 4
N_SITES = 48
START_DATE = "2024-01-01"
END_DATE = "2025-12-31"
SLA_DAYS = 5


COUNTRIES = [
    "Netherlands",
    "Germany",
    "Turkey",
    "United Kingdom",
    "Spain",
    "Italy",
    "United States",
    "Canada",
]

ROLES = [
    "Clinical Research Associate",
    "Study Coordinator",
    "Principal Investigator",
    "Data Manager",
    "Clinical Trial Manager",
]

DOCUMENT_TYPES = [
    (1, "Ethics Approval", "Regulatory", True),
    (2, "Informed Consent Form", "Patient", True),
    (3, "Investigator CV", "Personnel", True),
    (4, "Site Delegation Log", "Site Operations", True),
    (5, "Training Certificate", "Training", False),
    (6, "Lab Certification", "Laboratory", True),
    (7, "Monitoring Visit Report", "Monitoring", False),
    (8, "Site Initiation Visit Report", "Monitoring", True),
]


def make_dim_date() -> pd.DataFrame:
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    df = pd.DataFrame({"date": dates})
    iso = df["date"].dt.isocalendar()
    df["year"] = df["date"].dt.year
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["year_month"] = df["date"].dt.strftime("%Y-%m")
    df["week"] = iso.week.astype(int)
    df["day_of_week"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.weekday >= 5
    return df


def make_dim_study(rng: np.random.Generator) -> pd.DataFrame:
    phases = ["Phase II", "Phase III", "Observational"]
    areas = ["Neuroscience", "Oncology", "Immunology", "Cardiology"]
    sponsors = ["NovaCura Biotech", "Asterion Pharma", "HelixTrials CRO", "VitaSphere Therapeutics"]
    base_start = pd.Timestamp("2024-01-01")

    rows = []
    for i in range(1, N_STUDIES + 1):
        start = base_start + pd.Timedelta(days=int(rng.integers(0, 180)))
        end = start + pd.Timedelta(days=int(rng.integers(420, 900)))
        target = int(rng.integers(220, 650))
        rows.append(
            {
                "study_id": f"ST{i:03d}",
                "study_name": f"CTO-{100 + i}",
                "phase": phases[i % len(phases)],
                "therapeutic_area": areas[i % len(areas)],
                "sponsor": sponsors[i % len(sponsors)],
                "planned_start_date": start,
                "planned_end_date": end,
                "target_enrollment": target,
                "study_status": rng.choice(["Planning", "Active", "Active", "Active", "Close-Out"]),
            }
        )
    return pd.DataFrame(rows)


def make_dim_site(studies: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    site_rows = []
    for i in range(1, N_SITES + 1):
        study = studies.sample(1, random_state=int(rng.integers(1, 1_000_000))).iloc[0]
        planned = pd.Timestamp(study["planned_start_date"]) + pd.Timedelta(days=int(rng.integers(20, 220)))
        delay = int(rng.integers(-10, 75))
        actual = planned + pd.Timedelta(days=delay)
        country = rng.choice(COUNTRIES)
        status = "Activated" if actual <= pd.Timestamp(END_DATE) else "In Start-Up"
        site_rows.append(
            {
                "site_id": f"SI{i:03d}",
                "study_id": study["study_id"],
                "site_name": f"{country} Clinical Site {i:02d}",
                "country": country,
                "region": "North America" if country in ["United States", "Canada"] else "Europe",
                "principal_investigator": f"Dr. PI {i:02d}",
                "site_tier": rng.choice(["Tier 1", "Tier 2", "Tier 3"], p=[0.3, 0.5, 0.2]),
                "planned_activation_date": planned,
                "actual_activation_date": actual,
                "site_status": status,
                "enrollment_target": int(rng.integers(12, 40)),
                "activation_delay_days": delay,
            }
        )
    return pd.DataFrame(site_rows)


def make_dim_document_type() -> pd.DataFrame:
    return pd.DataFrame(DOCUMENT_TYPES, columns=["document_type_id", "document_type", "document_category", "is_critical"])


def make_dim_user(sites: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows: List[Dict] = []
    uid = 1
    for _, site in sites.iterrows():
        n_users = int(rng.integers(3, 7))
        for _ in range(n_users):
            role = rng.choice(ROLES, p=[0.25, 0.35, 0.15, 0.15, 0.10])
            rows.append(
                {
                    "user_id": f"U{uid:04d}",
                    "user_role": role,
                    "site_id": site["site_id"],
                    "study_id": site["study_id"],
                    "country": site["country"],
                    "user_status": rng.choice(["Active", "Active", "Active", "Inactive"]),
                }
            )
            uid += 1
    return pd.DataFrame(rows)


def make_fact_recruitment(sites: pd.DataFrame, months: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    rid = 1
    country_mult = {"United States": 1.2, "Germany": 1.1, "Canada": 1.05, "Turkey": 0.95, "Spain": 0.9, "Italy": 0.88, "Netherlands": 1.0, "United Kingdom": 1.0}
    for _, site in sites.iterrows():
        cum = 0
        monthly_target = max(1, int(site["enrollment_target"] / len(months) * 1.8))
        perf = rng.uniform(0.7, 1.4)
        for m in months:
            if m < pd.Timestamp(site["actual_activation_date"]).to_period("M").to_timestamp():
                screened = int(rng.integers(0, 2))
            else:
                screened = int(max(0, rng.normal(10 * perf * country_mult[site["country"]], 3)))
            failed = int(rng.integers(0, screened + 1)) if screened > 0 else 0
            randomized = int(max(0, screened - failed - rng.integers(0, 2))) if screened > 0 else 0
            withdrawn = int(rng.integers(0, randomized + 1)) if randomized > 0 and rng.random() < 0.15 else 0
            cum += randomized
            rows.append(
                {
                    "recruitment_id": f"R{rid:06d}",
                    "study_id": site["study_id"],
                    "site_id": site["site_id"],
                    "date": m,
                    "screened_count": screened,
                    "screen_failed_count": failed,
                    "randomized_count": randomized,
                    "withdrawn_count": withdrawn,
                    "cumulative_randomized": cum,
                    "monthly_target": monthly_target,
                    "enrollment_target": site["enrollment_target"],
                }
            )
            rid += 1
    return pd.DataFrame(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(RANDOM_SEED)
    dim_date = make_dim_date()
    dim_study = make_dim_study(rng)
    dim_site = make_dim_site(dim_study, rng)
    dim_document_type = make_dim_document_type()
    dim_user = make_dim_user(dim_site, rng)

    months = pd.date_range(START_DATE, END_DATE, freq="MS")
    fact_recruitment = make_fact_recruitment(dim_site, months, rng)

    fact_site_activation = dim_site[["study_id", "site_id", "country", "planned_activation_date", "activation_delay_days"]].copy()
    fact_site_activation.insert(0, "activation_id", [f"A{i:05d}" for i in range(1, len(fact_site_activation) + 1)])
    fact_site_activation["site_selected_date"] = fact_site_activation["planned_activation_date"] - pd.to_timedelta(rng.integers(100, 180, len(fact_site_activation)), unit="D")
    fact_site_activation["contract_sent_date"] = fact_site_activation["site_selected_date"] + pd.to_timedelta(rng.integers(7, 20, len(fact_site_activation)), unit="D")
    fact_site_activation["contract_signed_date"] = fact_site_activation["contract_sent_date"] + pd.to_timedelta(rng.integers(10, 45, len(fact_site_activation)), unit="D")
    fact_site_activation["regulatory_submitted_date"] = fact_site_activation["contract_signed_date"] + pd.to_timedelta(rng.integers(5, 20, len(fact_site_activation)), unit="D")
    fact_site_activation["regulatory_approved_date"] = fact_site_activation["regulatory_submitted_date"] + pd.to_timedelta(rng.integers(15, 60, len(fact_site_activation)), unit="D")
    fact_site_activation["site_initiation_visit_date"] = fact_site_activation["regulatory_approved_date"] + pd.to_timedelta(rng.integers(3, 20, len(fact_site_activation)), unit="D")
    fact_site_activation["activated_date"] = fact_site_activation["planned_activation_date"] + pd.to_timedelta(fact_site_activation["activation_delay_days"], unit="D")
    fact_site_activation["activation_status"] = np.where(fact_site_activation["activation_delay_days"] > 30, "Delayed", "Activated")
    fact_site_activation["selection_to_activation_days"] = (fact_site_activation["activated_date"] - fact_site_activation["site_selected_date"]).dt.days
    fact_site_activation["contract_cycle_days"] = (fact_site_activation["contract_signed_date"] - fact_site_activation["contract_sent_date"]).dt.days
    fact_site_activation["regulatory_cycle_days"] = (fact_site_activation["regulatory_approved_date"] - fact_site_activation["regulatory_submitted_date"]).dt.days

    query_rows = []
    for i in range(1, 1401):
        site = dim_site.sample(1, random_state=int(rng.integers(1, 1_000_000))).iloc[0]
        open_date = pd.Timestamp(START_DATE) + pd.Timedelta(days=int(rng.integers(0, 700)))
        is_resolved = rng.random() < 0.78
        resolution_days = int(max(0, rng.normal(4.8, 2.8))) if is_resolved else np.nan
        resolved_date = open_date + pd.Timedelta(days=int(resolution_days)) if is_resolved else pd.NaT
        age_days = int((pd.Timestamp(END_DATE) - open_date).days) if not is_resolved else int(resolution_days)
        status = "Resolved" if is_resolved else ("Overdue" if age_days > SLA_DAYS else "Open")
        query_rows.append({
            "query_id": f"Q{i:06d}", "study_id": site["study_id"], "site_id": site["site_id"], "subject_id": f"SUB{rng.integers(1,7000):05d}",
            "query_open_date": open_date, "query_resolved_date": resolved_date, "query_status": status,
            "query_category": rng.choice(["Missing Data", "Inconsistent Value", "Adverse Event Clarification", "Lab Value Out of Range", "Date Discrepancy", "Eligibility Criteria"]),
            "query_age_days": age_days, "resolution_days": resolution_days, "sla_days": SLA_DAYS,
            "sla_met": bool(is_resolved and resolution_days <= SLA_DAYS), "query_priority": rng.choice(["Low", "Medium", "High"], p=[0.3, 0.5, 0.2])
        })
    fact_queries = pd.DataFrame(query_rows)

    doc_rows = []
    did = 1
    for _, site in dim_site.iterrows():
        for _, dtype in dim_document_type.iterrows():
            due = pd.Timestamp(site["planned_activation_date"]) + pd.Timedelta(days=int(rng.integers(-30, 90)))
            rec = rng.random() < (0.88 if dtype["is_critical"] else 0.80)
            appr = rec and rng.random() < 0.9
            rec_date = due + pd.Timedelta(days=int(rng.integers(-10, 40))) if rec else pd.NaT
            overdue = int((pd.Timestamp(END_DATE) - due).days) if (not rec and due < pd.Timestamp(END_DATE)) else 0
            status = "Approved" if appr else "Received" if rec else "Overdue" if overdue > 0 else "Missing"
            doc_rows.append({"document_record_id": f"D{did:06d}", "study_id": site["study_id"], "site_id": site["site_id"], "document_type_id": dtype["document_type_id"], "required_flag": True, "received_flag": rec, "approved_flag": appr, "due_date": due, "received_date": rec_date, "days_overdue": overdue, "document_status": status})
            did += 1
    fact_documents = pd.DataFrame(doc_rows)

    cycle_rows = []
    cid = 1
    processes = [("Site Selection to Activation", 140), ("Contract Sent to Signed", 30), ("Regulatory Submission to Approval", 35), ("SIV to First Patient In", 45), ("Query Open to Resolution", 5), ("Document Due to Approval", 20)]
    for _, site in dim_site.iterrows():
        for pname, target in processes:
            start = pd.Timestamp(START_DATE) + pd.Timedelta(days=int(rng.integers(0, 600)))
            days = int(max(1, rng.normal(target * 1.05, max(2, target * 0.25))))
            end = start + pd.Timedelta(days=days)
            cycle_rows.append({"cycle_id": f"C{cid:06d}", "study_id": site["study_id"], "site_id": site["site_id"], "process_name": pname, "start_date": start, "end_date": end, "cycle_days": days, "target_days": target, "target_met": days <= target})
            cid += 1
    fact_cycle_time = pd.DataFrame(cycle_rows)

    adopt_rows = []
    aid = 1
    role_base = {"Clinical Research Associate": 72, "Study Coordinator": 74, "Principal Investigator": 65, "Data Manager": 78, "Clinical Trial Manager": 76}
    for _, user in dim_user.iterrows():
        for m in months:
            logins = int(max(0, rng.normal(10, 4)))
            forms = int(max(0, rng.normal(16, 6)))
            training = bool(rng.random() < 0.8)
            days_last = int(max(0, rng.normal(8, 6)))
            edc = float(np.clip(rng.normal(role_base[user["user_role"]], 12), 20, 100))
            etmf = float(np.clip(rng.normal(role_base[user["user_role"]] - 3, 14), 15, 100))
            score = float(np.clip(0.35 * edc + 0.30 * etmf + 0.20 * min(logins * 4, 100) + 0.15 * (100 if training else 40) - 0.8 * days_last, 0, 100))
            adopt_rows.append({"adoption_id": f"AD{aid:07d}", "study_id": user["study_id"], "site_id": user["site_id"], "user_id": user["user_id"], "date": m, "logins_count": logins, "forms_completed": forms, "training_completed_flag": training, "days_since_last_login": days_last, "edc_usage_score": round(edc, 2), "etmf_usage_score": round(etmf, 2), "adoption_score": round(score, 2), "active_user_flag": score >= 60})
            aid += 1
    fact_adoption = pd.DataFrame(adopt_rows)

    tables = {
        "dim_date.csv": dim_date,
        "dim_study.csv": dim_study,
        "dim_site.csv": dim_site,
        "dim_document_type.csv": dim_document_type,
        "dim_user.csv": dim_user,
        "fact_recruitment.csv": fact_recruitment,
        "fact_site_activation.csv": fact_site_activation,
        "fact_queries.csv": fact_queries,
        "fact_documents.csv": fact_documents,
        "fact_cycle_time.csv": fact_cycle_time,
        "fact_adoption.csv": fact_adoption,
    }

    for fname, df in tables.items():
        df.to_csv(out_dir / fname, index=False)

    print("Generated synthetic clinical operations data:")
    for fname, df in tables.items():
        print(f"- {fname}: {len(df):,} rows")


if __name__ == "__main__":
    main()
