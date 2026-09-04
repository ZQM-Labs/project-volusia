# COHERENT REALITY OF WORKERS IN THE ZQM-MESH
# ==================================================
# ZQM Labs internal governance reference
# Applies to Project Volusia and all ZQM-Mesh agentic contributions
#
# Version: 1.1
# Last updated: 2026-09-03
#
# Related documents:
#   - OPEN_INTELLIGENCE_DATA_DRIVEN_CHARTER.md (project charter)
#   - AGENTIC_CONTRIBUTION_STRATEGY.md (mesh architecture)
#   - PROJECT_VOLUSIA_GOV.md (CGB governance)
#   - GUIDING_PRINCIPLES_VOLUSIA_COUNTY.md (goals)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 1. WHAT "COHERENT REALITY" MEANS IN THIS CONTEXT
# ══════════════════════════════════════════════════════════════════════════

# In the ZQM-Mesh, "coherent reality" is the shared operational picture
# that all worker nodes, human reviewers, and community stakeholders can
# rely on when making decisions. It is built from:
#
#   - Verified data indicators (what the portal shows)
#   - Contribution records (what has been submitted and how it was handled)
#   - Governance decisions (what the CGB has decided and why)
#
# A coherent reality has three properties:
#   1. TRACEABLE — every number, submission, and decision can be traced
#      to its source, author, and review history.
#   2. NON-FLATENED — when multiple sources disagree, the disagreement
#      is visible rather than hidden behind a single "winner."
#   3. LIVE — the picture updates as data refreshes, submissions arrive,
#      and reviews complete. Stale information is marked as stale.

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2. THE MESH ARCHITECTURE (HOW WORKERS ARE DISTRIBUTED)
# ══════════════════════════════════════════════════════════════════════════

# From AGENTIC_CONTRIBUTION_STRATEGY.md and Q4_2026_EXECUTION_PLAN.md:
#
#   ZQM-Node-4 (zqm-garden-03)
#     Role: Public website host, serves https://volusia.zqmlabs.com
#     Services: portal_app.py (8789), contribution_api.py (8790)
#     Capability: serves content to external stakeholders
#
#   ZQM-Node-3 (zqm-node-3)
#     Role: Data pipeline execution, API key holder
#     Services: refresh_v2.py (periodic), fetcher modules
#     Capability: fetches Census, BLS, BEA, NOAA data
#
#   ZQM-Node-2 (zqm-node-2)
#     Role: Analysis and validation node
#     Capability: runs analytical models, validates contributions
#
#   ZQM-Node-1 (zqm-node-1)
#     Role: Map/GIS processing node
#     Capability: renders maps, processes spatial data
#
#   ZQM-Node-5 (zqm-node-5)
#     Role: Tool/test node
#     Capability: tests new tools, validates tool contributions
#
# The mesh distributes work because no single node has all capabilities.
# Contributions flow through the mesh according to which node has the
# relevant skills, not according to a centralized queue.

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3. COHERENCE GAPS IN THE CURRENT ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════

# Gap 1: Contribution routing vs. actual node capabilities
#
# The contribution API (contribution_api.py) routes submissions by TYPE
# to a named REVIEWER (e.g., "data_source" → "Data Steward").
# This assumes:
#   a) Every reviewer is available and can respond within SLA
#   b) The named reviewer is the correct node/person for that type
#   c) There is no fallback if the primary reviewer is unavailable
#
# In a mesh architecture, this is structurally fragile:
#   - If "Data Steward" is a human and goes on vacation, data_source
#     submissions pile up with no automatic retry
#   - If "GIS Lead" is a node and that node goes offline, map submissions
#     fail silently
#   - No workload balancing: one reviewer can get overwhelmed while
#     others are idle
#
# What coherence requires here:
#   - Routing should be to NODES with capabilities, not to NAMES
#   - Each contribution type should have PRIMARY and FALLBACK nodes
#   - If the primary is unavailable, the submission routes to fallback
#   - The status API should show which reviewer is assigned and whether
#     they are currently reachable

# Gap 2: Blind spots in contribution acceptance
#
# The contribution API accepts submissions from:
#   - Community web form (anonymous, no login)
#   - SMS gateway (phone number, no auth)
#   - Agentic contributors (API key optional)
#
# The acceptance logic checks:
#   - contribution_type is in VALID_CONTRIBUTION_TYPES
#   - content is non-empty
#   - idempotency_key is unique (if provided)
#
# What it does NOT check:
#   - Whether the content references an existing indicator or dataset
#   - Whether the content contradicts an already-verified indicator
#   - Whether the author is known (vs. anonymous)
#   - Whether the submission is within the scope of Project Volusia
#
# This is correct for anonymous community submissions — we want to accept
# broadly. But it means the coherence of accepted content is enforced only
# at review time, not at submission time. The coherence doc should make
# this explicit: acceptance ≠ endorsement.

# Gap 3: The population indicator discrepancy is real and visible
#
# Currently the portal stores:
#   - total_population_pep_2024 = 601,107 (Census PEP, July 2024)
#   - total_population_pep_2023 = 591,936 (Census PEP, July 2023)
#   - total_population_pep_2022 = 580,529 (Census PEP, July 2022)
#   - total_population_acs     = 568,229 (ACS 5-Year, 2023)
#   - population_bea           = 602,772 (BEA, 2024)
#
# The PEP series shows growth from 580K to 601K over 2 years — this is
# the official Census Bureau population estimate and should be the primary
# reference. The ACS figure (568K) is a survey-based estimate with a
# different methodology and wider margin of error. The BEA figure (603K)
# is an economic-geography estimate.
#
# The portal now surfaces this as a coherence disagreement (spread = 34,543
# persons across 5 indicators). This is correct behavior. The governance
# doc should explain WHY these differ so stakeholders don't treat them as
# errors.

# Gap 4: Contribution status is not surfaced on the portal
#
# The portal shows data indicators but does NOT show:
#   - How many contributions are pending review
#   - How many have been approved/rejected
#   - Whether the CGB reviewer queue is backlogged
#
# This is a coherence gap: stakeholders can see the data but not the
# process that produces it. The portal should eventually surface
# contribution statistics (count by status, average review time, etc.)
# from the contribution database.

# Gap 5: Version drift between documentation and running services
#
# As of 2026-09-03:
#   - BUILD_REPORT.md claims v2.0 "OPERATIONAL"
#   - portal_app.py reports v0.3.0
#   - contribution_api.py reports v1.0.0
#   - Documentation says "forward to ZQM-Node-4" but services run locally
#
# The version numbers should be reconciled. The running service version
# should match what the documentation claims.

# ══════════════════════════════════════════════════════════════════════════
# SECTION 4. CONTRIBUTION ROUTING — CURRENT STATE AND NEEDED CHANGES
# ══════════════════════════════════════════════════════════════════════════

# Current routing in contribution_api.py CONTRIBUTION_ROUTING dict:
#
#   data_source    → Data Steward
#   analysis       → Methodologist
#   tool           → Tool Owner
#   map            → GIS Lead
#   report         → Report Lead
#   community      → Community Liaison
#   social_media   → Community Liaison
#   educational    → Community Liaison
#   direct         → Community Liaison
#
# Problems:
#   1. Community-facing types (community, social_media, educational, direct)
#      all route to the same reviewer → single point of failure
#   2. No fallback reviewer defined
#   3. No consideration of which ZQM-Node has the capability
#   4. The reviewer names are roles, not node identifiers — they have no
#      connection to the actual mesh topology
#
# What coherence requires:
#   - Route to NODES with capabilities, not to ROLE NAMES
#   - Define PRIMARY and FALLBACK for each type
#   - For community-facing types, the reviewer must be a human with
#     explicit availability, not a role that may be inactive
#   - The status API should show: assigned reviewer, their status
#     (reachable/unreachable), and fallback if primary is down
#
# Proposed routing model (future):
#
#   data_source    → PRIMARY: Node-3 (data capability)
#                  → FALLBACK: Methodologist (human backup)
#   analysis       → PRIMARY: Node-2 (analysis capability)
#                  → FALLBACK: Methodologist (human backup)
#   tool           → PRIMARY: Node-5 (tool capability)
#                  → FALLBACK: Tool Owner (human backup)
#   map            → PRIMARY: Node-1 (gis capability)
#                  → FALLBACK: GIS Lead (human backup)
#   report         → PRIMARY: Report Lead (human)
#                  → FALLBACK: Community Liaison (human backup)
#   community      → PRIMARY: Community Liaison (human)
#                  → FALLBACK: Governance Chair (human backup)
#   social_media   → PRIMARY: Community Liaison (human)
#                  → FALLBACK: Governance Chair (human backup)
#   educational    → PRIMARY: Community Liaison (human)
#                  → FALLBACK: Governance Chair (human backup)
#   direct         → PRIMARY: Community Liaison (human)
#                  → FALLBACK: Governance Chair (human backup)
#
# This model:
#   - Distributes technical types across nodes (mesh-appropriate)
#   - Keeps community-facing types with humans (appropriate — these need
#     judgment that nodes don't have)
#   - Provides fallback for every type (no single point of failure)
#   - Clearly identifies which reviews require human judgment

# ══════════════════════════════════════════════════════════════════════════
# SECTION 5. WORKER NEEDS IN THE CURRENT SETUP
# ══════════════════════════════════════════════════════════════════════════

# What each worker needs to function coherently:

# ZQM-Node-3 (data pipeline)
#   - API keys for Census, BLS, BEA (currently configured)
#   - Network access to api.census.gov, api.bls.gov, apps.bea.gov,
#     ncei.noaa.gov (currently working)
#   - Write access to the shared database (volusia.db on zqm-garden-03)
#   - Schedule trigger (currently manual — needs cron/automation)
#   - Ability to detect when a fetch fails and retry

# ZQM-Node-4 (portal + contribution API)
#   - Read access to the shared database
#   - Network access to serve external requests (currently on localhost)
#   - The portal should eventually be exposed at https://volusia.zqmlabs.com
#   - Contribution API should eventually accept external submissions

# ZQM-Node-1 (GIS)
#   - Read access to spatial data in the database
#   - Capability to render maps for report contributions
#   - Currently not implemented — needs definition

# ZQM-Node-2 (analysis)
#   - Read access to indicators and datasets
#   - Capability to run analytical models on Volusia data
#   - Currently not implemented — needs definition

# ZQM-Node-5 (tool/test)
#   - Read access to tool contributions
#   - Capability to test tool contributions before approval
#   - Currently not implemented — needs definition

# Human reviewers (CGB members)
#   - Access to the contribution API to review submissions
#   - A way to see what's pending, what's decided, what's blocked
#   - Clear SLA expectations (5 business days from submission)
#   - Fallback assignment when primary reviewer is unavailable

# ══════════════════════════════════════════════════════════════════════════
# SECTION 6. WORKER RISKS IN THE CURRENT SETUP
# ══════════════════════════════════════════════════════════════════════════

# Risk 1: Single point of failure in community-facing routing
#
# The Community Liaison role handles 4 of 9 contribution types. If that
# person is unavailable (vacation, illness, departure), those submissions
# queue indefinitely with no automatic escalation. This is the most
# critical structural risk in the current architecture.

# Risk 2: Blind submission acceptance
#
# Anonymous submissions are accepted without content validation. This is
# correct for community access but means the coherence of accepted content
# depends entirely on the review process. If reviews are delayed, incoherent
# content sits in the queue unchallenged.

# Risk 3: Population indicator confusion
#
# Stakeholders who see 5 different population numbers (568K to 603K) without
# context will treat the discrepancy as an error rather than a multi-source
# reality. The portal's coherence panel helps but the governance doc must
# also explain the methodology differences.

# Risk 4: Manual-only refresh
#
# The data pipeline (refresh_v2.py) is currently run manually. This means:
#   - Data freshness depends on someone remembering to run it
#   - There's no automated retry if a fetch fails
#   - The "daily refresh by 06:00 UTC" SLA is not met
#   - The STATUS API says "manual — run refresh_v2.py" which signals to
#     stakeholders that the data may be stale

# Risk 5: API keys in source code
#
# The refresh_v2.py file contains hardcoded API keys as defaults:
#   - CENSUS_API_KEY = "***"  (line 44)
#   - BLS_API_KEY    = "***" (line 82)
#   - BEA_API_KEY    = "***" (line 114)
#
# If this repository is made public, these keys are exposed. The keys
# should come from environment variables only, with no defaults in source.

# Risk 6: Contribution database not backed up
#
# Submissions, decisions, and review history are stored in volusia.db
# alongside indicators. If the database is lost, contribution history
# is lost. The contribution system should have its own backup or export
# mechanism.

# Risk 7: Portal not externally accessible
#
# The portal runs on localhost:8789 on ZQM-Node-3. External stakeholders
# cannot access it. The plan says to "push to ZQM-Node-4" but that hasn't
# happened. Until the portal is externally accessible, the coherent reality
# it presents is only visible to people with direct access to the node.

# Risk 8: No contribution statistics on the portal
#
# Stakeholders see data indicators but not the contribution pipeline health.
# If submissions are piling up, the portal doesn't show it. This is a
# coherence gap: the "state of the project" is incomplete without pipeline
# metrics.

# ══════════════════════════════════════════════════════════════════════════
# SECTION 7. RECOMMENDED CHANGES (PRIORITIZED)
# ══════════════════════════════════════════════════════════════════════════

# Priority 1 (must fix before any public launch):
#   1. Remove hardcoded API keys from refresh_v2.py — use env vars only
#   2. Fix BLS series ID from LAUCN to LAUST (correct format for Volusia)
#   3. Rename fetch_pep or fix indicator naming to match actual source
#   4. Reconcile version numbers across docs and code
#   5. Create CONTRIBUTION_LOG.md for CGB decisions
#   6. Add a note to the portal explaining population discrepancy
#   7. Add fallback reviewers to CONTRIBUTION_ROUTING for all types
#   8. Add contribution statistics endpoint to the portal

# Priority 2 (should fix before scale-up):
#   9. Automate refresh pipeline (cron on ZQM-Node-3 or GitHub Actions)
#  10. Expose portal at https://volusia.zqmlabs.com
#  11. Define ZQM-Node-1, Node-2, Node-5 capabilities concretely
#  12. Create DATA_CATALOG.md and TOOLS_CATALOG.md (referenced by governance)
#  13. Add coherence group definitions to the config module (not hardcoded
#      in portal_app.py)
#  14. Add contribution status dashboard to the portal

# Priority 3 (nice to have):
#  15. Add content validation to contribution acceptance (optional, not
#      blocking for anonymous submissions)
#  16. Add contribution export/archival mechanism
#  17. Add per-contribution coherence check (does this submission contradict
#      an existing verified indicator?)
#  18. Add mesh node health dashboard (which nodes are online, what they
#      can do)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 8. HOW TO READ THIS DOCUMENT
# ══════════════════════════════════════════════════════════════════════════

# This document is part of the ZQM-Mesh coherence governance layer. It
# should be read alongside:
#
#   - OPEN_INTELLIGENCE_DATA_DRIVEN_CHARTER.md (why we exist)
#   - AGENTIC_CONTRIBUTION_STRATEGY.md (how the mesh works)
#   - PROJECT_VOLUSIA_GOV.md (who decides what)
#   - GUIDING_PRINCIPLES_VOLUSIA_COUNTY.md (what we're trying to achieve)
#
# When a new contributor joins the mesh, they should read this document
# to understand:
#   1. What "coherent reality" means in our context
#   2. Where the current architecture has gaps
#   3. What risks they should watch for when submitting or reviewing
#   4. What changes are needed before we can scale
#
# This document is itself a contribution. If it contains errors or
# omissions, submit a correction via the contribution API or open an
# issue on the project repository.
