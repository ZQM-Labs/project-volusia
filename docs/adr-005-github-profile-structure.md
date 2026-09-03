# ADR-005 — GitHub Profile Structure and Canonical Public Surfaces

Status: Accepted (2026-09-03)
Owner: ZQM Labs Ops / Project Volusia Executive Sponsor

## Context

Project Volusia is published through two GitHub organizations:

- **ZQM-Labs** — Research & development arm; hosts `project-volusia` (this
  working copy: open-data pipeline, FastAPI portal, contribution API, and the
  charter/governance corpus).
- **ZQM-Computing** — Services / IT arm; hosts `volusia-portal` (public React
  data portal).

Audit of the live GitHub profile information on 2026-09-03 found
inconsistencies:

1. `profile/README.md` still fronts "Windows endpoint attestation & forensic
   tooling", while the live org description, the root README, and every
   Project Volusia charter make Project Volusia the strategic focus
   (Q4 2026–2027).
2. Root `README.md` carries hardcoded green shields ("tests passing", "ruff
   passing", "mypy passing") that the repository does not actually prove.
3. Root `README.md` lists ~25 repositories, but only `project-volusia`
   (ZQM-Labs) and `volusia-portal` (ZQM-Computing) are public today.
4. CI workflows exist (`ci`, `tests`, `security-scan`, `supply-chain-scan`,
   `volusia-pipeline`), but several would not pass as written (no ruff config,
   no test directory, scanner downloaded from a non-public repository).

## Decision

1. **Canonical public surfaces.**
   - ZQM-Labs org profile (`profile/README.md`) → **Project Volusia strategic
     focus first**; attestation/forensics and AI-council are secondary
     workstreams.
   - `ZQM-Labs/project-volusia` → the open-data platform repository.
   - `ZQM-Computing/volusia-portal` → the public-facing data portal.
2. **Honest badges.** Root `README.md` shows live workflow badges only
   (`ci.yml`, `volusia-pipeline.yml` on `ZQM-Labs/project-volusia`). Hardcoded
   "passing" shields are removed; they made claims the repo does not prove.
3. **CI follow-up (tracked, not done here).** Bringing `ci.yml` / `tests.yml`
   to green (ruff config, real test suite, public scanner repo) is owned by
   Ops/CI and is a separate work item. ADR-005 only documents intent.
4. **Git topology.** The working copy tracks `project-volusia/main` and also
   mirrors `ZQM-Labs/ZQM-Labs` (org profile + GitHub Pages site). Push target
   for code = `project-volusia`; the org repo receives profile/site content.

## Consequences

- Org description, org profile README, and repo README now tell one consistent
  story: Project Volusia first.
- README no longer claims a passing/release state that CI cannot show.
- Public-vs-private repo split is explicit (one flagship repo per org today).
- Remote-side actions (org description already set; repo visibility, branch
  protection, Secrets for the pipeline workflow) remain with the repo owner;
  this ADR records the intent for whoever executes them.

Related: COLLABORATION_CONVENTIONS.md §4 (git protocol), docs/ADR.md
---

## Deeper Findings — GitHub Pages Site Audit (2026-09-03

Reading the repository's GitHub Pages site (`zqm-labs.github.io/ZQM-Labs/`;
10 static HTML pages + `robots.txt` + `sitemap.xml`) surfaced more divergence:

1. **Site branding is the OPPOSITE of the org profile.** Every page fronts
   "attestation & council" (`ZQM Labs: umbrella organization for attestation,
   security, and AI tooling`; brand-sub `— attestation & council`); **no page
   mentions Project Volusia / Volusia County at all**. The org's canonical surfaces
   (org description, root README, `profile/README.md` — ADR-005) say
   Project Volusia first.
2. **"Public surface: 7 public repos" badge** in the site nav — but only
   `project-volusia` is public to a logged-out visitor today. The 6 attestation
   repos (pqc-readiness-toolkit, zqm-attestation-toolkit, zqm-public-tools,
   awesome-windows-attestation, zqm-security-policy, zqm-shield) are not
   yet visible publicly.

3. **Mechanical defects found and fixed（P1-016):**
   - `*-es.html` meta descriptions carried duplicated `content` attributes
     (invalid HTML). The redundant English duplicates were removed; the Spanish
     strings kept。
   - `sitemap.xml` omitted all five Spanish pages; added them（priorities/
     changefreq mirrored from the EN pages)。
   - `contact.html` masks the phone number (`+138****9994`) — intentional
     (screenshot-friendly public surface），noted for the owner。

## Decision (addendum)

- The GitHub **org** is the authoritative profile（Project Volusia first, ADR-005）。
- The GitHub **Pages site** is stale/aspirational: attestation landing，
  "7 public repos" that aren't public, Spanish pages half-translated, masked
  phone域。Owner decision needed**: rebrand the Pages site Volusia-first
  （attestation as services sub-page）or park it as a legacy/archive index／
  until then。Do not let the site contradict the org profile。
- **Sequencing bit**: making the six attestation repos public without first fixing
  the site would amplify the contradiction — rebrand the site first, then
  visibility of the attestation portfolio, not the other way around。



Consequences: a consistent public narrative depends on aligning the Pages site；
this is an owner action（approved scope），not yet executed。Related：the
README "Repos" table（≥25 repos, many internal/private），the site badge "7
public" and the live org "1 public" are three different truths that should converge
after the rebrand。





Related: ADR-005（main decision）, COLLABORATION_CONVENTIONS.md §4（git protocol）；
Document owner: Project Volusia Ops / Communications Lead