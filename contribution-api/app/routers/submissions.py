from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json
import uuid

from app.database import get_db
from app.models import (
    Contributor, Submission, AgentItem, APILog,
    Pathway, SubmissionStatus, ItemType, HumanOwner,
    RateLimitTier
)
from app.routers.auth import get_current_contributor

router = APIRouter()

# ─── Schemas ─────────────────────────────────────────────────────
class PathwayFSubmission(BaseModel):
    what_i_know: str = Field(..., max_length=5000)
    where: Optional[str] = None
    when: Optional[str] = None
    why_believe_accurate: str = Field(..., max_length=2000)
    what_decision_or_report: Optional[str] = None
    channel_used: str = "web_form"
    contributor_display: Optional[str] = Field(None, max_length=100)
    contact_preference: str = "no_follow_up"
    contact_email: Optional[str] = None
    idempotency_key: Optional[str] = Field(None, max_length=100)

class PathwayISubmission(BaseModel):
    what_to_contribute: str = Field(..., max_length=5000)
    basis: str = Field(..., max_length=2000)
    what_decision_or_report: Optional[str] = None
    anything_else: Optional[str] = Field(None, max_length=2000)
    contact_preference: str = "no_follow_up"
    contact_email: Optional[str] = None
    idempotency_key: Optional[str] = Field(None, max_length=100)

class AgentItemSubmission(BaseModel):
    itemtype: ItemType
    agent_id: str
    agent_version: str
    timestamp: datetime
    source: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    content: Dict[str, Any]
    flags: List[str]
    next_action: str
    human_owner: HumanOwner
    idempotency_key: Optional[str] = None

class SubmissionResponse(BaseModel):
    submission_id: str
    pathway: str
    status: str
    submitted_at: datetime
    acknowledged_at: Optional[datetime] = None
    estimated_review_by: Optional[datetime] = None
    message: str
    idempotency_key: Optional[str] = None

class AgentItemResponse(BaseModel):
    submission_id: str
    status: str
    routed_to: str
    estimated_review_by: Optional[datetime] = None
    message: str
    idempotency_key: Optional[str] = None

class SubmissionStatusResponse(BaseModel):
    submission_id: str
    pathway: str
    status: str
    submitted_at: datetime
    acknowledged_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    decision: Optional[str] = None
    decision_details: Optional[str] = None
    reviewer: Optional[str] = None
    contributor_display: Optional[str] = None
    credit_option: Optional[str] = None
    publication_note: Optional[str] = None
    next_steps: Optional[str] = None

class SubmissionSummary(BaseModel):
    submission_id: str
    pathway: str
    status: str
    submitted_at: datetime
    decision: Optional[str] = None

class SubmissionList(BaseModel):
    data: List[SubmissionSummary]
    pagination: Dict[str, int]

class Pagination(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int

# ─── Helpers ─────────────────────────────────────────────────────
def generate_submission_id(pathway: str) -> str:
    return f"sub_{pathway.lower()}_{uuid.uuid4().hex[:10]}"

def check_idempotency(db: Session, key: str) -> Optional[Submission]:
    if not key:
        return None
    return db.query(Submission).filter(Submission.idempotency_key == key).first()

# ─── Endpoints ───────────────────────────────────────────────────
@router.post("/submissions/F", response_model=SubmissionResponse, status_code=201)
async def submit_pathway_f(
    req: PathwayFSubmission,
    request: Request,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    # Check idempotency
    existing = check_idempotency(db, req.idempotency_key)
    if existing:
        return SubmissionResponse(
            submission_id=existing.id,
            pathway=existing.pathway.value,
            status=existing.status.value,
            submitted_at=existing.submitted_at,
            acknowledged_at=existing.acknowledged_at,
            estimated_review_by=existing.estimated_review_by,
            message="Submission already received.",
            idempotency_key=req.idempotency_key,
        )

    submission_id = generate_submission_id("F")
    submission = Submission(
        id=submission_id,
        pathway=Pathway.F,
        status=SubmissionStatus.QUEUED,
        contributor_id=contributor.id,
        contributor_display=req.contributor_display or contributor.preferred_name,
        contact_preference=req.contact_preference,
        contact_email=req.contact_email or contributor.contact_email,
        channel_used=req.channel_used,
        idempotency_key=req.idempotency_key,
        content=json.dumps(req.model_dump()),
        estimated_review_by=datetime.utcnow() + timedelta(days=5),
    )
    db.add(submission)
    db.commit()

    return SubmissionResponse(
        submission_id=submission_id,
        pathway="F",
        status="queued",
        submitted_at=submission.submitted_at,
        estimated_review_by=submission.estimated_review_by,
        message="Submission received. You will receive an update within 5 business days.",
        idempotency_key=req.idempotency_key,
    )

@router.post("/submissions/I", response_model=SubmissionResponse, status_code=201)
async def submit_pathway_i(
    req: PathwayISubmission,
    request: Request,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    # Check idempotency
    existing = check_idempotency(db, req.idempotency_key)
    if existing:
        return SubmissionResponse(
            submission_id=existing.id,
            pathway=existing.pathway.value,
            status=existing.status.value,
            submitted_at=existing.submitted_at,
            acknowledged_at=existing.acknowledged_at,
            estimated_review_by=existing.estimated_review_by,
            message="Submission already received.",
            idempotency_key=req.idempotency_key,
        )

    submission_id = generate_submission_id("I")
    submission = Submission(
        id=submission_id,
        pathway=Pathway.I,
        status=SubmissionStatus.QUEUED,
        contributor_id=contributor.id,
        contributor_display=contributor.preferred_name,
        contact_preference=req.contact_preference,
        contact_email=req.contact_email or contributor.contact_email,
        channel_used="web_form",
        idempotency_key=req.idempotency_key,
        content=json.dumps(req.model_dump()),
        estimated_review_by=datetime.utcnow() + timedelta(days=5),
    )
    db.add(submission)
    db.commit()

    return SubmissionResponse(
        submission_id=submission_id,
        pathway="I",
        status="queued",
        submitted_at=submission.submitted_at,
        estimated_review_by=submission.estimated_review_by,
        message="Submission received. You will receive an update within 5 business days.",
        idempotency_key=req.idempotency_key,
    )

@router.post("/submissions/agent-item", response_model=AgentItemResponse, status_code=202)
async def submit_agent_item(
    req: AgentItemSubmission,
    request: Request,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    # Verify agent is registered (simplified — in production, check agent_records)
    # For now, accept any agent_id from a verified contributor

    # Check idempotency
    existing = check_idempotency(db, req.idempotency_key)
    if existing:
        return AgentItemResponse(
            submission_id=existing.id,
            status="queued",
            routed_to=req.human_owner.value,
            estimated_review_by=existing.estimated_review_by,
            message="Agent ITEM already received.",
            idempotency_key=req.idempotency_key,
        )

    submission_id = generate_submission_id("agent")

    # Create submission
    submission = Submission(
        id=submission_id,
        pathway=Pathway.AGENT_ITEM,
        status=SubmissionStatus.QUEUED,
        contributor_id=contributor.id,
        channel_used="api",
        idempotency_key=req.idempotency_key,
        content=json.dumps(req.model_dump()),
        estimated_review_by=datetime.utcnow() + timedelta(days=2),
    )
    db.add(submission)

    # Create agent item
    agent_item = AgentItem(
        id=f"ai_{uuid.uuid4().hex[:10]}",
        submission_id=submission_id,
        itemtype=req.itemtype,
        agent_id=req.agent_id,
        agent_version=req.agent_version,
        source=req.source,
        confidence=req.confidence,
        content=json.dumps(req.content),
        flags=",".join(req.flags),
        next_action=req.next_action,
        human_owner=req.human_owner,
    )
    db.add(agent_item)
    db.commit()

    return AgentItemResponse(
        submission_id=submission_id,
        status="queued",
        routed_to=req.human_owner.value,
        estimated_review_by=submission.estimated_review_by,
        message=f"Agent ITEM received and routed to {req.human_owner.value} queue.",
        idempotency_key=req.idempotency_key,
    )

@router.get("/submissions/{submission_id}", response_model=SubmissionStatusResponse)
async def get_submission(
    submission_id: str,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return SubmissionStatusResponse(
        submission_id=submission.id,
        pathway=submission.pathway.value,
        status=submission.status.value,
        submitted_at=submission.submitted_at,
        acknowledged_at=submission.acknowledged_at,
        reviewed_at=submission.reviewed_at,
        decision=submission.decision,
        decision_details=submission.decision_details,
        reviewer=submission.reviewer,
        contributor_display=submission.contributor_display,
        credit_option=None,  # derived from contributor record
        publication_note=submission.publication_note,
        next_steps=submission.next_steps,
    )

@router.get("/submissions", response_model=SubmissionList)
async def list_submissions(
    page: int = 1,
    per_page: int = 20,
    status_filter: Optional[str] = None,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    query = db.query(Submission).filter(Submission.contributor_id == contributor.id)

    if status_filter:
        query = query.filter(Submission.status == status_filter)

    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    submissions = query.order_by(Submission.submitted_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return SubmissionList(
        data=[
            SubmissionSummary(
                submission_id=s.id,
                pathway=s.pathway.value,
                status=s.status.value,
                submitted_at=s.submitted_at,
                decision=s.decision,
            )
            for s in submissions
        ],
        pagination={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )
