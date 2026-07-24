from app.services.evaluation import holdout_result_summary


def test_holdout_result_summary_finds_first_heldout_rank() -> None:
    summary = holdout_result_summary([9, 7, 5, 3], {5, 1})

    assert summary == {"hit": True, "rank": 3}


def test_holdout_result_summary_handles_miss() -> None:
    summary = holdout_result_summary([9, 7, 5], {1, 2})

    assert summary == {"hit": False, "rank": 0}
