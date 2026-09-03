from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Contributor
from app.routers.auth import get_current_contributor

router = APIRouter()

# ─── Schemas ─────────────────────────────────────────────────────
class DataSourceSummary(BaseModel):
    source_id: str
    source_name: str
    agency: str
    data_type: str
    integration_status: str

class DataSource(DataSourceSummary):
    access_method: str
    update_frequency: str
    geographic_granularity: str
    license: str
    volusia_notes: Optional[str] = None

class TableSummary(BaseModel):
    table_id: str
    table_name: str
    domain: str
    source: str

class Table(TableSummary):
    vintage: str
    update_frequency: str
    geographic_resolution: str
    key_fields: List[str]
    join_keys: List[str]
    usage_notes: Optional[str] = None

class TableSamples(BaseModel):
    table_id: str
    sample_size: int
    columns: List[str]
    rows: List[dict]

class ReportSummary(BaseModel):
    report_id: str
    report_type: str
    title: str
    status: str

class Report(ReportSummary):
    published_at: Optional[str] = None
    sections: List[dict] = []

class ToolSummary(BaseModel):
    tool_id: str
    tool_name: str
    category: str
    status: str

class DataMetadataIndex(BaseModel):
    total_tables: int
    total_sources: int
    domains: List[str]
    last_updated: str

class ContributorRecord(BaseModel):
    contributor_id: str
    standing: str
    pathways_used: List[str]
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

# ─── Mock data (in production, load from DATA_CATALOG.md, etc.) ───
DATA_SOURCES = [
    DataSourceSummary(
        source_id="acs_2023_5yr",
        source_name="American Community Survey 5-Year Estimates",
        agency="US Census Bureau",
        data_type="demographics",
        integration_status="live",
    ),
    DataSourceSummary(
        source_id="bls_laus",
        source_name="Local Area Unemployment Statistics",
        agency="Bureau of Labor Statistics",
        data_type="employment",
        integration_status="live",
    ),
    DataSourceSummary(
        source_id="bea_gdp",
        source_name="Regional GDP",
        agency="Bureau of Economic Analysis",
        data_type="economy",
        integration_status="in_progress",
    ),
]

TABLES = [
    TableSummary(
        table_id="b19013",
        table_name="Median Household Income",
        domain="demographics",
        source="ACS 5-Year",
    ),
    TableSummary(
        table_id="b17001",
        table_name="Poverty Status",
        domain="demographics",
        source="ACS 5-Year",
    ),
]

REPORTS = [
    ReportSummary(
        report_id="reb_q3_2026",
        report_type="quarterly_economic_briefing",
        title="Q3 2026 Quarterly Economic Briefing",
        status="published",
    ),
]

TOOLS = [
    ToolSummary(
        tool_id="census_api_wrapper",
        tool_name="Census API Wrapper",
        category="data_collection",
        status="live",
    ),
]

# ─── Endpoints ───────────────────────────────────────────────────
@router.get("/data/sources")
async def list_data_sources(
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    return {"data": [s.model_dump() for s in DATA_SOURCES], "pagination": {"page": 1, "per_page": 20, "total": len(DATA_SOURCES), "total_pages": 1}}

@router.get("/data/sources/{source_id}")
async def get_data_source(
    source_id: str,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    for s in DATA_SOURCES:
        if s.source_id == source_id:
            return s.model_dump()
    raise HTTPException(status_code=404, detail="Data source not found")

@router.get("/data/tables")
async def list_tables(
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    return {"data": [t.model_dump() for t in TABLES], "pagination": {"page": 1, "per_page": 20, "total": len(TABLES), "total_pages": 1}}

@router.get("/data/tables/{table_id}")
async def get_table(
    table_id: str,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    for t in TABLES:
        if t.table_id == table_id:
            return t.model_dump()
    raise HTTPException(status_code=404, detail="Table not found")

@router.get("/data/tables/{table_id}/samples")
async def get_table_samples(
    table_id: str,
    size: int = 100,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    return TableSamples(
        table_id=table_id,
        sample_size=min(size, 1000),
        columns=["fips", "geoid", "value", "moe"],
        rows=[{"fips": "12001", "geoid": "12001000100", "value": 55000, "moe": 2500}],
    )

@router.get("/data/metadata")
async def get_data_metadata(
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    return DataMetadataIndex(
        total_tables=len(TABLES),
        total_sources=len(DATA_SOURCES),
        domains=["demographics", "economy", "employment", "tourism", "infrastructure", "environment"],
        last_updated="2026-09-03T00:00:00Z",
    )

@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    for r in REPORTS:
        if r.report_id == report_id:
            return r.model_dump()
    raise HTTPException(status_code=404, detail="Report not found")

@router.get("/reports/upcoming")
async def get_upcoming_reports(
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    return {"data": [r.model_dump() for r in REPORTS], "pagination": {"page": 1, "per_page": 20, "total": len(REPORTS), "total_pages": 1}}

@router.get("/tools")
async def list_tools(
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    return {"data": [t.model_dump() for t in TOOLS], "pagination": {"page": 1, "per_page": 20, "total": len(TOOLS), "total_pages": 1}}

# ─── Contributor record endpoint ─────────────────────────────────
@router.get("/contributors/me/record", response_model=ContributorRecord)
async def get_contributor_record(
    contributor: Contributor = Depends(get_current_contributor),
    db: Session = Depends(get_db),
):
    # In production, compute from actual submission data
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
