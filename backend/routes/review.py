from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend import crud, models
from backend.schemas import ReviewRequest, ReviewReportResponse

from agents.coordinator_agent import CoordinatorAgent
from agents.aggregator_agent import AggregatorAgent
from verifier.verifier_agent import VerifierAgent

router = APIRouter()

coordinator = CoordinatorAgent()
verifier = VerifierAgent()
aggregator = AggregatorAgent()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/review")
def review_code(
    payload: ReviewRequest,
    db: Session = Depends(get_db),
):
    if not payload.code or not payload.code.strip():
        raise HTTPException(
            status_code=400,
            detail="Code must not be empty.",
        )

    try:
        findings = coordinator.review_pull_request(payload.code)
        verification = verifier.verify(findings)

        final_report = aggregator.aggregate(verification["findings"])

        saved_review = crud.create_review_report(
            db=db,
            code=payload.code,
            report=final_report,
        )

        return {
            "review_id": saved_review.id,
            "findings": findings,
            "verified_findings": verification["findings"],
            "agent_errors": verification["agent_errors"],
            "review_complete": verification["complete"],
            "final_report": final_report,
        }

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Review failed: {str(exc)}",
        ) from exc


@router.get("/reviews", response_model=list[ReviewReportResponse])
def list_reviews(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    return crud.get_review_reports(db, limit=limit)


@router.get("/reviews/{review_id}", response_model=ReviewReportResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
):
    review = crud.get_review_report(db, review_id)

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found.",
        )

    return review
