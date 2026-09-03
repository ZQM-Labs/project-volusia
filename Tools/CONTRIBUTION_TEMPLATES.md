# CONTRIBUTION TEMPLATES — PROJECT VOLUSIA
# Appendix to AGENTIC_CONTRIBUTION_STRATEGY.md
# Date: 2026-09-03 | Version: 1.0

---

## APPENDIX A: DATA SOURCE CONTRIBUTION (SUBMIT_DATA_SOURCE.md)

```
SUBMIT_DATA_SOURCE.md
=====================

Source Name:           [e.g., "Volusia County Property Appraiser — Parcel Data"]
Agency/Organization:   [e.g., "Volusia County Property Appraiser's Office"]
URL / Access Method:   [e.g., "https://vcpa.vcgov.org/download"]
Data Type:             [demographics / employment / real_estate / tourism / other]
Geographic Coverage:   [county / tract / zip / city / state / national]
Update Frequency:      [monthly / quarterly / annual / weekly / daily / unknown]
License / Terms:       [public_domain / CC-BY / commercial / unknown]
Known Limitations:     [e.g., "Access database format requires conversion"]
Why this matters:      [1-2 sentences on decision this informs]
Contributor:           [name / email]
Date Submitted:        [YYYY-MM-DD]

VALIDATION CHECKLIST (completed by CGB):
[ ] Source exists and is accessible
[ ] Data Steward verifies source and quality score
[ ] GIS Lead reviews if tract/zip level
[ ] Added to PUBLIC_DATA_SOURCE_RECON.md
[ ] Added to DATA_CATALOG.md
```

---

## APPENDIX B: ANALYSIS CONTRIBUTION (ANALYSIS_SUBMISSION.md)

```
ANALYSIS_SUBMISSION.md
======================

Research Question:     [What decision does this inform?]
Data Sources Used:     [cite PUBLIC_DATA_SOURCE_RECON entries by ID]
Methodology:           [cite METHODOLOGY.md section, or propose new method]
Results:               [with uncertainty bounds]
Limitations:           [honestly stated]
Reproducibility:       [code repo / environment / data location]
Conflict of Interest:  [disclosure]
Contributor:           [name / email]
Date Submitted:        [YYYY-MM-DD]

VALIDATION CHECKLIST:
[ ] Methodologist reviews methodology
[ ] Data Steward verifies sources
[ ] Results have stated uncertainty
[ ] COI disclosed
[ ] CGB majority vote if touching material indicator
```

---

## APPENDIX C: TOOL CONTRIBUTION (TOOL_SUBMISSION.md)

```
TOOL_SUBMISSION.md
==================

Tool Name:             [e.g., "Census ACS Fetcher"]
Category:              [Data Collection / Processing / Analysis / Visualization / Infrastructure]
Purpose:               [what task, why not existing tool]
Language/Deps:         [Python 3.11, requests, pandas]
Usage Example:         [copy-pasteable]
Test Status:           [passed / pending]
License:               [MIT / Apache 2.0 / BSD / other OSS]
Access:                [repo URL, install instructions]
Maintainer:            [contact]
Known Limitations:     [e.g., "Requires Census API key"]

VALIDATION CHECKLIST:
[ ] Tool Owner verifies it runs as described
[ ] CGB reviews if external-facing
[ ] Security review if handling credentials
[ ] Documentation complete
[ ] Added to TOOLS_CATALOG.md
```

---

## APPENDIX D: MAP LAYER CONTRIBUTION (MAP_SUBMISSION.md)

```
MAP_SUBMISSION.md
=================

Layer Name:            [e.g., "Median Income by Census Tract"]
Category:              [boundary / economic / infrastructure / environment / demographic / historic]
Geographic Scope:       [county / city / tract / zip]
Data Source:           [cite PUBLIC_DATA_SOURCE_RECON entry]
Projection / Format:   [EPSG:4269, GeoJSON]
Vintage:               [last updated date]
Refresh Frequency:      [expected]
Intended Use:          [what analysis or report]
Known Accuracy:        [limitations]
Source Citation:       [for the map itself]
Contributor:           [name / email]
Date Submitted:        [YYYY-MM-DD]

VALIDATION CHECKLIST:
[ ] GIS Lead reviews projection and format
[ ] Data Steward verifies underlying source
[ ] Privacy review if public release
[ ] Added to MAP_CATALOG.md
```

---

## APPENDIX E: COMMUNITY INPUT (COMMUNITY_INPUT.md)

```
COMMUNITY_INPUT.md
==================

What I observed/knew:  [the substance of the contribution]
Where and when:        [geographic + temporal context]
Basis for accuracy:    [saw it / verified / documentation / experience]
What decision/report:  [what this might affect]
Contributor:           [name / email / phone / anonymous]
Channel:               [web_form / email / sms / phone / library / meeting / social_media]
Date Submitted:        [YYYY-MM-DD]

SPECIAL HANDLING:
- Community knowledge is Tier 4 evidence (illustrative only)
- Can trigger investigation, provide context, generate hypothesis
- Cannot change an indicator value on its own
- No personally identifiable information in summaries

VALIDATION CHECKLIST:
[ ] Community Liaison logs and acknowledges (within 5 business days)
[ ] If affects report/indicator, CGB member reviews
[ ] Where possible, cross-checked against other sources
- [ ] Re-contact for clarification
- [ ] Add to priority list
- [ ] Escalate to [lead]
- [ ] No follow-up needed
```

---

## APPENDIX F: EDUCATIONAL INSTITUTION SUBMISSION (SCHOOL_PROJECT_SUBMISSION.md)

```
SCHOOL_PROJECT_SUBMISSION.md
=============================

Institution:           [e.g., "Volusia County Schools / Daytona State College"]
Teacher/Faculty:       [sponsor name]
Course/Project:        [class or project name]
Level:                 [K-12 / undergraduate / graduate]
Students Involved:     [count range]
Project Description:    [what students did, data they collected/analyzed]
Output:                [analysis / dataset / map / tool / report / observation]
Privacy Preference:    [full_credit / first_name_only / anonymous / school_only]
Shared Back:           [will students share data back to Project Volusia?]
Contributor:           [teacher/faculty name, email]
Date Submitted:        [YYYY-MM-DD]
```

---

Document owner: Project Volusia CGB
Related: AGENTIC_CONTRIBUTION_STRATEGY.md
Next review: 2026-12-02
