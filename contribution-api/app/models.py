from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import enum

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ─── Enums ────────────────────────────────────────────────────────
class ContributorType(str, enum.Enum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"
    EDUCATIONAL_INSTITUTION = "educational_institution"
    AGENT = "agent"

class ContributorStanding(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class RateLimitTier(str, enum.Enum):
    PUBLIC_ANONYMOUS = "public_anonymous"
    PUBLIC_REGISTERED = "public_registered"
    TRUSTED_CONTRIBUTOR = "trusted_contributor"
    AGENT_VERIFIED = "agent_verified"
    CGB_MEMBER = "cgb_member"
    SYSTEM_INTERNAL = "system_internal"

class Pathway(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"
    AGENT_ITEM = "agent-item"

class SubmissionStatus(str, enum.Enum):
    QUEUED = "queued"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    RETURNED = "returned"
    REJECTED = "rejected"
    RESOLVED = "resolved"
    NOTED = "noted"

class ItemType(str, enum.Enum):
    MONITORING_EVENT = "monitoring_event"
    PROCESSING_RESULT = "processing_result"
    SYNTHESIS_DRAFT = "synthesis_draft"
    QUALITY_FLAG = "quality_flag"
    CROSS_REFERENCE = "cross_reference"
    SUBMISSION_ITEM = "submission_item"

class HumanOwner(str, enum.Enum):
    DATA_STEWARD = "Data Steward"
    METHODOLOGIST = "Methodologist"
    TOOL_OWNER = "Tool Owner"
    GIS_LEAD = "GIS Lead"
    REPORT_LEAD = "Report Lead"
    COMMUNITY_LIAISON = "Community Liaison"
    AGENT_OPERATIONS_LEAD = "Agent Operations Lead"

# ─── Models ───────────────────────────────────────────────────────
class Contributor(Base):
    __tablename__ = "contributors"

    id = Column(String, primary_key=True, index=True)
    contributor_type = Column(SQLEnum(ContributorType))
    contact_email = Column(String, unique=True, index=True)
    preferred_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # null for anonymous
    standing = Column(SQLEnum(ContributorStanding), default=ContributorStanding.PENDING)
    rate_limit_tier = Column(SQLEnum(RateLimitTier), default=RateLimitTier.PUBLIC_ANONYMOUS)
    api_key = Column(String, unique=True, index=True)
    api_key_expires_at = Column(DateTime, nullable=True)
    agree_to_terms = Column(Boolean, default=False)
    credit_option = Column(String, default="anonymous")  # credited | anonymous | school_only | not_credited
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=True)

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, index=True)
    pathway = Column(SQLEnum(Pathway))
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.QUEUED)
    contributor_id = Column(String, ForeignKey("contributors.id"), nullable=True)
    contributor_display = Column(String, nullable=True)
    contact_preference = Column(String, default="no_follow_up")  # email | phone | no_follow_up
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    channel_used = Column(String, default="web_form")  # web_form | email | sms | phone | library | meeting_card | social_media | api | other
    idempotency_key = Column(String, unique=True, nullable=True)

    # Content (JSON stored as text)
    content = Column(Text)

    # Review
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)
    decision = Column(String, nullable=True)  # accepted | returned | rejected | resolved | noted
    decision_details = Column(Text, nullable=True)
    reviewer = Column(String, nullable=True)
    publication_note = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    estimated_review_by = Column(DateTime, nullable=True)

class AgentItem(Base):
    __tablename__ = "agent_items"

    id = Column(String, primary_key=True, index=True)
    submission_id = Column(String, ForeignKey("submissions.id"))
    itemtype = Column(SQLEnum(ItemType))
    agent_id = Column(String, index=True)
    agent_version = Column(String)
    source = Column(String)
    confidence = Column(Float)
    content = Column(Text)  # JSON
    flags = Column(Text)  # comma-separated
    next_action = Column(String)
    human_owner = Column(SQLEnum(HumanOwner))
    created_at = Column(DateTime, default=datetime.utcnow)

class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String, index=True)
    contributor_id = Column(String, nullable=True)
    method = Column(String)
    path = Column(String)
    status_code = Column(Integer)
    duration_ms = Column(Float)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ─── Database initialization ─────────────────────────────────────
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
