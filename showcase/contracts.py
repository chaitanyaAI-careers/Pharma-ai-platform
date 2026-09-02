from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable


@dataclass(frozen=True)
class RetrievalEvidence:
    source_id: str
    chunk_id: str
    excerpt: str


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: tuple[str, ...]


@dataclass(frozen=True)
class SummaryResult:
    title: str
    highlights: tuple[str, ...]
    trace_id: str


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ReviewItem:
    item_id: str
    trace_id: str
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer: str | None = None


def format_citation(evidence: RetrievalEvidence) -> str:
    """Return a stable, recruiter-safe citation representation."""
    return f"{evidence.source_id}#chunk-{evidence.chunk_id}"


def build_grounded_answer(
    answer: str,
    evidence: Iterable[RetrievalEvidence],
) -> GroundedAnswer:
    """
    Build an answer contract from already-retrieved evidence.

    This showcase intentionally does not expose retrieval, ranking,
    chunking, embedding, or prompt-generation implementation.
    """
    citations = tuple(dict.fromkeys(format_citation(item) for item in evidence))

    return GroundedAnswer(
        answer=answer.strip(),
        citations=citations,
    )


def build_summary_result(
    title: str,
    highlights: Iterable[str],
    trace_id: str,
) -> SummaryResult:
    """
    Build a structured summary contract.

    Actual pharmaceutical summarization heuristics remain private.
    """
    cleaned = tuple(
        highlight.strip()
        for highlight in highlights
        if highlight and highlight.strip()
    )

    return SummaryResult(
        title=title.strip() or "Untitled Document",
        highlights=cleaned,
        trace_id=trace_id.strip(),
    )


def transition_review(
    item: ReviewItem,
    target: ReviewStatus,
    reviewer: str,
) -> ReviewItem:
    """
    Demonstrate a minimal human-review state transition.

    The production review workflow remains private.
    """
    reviewer = reviewer.strip()

    if not reviewer:
        raise ValueError("reviewer is required")

    if item.status is not ReviewStatus.PENDING:
        raise ValueError("only pending review items can be decided")

    if target not in {ReviewStatus.APPROVED, ReviewStatus.REJECTED}:
        raise ValueError("target must be approved or rejected")

    return replace(
        item,
        status=target,
        reviewer=reviewer,
    )
