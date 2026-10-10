from sqlalchemy.orm import Session

from backend import models


def create_pr(db: Session, pr):
    new_pr = models.PullRequest(
        pr_number=pr.pr_number,
        repository=pr.repository,
        title=pr.title,
        author=pr.author,
    )

    db.add(new_pr)
    db.commit()
    db.refresh(new_pr)

    return new_pr


def create_finding(db, agent_name, severity, issue, recommendation):
    finding = models.Finding(
        agent_name=agent_name,
        severity=severity,
        issue=issue,
        recommendation=recommendation,
    )

    db.add(finding)
    db.commit()
    db.refresh(finding)

    return finding


def create_review_report(db: Session, code: str, report: str):
    review = models.ReviewReport(
        code=code,
        report=report,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def get_review_reports(db: Session, limit: int = 50):
    return (
        db.query(models.ReviewReport)
        .order_by(models.ReviewReport.id.desc())
        .limit(limit)
        .all()
    )


def get_review_report(db: Session, review_id: int):
    return (
        db.query(models.ReviewReport)
        .filter(models.ReviewReport.id == review_id)
        .first()
    )
