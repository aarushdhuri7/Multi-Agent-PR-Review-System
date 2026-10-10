from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PullRequestCreate(BaseModel):
    pr_number: int
    repository: str
    title: str
    author: str


class PullRequestResponse(PullRequestCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ReviewRequest(BaseModel):
    code: str


class ReviewReportResponse(BaseModel):
    id: int
    code: str
    report: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
