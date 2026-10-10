from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from backend import crud
from backend import schemas

from backend.database import SessionLocal

router = APIRouter()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/pull-request")
def create_pull_request(pr: schemas.PullRequestCreate, db: Session = Depends(get_db)):

    return crud.create_pr(db, pr)
