#!/usr/bin/env python3
"""
Project Volusia — Citation Validation Layer
Validates source citations, URLs, and attribution quality for all indicators.
"""

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DB_PATH = Path(__file__).resolve().parent.parent.parent / "volusia_data" / "volusia.db"

# Known authoritative source domains
AUTHORITATIVE_SOURCES = {
    "gov": 10,           # Government sources (highest trust)
    "edu": 9,            # Educational institutions
    "int": 9,            # International organizations
    "org": 7,            # Non-profits (variable trust)
    "com": 5,            # Commercial (lower trust)
    "net": 5,            # Network sources
}

# Known high-trust domains
HIGH_TRUST_DOMAINS = {
    "census.gov", "bls.gov", "bea.gov", "noaa.gov", "ncei.noaa.gov",
    "epa.gov", "fcc.gov", "fda.gov", "cdc.nih.gov", "nih.gov",
    "usgs.gov", "fs.usda.gov", "fema.gov", "loc.gov",
    "volusia.org", "vcgov.org", "vcsedu.org",
    "fldoe.org", "floridahealth.gov", "fdle.state.fl.us",
}

# Known low-trust domains
LOW_TRUST_DOMAINS = {
    "spotcrime.com", "crimebycounty.com", "floridasfastestinternet.com",
    "floridastateauthority.com",
}


def validate_url_format(url: str) -> tuple:
    """Validate URL format and return (is_valid, score, issues)."""
    issues = []
    score = 100
    
    if not url:
        return False, 0, ["URL is empty"]
    
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, 0, [f"URL parse error: {e}"]
    
    # Check scheme
    if parsed.scheme not in ("http", "https"):
        issues.append(f"Non-HTTP scheme: {parsed.scheme}")
        score -= 20
    
    # Check netloc
    if not parsed.netloc:
        issues.append("Missing domain")
        score -= 30
    else:
        # Check for known high-trust domains
        domain = parsed.netloc.lower().replace("www.", "")
        if domain in HIGH_TRUST_DOMAINS:
            score += 10
        elif domain in LOW_TRUST_DOMAINS:
            issues.append(f"Low-trust domain: {domain}")
            score -= 20
        
        # Check for government/edu domains
        if domain.endswith((".gov", ".edu", ".int")):
            score += 5
    
    # Check path (should have actual path, not just root)
    if parsed.path in ("", "/"):
        issues.append("Root URL only (no specific page)")
        score -= 10
    
    # Check for query parameters (often good for API calls)
    if parsed.query:
        score += 5
    
    # Check for fragment
    if parsed.fragment:
        score += 2
    
    return len(issues) == 0 or score > 50, max(0, score), issues


def validate_citation_completeness(row: dict) -> tuple:
    """Validate citation completeness and return (score, issues)."""
    issues = []
    score = 100
    
    # Source name
    source = row.get("source", "")
    if not source or source.strip() == "":
        issues.append("Missing source name")
        score -= 30
    elif len(source) < 3:
        issues.append(f"Source name too short: '{source}'")
        score -= 10
    
    # Source URL
    url = row.get("source_url", "")
    if not url or url.strip() == "":
        issues.append("Missing source URL")
        score -= 30
    else:
        url_valid, url_score, url_issues = validate_url_format(url)
        score -= (100 - url_score)
        issues.extend(url_issues)
    
    # Vintage
    vintage = row.get("vintage", "")
    if not vintage or vintage.strip() == "":
        issues.append("Missing vintage/date")
        score -= 15
    else:
        # Check if vintage is a valid year or date range
        if re.match(r'^\d{4}$', vintage):  # Single year
            year = int(vintage)
            current_year = datetime.now().year
            if year < 2000 or year > current_year + 1:
                issues.append(f"Suspicious vintage year: {vintage}")
                score -= 10
            elif year == current_year or year == current_year - 1:
                score += 5  # Recent data bonus
        elif re.match(r'^\d{4}-\d{4}$', vintage):  # Year range
            years = vintage.split('-')
            if int(years[0]) >= int(years[1]):
                issues.append(f"Invalid year range: {vintage}")
                score -= 5
        else:
            # Other formats (quarters, etc.) - acceptable
            pass
    
    # Description
    description = row.get("description", "")
    if not description or description.strip() == "":
        issues.append("Missing description")
        score -= 10
    elif len(description) < 10:
        issues.append(f"Description too short: '{description[:20]}...'")
        score -= 5
    
    # Fetch timestamp
    fetched = row.get("fetched_at", "")
    if not fetched or fetched.strip() == "":
        issues.append("Missing fetch timestamp")
        score -= 10
    
    return max(0, score), issues


def validate_attribution_quality(row: dict) -> tuple:
    """Validate attribution quality and return (score, issues)."""
    issues = []
    score = 100
    
    source = row.get("source", "").strip()
    description = row.get("description", "").strip()
    
    # Check if source is just a URL (bad practice)
    if source.startswith(("http://", "https://")):
        issues.append("Source field contains URL instead of name")
        score -= 15
    
    # Check if source is generic
    generic_sources = ["Various", "Third Party", "Unknown", "N/A", "TBD"]
    if source in generic_sources:
        issues.append(f"Generic source name: '{source}'")
        score -= 10
    
    # Check if description is actually a timestamp
    if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', description):
        issues.append("Description contains timestamp instead of text")
        score -= 20
    
    # Check if description is informative
    if description and len(description) > 50:
        score += 5  # Bonus for detailed description
    
    # Check for proper capitalization in source
    if source and not source[0].isupper() and not source.startswith(("U.S.", "FL")):
        # Allow lowercase for domains
        if "." not in source:
            issues.append(f"Source not capitalized: '{source}'")
            score -= 5
    
    return max(0, score), issues


def validate_cross_reference(row: dict, all_rows: list) -> tuple:
    """Validate cross-referencing and return (score, issues)."""
    issues = []
    score = 100
    
    name = row.get("name", "")
    source = row.get("source", "")
    url = row.get("source_url", "")
    
    # Check for indicators sharing the same URL with different sources
    if url:
        same_url_rows = [r for r in all_rows if r.get("source_url") == url and r.get("name") != name]
        if len(same_url_rows) > 5:
            issues.append(f"URL shared with {len(same_url_rows)} other indicators (consider more specific URLs)")
            score -= 10
    
    # Check for indicators from same source with inconsistent formatting
    same_source_rows = [r for r in all_rows if r.get("source") == source]
    if len(same_source_rows) > 1:
        # Check if all have URLs
        has_urls = sum(1 for r in same_source_rows if r.get("source_url"))
        if has_urls != len(same_source_rows) and has_urls != 0:
            issues.append(f"Inconsistent URL coverage for source '{source}' ({has_urls}/{len(same_source_rows)})")
            score -= 5
    
    return max(0, score), issues


def generate_citation_report():
    """Generate comprehensive citation validation report."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute("SELECT * FROM indicators ORDER BY category, name").fetchall()
    all_rows = [dict(r) for r in rows]
    
    citation_results = []
    url_results = []
    attribution_results = []
    crossref_results = []
    
    overall_scores = []
    
    for row in rows:
        row_dict = dict(row)
        name = row_dict.get("name", "")
        
        # Citation completeness
        comp_score, comp_issues = validate_citation_completeness(row_dict)
        
        # Attribution quality
        attr_score, attr_issues = validate_attribution_quality(row_dict)
        
        # URL format
        url = row_dict.get("source_url", "")
        url_valid, url_score, url_issues = validate_url_format(url) if url else (False, 0, ["No URL"])
        
        # Cross-reference
        xref_score, xref_issues = validate_cross_reference(row_dict, all_rows)
        
        # Overall score
        overall = (comp_score * 0.4 + attr_score * 0.3 + url_score * 0.2 + xref_score * 0.1)
        overall_scores.append(overall)
        
        # Determine status
        if overall >= 90:
            status = "OK"
        elif overall >= 70:
            status = "WARN"
        elif overall >= 50:
            status = "REVIEW"
        else:
            status = "FAIL"
        
        all_issues = comp_issues + attr_issues + url_issues + xref_issues
        
        citation_results.append({
            "indicator": name,
            "category": row_dict.get("category", ""),
            "source": row_dict.get("source", ""),
            "url": row_dict.get("source_url", ""),
            "vintage": row_dict.get("vintage", ""),
            "completeness_score": comp_score,
            "attribution_score": attr_score,
            "url_score": url_score,
            "crossref_score": xref_score,
            "overall_score": round(overall, 1),
            "status": status,
            "issues": all_issues,
        })
    
    # Summary statistics
    total = len(citation_results)
    ok_count = len([c for c in citation_results if c["status"] == "OK"])
    warn_count = len([c for c in citation_results if c["status"] == "WARN"])
    review_count = len([c for c in citation_results if c["status"] == "REVIEW"])
    fail_count = len([c for c in citation_results if c["status"] == "FAIL"])
    avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
    
    # Worst performers
    worst = sorted(citation_results, key=lambda x: x["overall_score"])[:10]
    
    report = {
        "overall": "OK" if fail_count == 0 and review_count < total * 0.1 else "REVIEW",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": total,
            "ok": ok_count,
            "warn": warn_count,
            "review": review_count,
            "fail": fail_count,
            "average_score": round(avg_score, 1),
        },
        "citations": citation_results,
        "worst_performers": worst,
    }
    
    conn.close()
    return report


if __name__ == "__main__":
    report = generate_citation_report()
    print(json.dumps(report, indent=2))
