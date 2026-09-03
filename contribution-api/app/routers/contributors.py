from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import Contributor
from app.routers.auth import get_current_contributor

router = APIRouter()

class ContributorRecord(BaseModel):
    contributor_id: str
    standing: str
    pathways_used: list
    total_submissions: int
    accepted: int
    returned: int
    rejected: int
    acceptance_rate: float
    median_time_to_review_days: float
    quality_score_avg: float
    repeatability: str
    credit_option: str
    last_activity: Optional[str]
    since: str

@router.get("/contributors/me/record", response_model=ContributorRecord)
async def get_contributor_record(
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    return ContributorRecord(
        contributor_id=contributor.id,
        standing=contributor.standing.value,
        pathways_used=["F", "I"],
        total_submissions=0,
        accepted=0,
        returned=0,
        rejected=0,
        acceptance_rate=0.0,
        median_time_to_review_days=0.0,
        quality_score_avg=0.0,
        repeatability="infrequent",
        credit_option=contributor.credit_option,
        last_activity=contributor.last_activity_at.isoformat() if contributor.last_activity_at else None,
        since=contributor.created_at.isoformat(),
    )
