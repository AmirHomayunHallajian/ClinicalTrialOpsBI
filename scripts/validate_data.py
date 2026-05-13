"""Validate generated synthetic clinical trial operations data."""
from pathlib import Path
import pandas as pd

EXPECTED = {
    "fact_recruitment.csv": ["randomized_count", "screened_count", "screen_failed_count"],
    "fact_queries.csv": ["resolution_days"],
    "fact_site_activation.csv": ["selection_to_activation_days", "contract_cycle_days", "regulatory_cycle_days"],
    "fact_adoption.csv": ["adoption_score"],
    "fact_documents.csv": ["document_status"],
}
DOC_STATUSES = {"Missing", "Received", "Approved", "Overdue"}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data" / "processed"
    errors = []

    for file_name, columns in EXPECTED.items():
        path = data_dir / file_name
        if not path.exists():
            errors.append(f"Missing file: {file_name}")
            continue
        df = pd.read_csv(path)
        for col in columns:
            if col not in df.columns:
                errors.append(f"{file_name} missing column: {col}")

        if file_name == "fact_recruitment.csv":
            bad = df[(df["randomized_count"] > df["screened_count"]) | (df["screen_failed_count"] > df["screened_count"])]
            if not bad.empty:
                errors.append("fact_recruitment has invalid counts")

        if file_name == "fact_queries.csv":
            bad = df[df["resolution_days"].notna() & (df["resolution_days"] < 0)]
            if not bad.empty:
                errors.append("fact_queries has negative resolution_days")

        if file_name == "fact_site_activation.csv":
            for col in ["selection_to_activation_days", "contract_cycle_days", "regulatory_cycle_days"]:
                if (df[col] < 0).any():
                    errors.append(f"fact_site_activation has negative {col}")

        if file_name == "fact_adoption.csv":
            if ((df["adoption_score"] < 0) | (df["adoption_score"] > 100)).any():
                errors.append("fact_adoption has out-of-range adoption_score")

        if file_name == "fact_documents.csv":
            bad_vals = set(df["document_status"].dropna().unique()) - DOC_STATUSES
            if bad_vals:
                errors.append(f"fact_documents has unexpected statuses: {sorted(bad_vals)}")

    if errors:
        print("Validation FAILED")
        for e in errors:
            print(f"- {e}")
        raise SystemExit(1)

    print("Validation PASSED")


if __name__ == "__main__":
    main()
