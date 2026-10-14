import re

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import SessionLocal
from agents.coordinator_agent import CoordinatorAgent
from agents.aggregator_agent import AggregatorAgent
from verifier.verifier_agent import VerifierAgent


router = APIRouter()

GITHUB_API = "https://api.github.com"
MAX_DIFF_CHARS = 30000
REQUEST_TIMEOUT = 20

coordinator = CoordinatorAgent()
verifier = VerifierAgent()
aggregator = AggregatorAgent()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def parse_pull_request_url(pr_url: str):
    pattern = (
        r"^https?://github\.com/"
        r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/(\d+)/?$"
    )
    match = re.match(pattern, pr_url.strip())

    if not match:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid GitHub PR URL. Expected format: "
                "https://github.com/owner/repository/pull/123"
            ),
        )

    owner, repo, number = match.groups()
    return owner, repo, int(number)


def fetch_github_pr(pr_url: str):
    owner, repo, pr_number = parse_pull_request_url(pr_url)

    api_url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ReviewPilot",
    }

    try:
        response = requests.get(
            api_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not connect to GitHub: {exc}",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Pull request not found or repository is private.",
        )

    if response.status_code == 403:
        raise HTTPException(
            status_code=429,
            detail="GitHub API denied the request or rate-limited access.",
        )

    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API returned status {response.status_code}.",
        )

    pr_data = response.json()

    try:
        diff_response = requests.get(
            api_url,
            headers={
                **headers,
                "Accept": "application/vnd.github.diff",
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not fetch the PR diff: {exc}",
        ) from exc

    if diff_response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Pull request diff could not be found.",
        )

    if not diff_response.ok:
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not fetch diff. GitHub returned status "
                f"{diff_response.status_code}."
            ),
        )

    diff = diff_response.text.strip()

    if not diff:
        raise HTTPException(
            status_code=422,
            detail="This pull request has no reviewable diff.",
        )

    truncated = len(diff) > MAX_DIFF_CHARS
    if truncated:
        diff = diff[:MAX_DIFF_CHARS]

    return {
        "owner": owner,
        "repository": repo,
        "pull_request_number": pr_number,
        "title": pr_data.get("title", ""),
        "state": pr_data.get("state", ""),
        "html_url": pr_data.get("html_url", pr_url),
        "changed_files": pr_data.get("changed_files", 0),
        "additions": pr_data.get("additions", 0),
        "deletions": pr_data.get("deletions", 0),
        "diff": diff,
        "diff_truncated": truncated,
        "diff_characters": len(diff),
    }


@router.post("/pull-request")
def create_pull_request(
    pr: schemas.PullRequestCreate,
    db: Session = Depends(get_db),
):
    return crud.create_pr(db, pr)


@router.post("/pull-request/review")
def review_github_pull_request(
    payload: dict,
    db: Session = Depends(get_db),
):
    pr_url = payload.get("url")

    if not isinstance(pr_url, str) or not pr_url.strip():
        raise HTTPException(
            status_code=400,
            detail="Provide a GitHub PR URL in the 'url' field.",
        )

    pr = fetch_github_pr(pr_url)

    # Label the diff with repository context for the agents.
    review_input = (
        f"GitHub Pull Request: {pr['html_url']}\n"
        f"Title: {pr['title']}\n"
        f"Changed files: {pr['changed_files']}\n\n"
        "Review the following pull request diff. Focus on changes "
        "introduced by this PR. Treat removed lines as context, "
        "not as newly introduced code. Identify affected files and "
        "line numbers where possible.\n\n"
        f"{pr['diff']}"
    )

    try:
        findings = coordinator.review_pull_request(review_input)
        verification = verifier.verify(findings)

        final_report = aggregator.aggregate(verification["findings"])

        saved_review = crud.create_review_report(
            db=db,
            code=review_input,
            report=final_report,
        )

        return {
            **{key: value for key, value in pr.items() if key != "diff"},
            "review_id": saved_review.id,
            "findings": findings,
            "verified_findings": verification["findings"],
            "agent_errors": verification["agent_errors"],
            "review_complete": verification["complete"],
            "verifier_status": verification["status"],
            "verifier_message": verification["status_message"],
            "verifier_checks": verification["checks_performed"],
            "validation_warnings": verification["validation_warnings"],
            "duplicate_findings": verification["duplicate_findings"],
            "final_report": final_report,
        }

    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"GitHub PR review failed: {str(exc)}",
        ) from exc
