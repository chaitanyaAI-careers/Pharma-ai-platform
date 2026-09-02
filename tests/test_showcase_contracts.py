import pytest

from showcase.contracts import (
    RetrievalEvidence,
    ReviewItem,
    ReviewStatus,
    build_grounded_answer,
    build_summary_result,
    format_citation,
    transition_review,
)


def test_format_citation_uses_source_and_chunk_identity():
    evidence = RetrievalEvidence(
        source_id="synthetic-guideline",
        chunk_id="7",
        excerpt="Synthetic evidence.",
    )

    assert format_citation(evidence) == "synthetic-guideline#chunk-7"


def test_grounded_answer_collects_unique_citations():
    evidence = [
        RetrievalEvidence("guideline-a", "1", "Synthetic evidence A."),
        RetrievalEvidence("guideline-a", "1", "Synthetic evidence A."),
        RetrievalEvidence("sop-b", "4", "Synthetic evidence B."),
    ]

    result = build_grounded_answer(
        "Evidence-backed example answer.",
        evidence,
    )

    assert result.answer == "Evidence-backed example answer."
    assert result.citations == (
        "guideline-a#chunk-1",
        "sop-b#chunk-4",
    )


def test_summary_contract_cleans_highlights():
    result = build_summary_result(
        title=" Synthetic Regulatory Document ",
        highlights=[
            " First synthetic highlight. ",
            "",
            "Second synthetic highlight.",
        ],
        trace_id="trace-example-001",
    )

    assert result.title == "Synthetic Regulatory Document"
    assert result.highlights == (
        "First synthetic highlight.",
        "Second synthetic highlight.",
    )
    assert result.trace_id == "trace-example-001"


def test_summary_contract_uses_safe_fallback_title():
    result = build_summary_result(
        title="",
        highlights=[],
        trace_id="trace-example-002",
    )

    assert result.title == "Untitled Document"


def test_pending_review_can_be_approved():
    item = ReviewItem(
        item_id="review-example-001",
        trace_id="trace-example-001",
    )

    result = transition_review(
        item,
        ReviewStatus.APPROVED,
        reviewer="synthetic-reviewer",
    )

    assert result.status is ReviewStatus.APPROVED
    assert result.reviewer == "synthetic-reviewer"


def test_pending_review_can_be_rejected():
    item = ReviewItem(
        item_id="review-example-002",
        trace_id="trace-example-002",
    )

    result = transition_review(
        item,
        ReviewStatus.REJECTED,
        reviewer="synthetic-reviewer",
    )

    assert result.status is ReviewStatus.REJECTED


def test_decided_review_cannot_be_decided_again():
    item = ReviewItem(
        item_id="review-example-003",
        trace_id="trace-example-003",
        status=ReviewStatus.APPROVED,
        reviewer="first-reviewer",
    )

    with pytest.raises(ValueError):
        transition_review(
            item,
            ReviewStatus.REJECTED,
            reviewer="second-reviewer",
        )


def test_review_requires_reviewer_identity():
    item = ReviewItem(
        item_id="review-example-004",
        trace_id="trace-example-004",
    )

    with pytest.raises(ValueError):
        transition_review(
            item,
            ReviewStatus.APPROVED,
            reviewer="",
        )
