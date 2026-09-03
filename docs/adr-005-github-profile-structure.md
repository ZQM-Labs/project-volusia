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