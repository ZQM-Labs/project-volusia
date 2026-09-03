Q4 2026 EXECUTION PLAN — PROJECT VOLUSIA
=========================================
Phase 1 Foundation — First Quarter Delivery Plan
ZQM Labs

Version: 1.0
Date: 2026-09-02
Author: Alex Zelenski
Classification: Internal Strategic Document

---

0. PURPOSE

This is the operational companion to STRATEGIC_FOCUS_Q4_2026_2027.md.

It takes Phase 1 Foundation from the roadmap and turns it into a
concrete Q4 2026 delivery plan. Six roadmap items. Five working weeks
from planning through end-of-quarter. No vapor.

Q4 2026 calendar anchor: October through December. End-of-quarter
review target: December 2, 2026 (aligned with existing charter review
cadence).

---

1. PHASE 1 FOUNDATION — ROADMAP ITEMS

From TIMELINE_AND_ROADMAP.md, Phase 1 (2026 Q4 - 2027 Q2):

   - Establish Project Volusia team and governance
   - Audit existing open data assets and gaps
   - Launch baseline data portal with key economic indicators
   - Begin stakeholder interviews across all four groups
   - Publish commerce reliability standards
   - Open-source first internal tools

This plan covers all six in Q4.

---

2. Q4 DELIVERY PLAN — BY ITEMS

2.1 ITEM 1: TEAM AND GOVERNANCE

Current state: Documents exist, team does not yet exist as an
operational unit.

Q4 deliverable: A functioning Project Volusia team structure with
named roles, decision authority, and a governance cadence.

Sub-deliverables:
  a) Define team roles (at minimum): Executive Sponsor, Technical
     Lead, Data Lead, Research Lead, Communications/Ops Lead.
     Alex Zelenski is Executive Sponsor.
  b) Define decision authority: who decides what, at what level.
     Strategic commits → Executive Sponsor. Technical architecture
     → Technical Lead. Data methodology → Data Lead + Research Lead.
     Public comms → Communications/Ops Lead.
  c) Define meeting cadence: weekly operational sync, monthly
     stakeholder-facing review, quarterly formal review (Dec 2).
  d) Define escalation path: what gets raised to Executive Sponsor
     vs. resolved at working level.
  e) Document governance in a single living doc (PROJECT_VOLUSIA_GOV.md
     or equivalent, kept in this folder).

Success signal: A new person (internal or partner) can read the
governance doc and know exactly what they own, who decides what, and
when things are reviewed.

Status: START. Governance doc drafted this plan's first week.

2.2 ITEM 2: DATA ASSET AUDIT AND GAP REPORT

Current state: DATA_CATALOG.md lists ten categories and named sources,
but no actual inventory of what's available, fresh, machine-readable,
or missing for Volusia County right now.

Q4 deliverable: An audit report covering all ten categories with
per-source status — available via API, available via download, requires
manual work, gated (subscription/permission), or missing — plus a
prioritized gap list.

Sub-deliverables:
  a) For each source in DATA_CATALOG.md (BLS LAUS/QCEW, Census ACS
     DP03/DP05 for FIPS 12127, BEA CAINC1, Zillow ZHVI/ZORI, Realtor.com,
     Volusia Property Appraiser, FDOT traffic, VOTRAN, CVB, NOAA, FCC,
     FEMA, USGS, CDC, FL DOH, etc.): record
       - Current availability (API / download / manual / gated / missing)
       - Most recent vintage observed
       - Machine-readability (CSV, JSON, GeoJSON, API, PDF-only, other)
       - Known access friction (auth, rate limits, scraping needed,
         subscription, FOIA, manual contact)
       - Refresh cadence the source publishes
       - Gap status (do we have it, need it, can't get it)
  b) Produce a single gap report document in this folder.
  c) Produce a prioritized list: what to build/fetch first to power
     the baseline portal.

Success signal: Someone can read the audit and immediately know which
datasets are ready to go, which need a scraper, which need a manual
request, and which are simply unavailable. No guessing.

Status: START. This is the Q4 work item with the highest leverage for
everything downstream. Begins week 1 along with governance.

2.3 ITEM 3: BASELINE DATA PORTAL — KEY ECONOMIC INDICATORS

Current state: No portal exists. No actual datasets loaded anywhere
Project Volusia can serve.

Q4 deliverable: A baseline portal (even if minimal) showing key
economic indicators for Volusia County, sourced from real data,
refreshable, with documented sources and limitations.

Sub-deliverables:
  a) Pick the first indicator set from the audit (likely: BLS LAUS
     unemployment for Volusia County, Census ACS DP03 economic
     characteristics and DP05 demographic for FIPS 12127, BEA local
     personal income CAINC1). Start small — three to five indicators.
  b) Fetch real data. Not mock data. Not "we will get this later."
     Real, current, cited data.
  c) Publish through a baseline portal: could be a static generated
     page, a small web app, a dashboard stub, or a documented dataset
     bundle with a README — the bar is "someone can open it and see
     real Volusia economic indicators with sources." The minimum viable
     portal is better than the perfect portal that never ships.
  d) Document methodology and sources alongside the portal. Every
     number cites its source and vintage. Limitations stated.
  e) Make it refreshable. Not necessarily automated on day one, but
     the refresh path is documented and repeatable.

Success signal: An external stakeholder (business owner, resident,
investor, local official) can open the portal, see real numbers for
Volusia County, and know where they came from and how old they are.

Status: START after the data audit identifies the first fetchable
indicators. Probably week 2-3.

2.4 ITEM 4: STAKEHOLDER INTERVIEWS — ALL FOUR GROUPS

Current state: No interviews conducted. No documented stakeholder
input. The guiding principles describe four constituencies; none have
been spoken to yet for Project Volusia specifically.

Q4 deliverable: A documented set of initial stakeholder conversations
across all four groups, with themes captured and a report of what
stakeholders actually need (vs. what the documents assume they need).

Sub-deliverables:
  a) Define the interview protocol from METHODOLOGY.md section 4.2
     (semi-structured guide, role/perspective documented, themes not
     quotes, opinion vs. fact distinguished).
  b) Identify and contact a small set of representatives from each
     group — at minimum one or two per group to start:
       - Business owners (small business, retail, hospitality, services)
       - Residents (varied: working, retired, fixed income, commuter)
       - Tourists — harder to reach directly; initial input may come
         from CVB, hospitality operators, or visitor-facing service
         operators who see tourists daily
       - Industry movers (local officials, economic development,
         investors, developers, nonprofits, educators)
  c) Conduct interviews. Record themes. Do not over-sample in Q4 —
     the goal is initial signal, not statistical representativity.
  d) Produce a stakeholder input summary: what they need, what they
     lack today, what would make Project Volusia useful to them.
  e) Feed findings back into portal and tool priorities. If
     stakeholders say they need X, that is data about priorities.

Success signal: The four documents' assumptions about stakeholder
needs are tested against actual stakeholder voices. The record exists
and is referenced in future decisions.

Status: START alongside audit. Interview guide drafted in week 1;
first conversations week 2-4.

Note: Tourist-facing interviews are the hardest group to reach directly
in Q4. Plan for that. Initial tourist intelligence may come indirectly
through CVB and hospitality operators. That is acceptable for a
Phase 1 start; direct tourist input becomes more feasible as the
tourist-facing APIs and tools from Phase 2 take shape.

2.5 ITEM 5: PUBLISH COMMERCE RELIABILITY STANDARDS

Current state: COMMERCE_RESEARCH_RELIABILITY.md exists as an internal
charter document with detailed standards and metrics. It has not been
published or operationalized as a live reference.

Q4 deliverable: The commerce reliability standards are published as a
real, usable reference — not just a document that sits in a folder.

Sub-deliverables:
  a) Make the standards visible and navigable — publish alongside the
     baseline portal or as a standalone reference in the Project Volusia
     public surface. The content is already written; the work is making
     it accessible and operational.
  b) Define how the metrics in the document (order accuracy >=99.95%,
     price accuracy >=99.99%, inventory freshness p95 <30s, checkout
     success >=98%, dispute rate <0.1%, fulfillment SLA >=99%, NPS >=60,
     time-to-detect <60s, time-to-resolve <4hrs) become measurable when
     commerce systems are built — not necessarily all measurable on day
     one, but the measurement plan exists.
  c) Connect the standards to the stakeholder-facing materials. A
     business owner reading the portal or dashboard should be able to
     find the reliability standards that back what they're seeing.

Success signal: A business owner or partner can find the reliability
standards and understand what they mean and how they'll be measured,
not just that they exist in a document.

Status: START. Content ready. Publishing and operationalizing in Q4.

2.6 ITEM 6: OPEN-SOURCE FIRST INTERNAL TOOLS

Current state: TOOLS_CATALOG.md lists 21 tools across five categories,
all specified but none built or published.

Q4 deliverable: At least the first internal tool(s) built and
documented, following the tool development standards in TOOLS_CATALOG.md
section 3, and made available in open form.

Sub-deliverables:
  a) Pick one or two tools from the catalog to build first, based on
     the data audit — the tools that feed the baseline portal get
     priority. The Census ACS wrapper and BLS scraper are the natural
     first candidates because they're the primary sources for economic
     indicators and have documented public APIs.
  b) Build the tool to the standards in TOOLS_CATALOG.md section 3:
     --help flag, timestamped logging, documented dependencies,
     tested against sample data, open output formats (CSV/JSON/GeoJSON/
     Parquet).
  c) Publish the tool in open source form with documentation. Not
     internal-only. The charter says open by default.
  d) Run the tool against real Volusia County data and produce a real
     output. A tool that exists but has never been run on real data is
     a prototype, not a deliverable.

Success signal: A real tool exists, is documented, is open, and has
produced real output for Volusia County from a real data source.

Status: START after data audit identifies the first tool to build.
Week 2-4.

Note: "First tools" is plural intentionally — one is the minimum, two
is better if the audit shows two high-priority sources ready to go
in parallel. Don't let perfect tool architecture delay the first real
tool that runs on real data.

---

3. Q4 WEEK-BY-WEEK ANCHOR

Q4 2026 has roughly 13 working weeks (early October through late
December). This plan anchors them as:

WEEK 1 (early October):
  - Draft and ratify PROJECT_VOLUSIA_GOV.md (Item 1)
  - Kick off data asset audit (Item 2) — begin per-source inventory
  - Draft stakeholder interview guide (Item 4)
  - Identify first tool candidates from audit needs (Item 6)
  - Review existing charter docs for anything that needs updating
    before publication (Items 3, 5)

WEEK 2-3 (mid October):
  - Complete data audit for first priority categories (economic,
    demographic — the ones that power the baseline portal)
  - First stakeholder interviews begin (Item 4)
  - Build first tool(s) — Census ACS and/or BLS for Volusia County
    (Item 6)
  - Begin baseline portal scoping based on audit results (Item 3)

WEEK 4-6 (late October through November):
  - Run first tool(s) on real Volusia data, produce real output
    (Item 6)
  - Load first economic indicators into baseline portal (Item 3)
  - Continue stakeholder interviews across groups (Item 4)
  - Publish commerce reliability standards in accessible form (Item 5)
  - Finish data audit for remaining categories; produce gap report
    (Item 2)

WEEK 7-10 (November through early December):
  - Baseline portal v0 live with at least the first economic indicators
    and sourced, refreshable data (Item 3)
  - Stakeholder interviews wrapping; stakeholder input summary drafted
    (Item 4)
  - Tools published in open form (Item 6)
  - Governance operating; weekly syncs running (Item 1)

WEEK 11-13 (December, leading to Dec 2 review):
  - December 2, 2026 review: demonstrate each of the six items with
    real deliverables, not just status reports.
  - Portal live with real data.
  - Tools built, run, published.
  - Stakeholder input captured across all four groups (or documented
    plan for the group that wasn't reachable in Q4).
  - Commerce reliability standards published.
  - Governance document live.
  - Data audit complete with gap report.
  - Plan for Q1 2027 / Phase 1 continuation set.

---

4. SUCCESS CONDITIONS FOR Q4

By December 2, 2026, the following are true, demonstrable, and not
just status updates:

  [ ] Project Volusia governance document exists and is in use.
  [ ] Data asset audit complete, covering all ten DATA_CATALOG.md
      categories, with a gap report and prioritized fetch/build list.
  [ ] Baseline data portal live with at least three real economic
      indicators for Volusia County, sourced, cited, refreshable.
  [ ] Stakeholder interviews conducted across all four groups (or a
      documented plan for the unreachable group, with initial input
      from proxies where direct contact wasn't possible).
  [ ] Commerce reliability standards published in accessible form and
      connected to stakeholder-facing materials.
  [ ] At least one internal tool built, documented, published in open
      form, and run on real Volusia County data with real output.
  [ ] December 2 review has concrete deliverables to present, not
      just a plan.

---

5. WHAT DOES NOT CARRY INTO Q4

These are deferred. Not canceled — deferred. If one becomes necessary
for a Phase 1 deliverable, it gets reconsidered. Otherwise:

  - Phase 2 work (portal v2.0, business owner dashboards, resident
    data access, tourist APIs, developer portal, quarterly briefings)
    begins only after Phase 1 foundations are in place. Q4 is not the
    time to build Phase 2 before Phase 1 exists.
  - Predictive models, scenario planning, climate modeling, ML
    (Phase 3 items) — too early.
  - Regional integration with Orlando, Titusville, Palm Coast, state
    agencies (Phase 3) — too early.
  - New initiative outside the Project Volusia scope.
  - Any work whose only justification is "it might be useful someday."

---

6. CONSTRAINTS AND ASSUMPTIONS

6.1 Assumptions:
  - ZQM Labs capacity exists to execute this plan with the existing
    technical team. If it does not, that is a signal to raise, not a
    reason to soften the commitment.
  - The data sources listed in DATA_CATALOG.md are as accessible as
    their documentation describes. The audit will confirm or contradict
    this.
  - Stakeholders are reachable and willing to be interviewed. If
    specific groups are hard to reach in Q4, that is data about the
    stakeholder landscape and gets documented.

6.2 Constraints:
  - Q4 ends December 31. December 2 review is the anchor. Work after
    that date is Q1 2027.
  - The plan is a delivery plan, not a perfection plan. A minimal
    baseline portal with real data beats a perfect portal that doesn't
    exist in December.
  - The first tools don't need to cover every category. They need to
    exist, be open, and run on real data.

---

7. DOCUMENTATION OUTPUTS EXPECTED FROM Q4

These files should exist in the Project-Volusia folder by December 2:

  STRATEGIC_FOCUS_Q4_2026_2027.md         (this folder — already created)
  Q4_2026_EXECUTION_PLAN.md               (this file)
  PRIORITY_TRADEOFFS.md                   (this folder — already created)
  PROJECT_VOLUSIA_GOV.md                  (governance — Item 1)
  DATA_ASSET_AUDIT_VOLUSIA.md             (audit + gap report — Item 2)
  [Baseline portal — location TBD by implementation]
  [First tool(s) — location TBD by implementation]
  STAKEHOLDER_INPUT_SUMMARY_Q4_2026.md   (interview themes — Item 4)
  COMMERCE_RELIABILITY_PUBLIC.md          (published standards — Item 5)

Specific paths for the portal and tools depend on implementation. The
document outputs are plain files in this folder.

---

8. REVIEW AND FEEDBACK

This plan is a starting point, not a final decree. It should be read,
challenged, and refined before execution. The December 2 review is the
first formal checkpoint.

Feedback channels:
  - Internal: weekly operational sync (once governance is set)
  - Stakeholder: interview findings feed back into priorities
  - External (later): once the portal and tools are public, feedback
    from actual users becomes a primary input

---

Document owner: Alex Zelenski / Project Volusia Leadership
Related: STRATEGIC_FOCUS_Q4_2026_2027.md, PRIORITY_TRADEOFFS.md,
         MISSION_STATEMENT.md, TIMELINE_AND_ROADMAP.md,
         DATA_CATALOG.md, TOOLS_CATALOG.md, METHODOLOGY.md
Next review: 2026-12-02
