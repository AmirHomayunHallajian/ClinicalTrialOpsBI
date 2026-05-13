from pathlib import Path
import pandas as pd

from scripts.generate_mock_clinical_ops_data import main


def test_generation_outputs_exist():
    main()
    out = Path("data/processed")
    expected = [
        "dim_date.csv", "dim_study.csv", "dim_site.csv", "dim_document_type.csv", "dim_user.csv",
        "fact_recruitment.csv", "fact_site_activation.csv", "fact_queries.csv", "fact_documents.csv",
        "fact_cycle_time.csv", "fact_adoption.csv",
    ]
    for name in expected:
        assert (out / name).exists()


def test_non_empty_and_constraints():
    rec = pd.read_csv("data/processed/fact_recruitment.csv")
    q = pd.read_csv("data/processed/fact_queries.csv")
    ad = pd.read_csv("data/processed/fact_adoption.csv")

    assert not rec.empty and not q.empty and not ad.empty
    assert (rec["randomized_count"] <= rec["screened_count"]).all()
    assert (rec["screen_failed_count"] <= rec["screened_count"]).all()
    assert (q["resolution_days"].dropna() >= 0).all()
    assert ((ad["adoption_score"] >= 0) & (ad["adoption_score"] <= 100)).all()
