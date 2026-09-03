# Contributing to ZQM Projects

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch ()
3. Commit your changes ()
4. Push to the branch ()
5. Open a Pull Request

## Code Standards

- Follow existing code style
- Add tests for new features
- Update documentation as needed

## Reporting Issues

- Use GitHub Issues for bug reports
- Include steps to reproduce
- Specify your environment

## Questions?

Open an issue or discussion in the repository.

---

## Multi-Writer Conventions (Shared Drive)

This repository is edited by humans AND AI agents on a shared network drive =
they can collide. Before editing:

1. Read [`COLLABORATION_CONVENTIONS.md`](COLLABORATION_CONVENTIONS.md) — the
   multi-writer protocol (claims, atomic writes, git hygiene).
2. Claim the file you will edit with
   [`Tools/collab/claim.py`](Tools/collab/claim.py).
3. Re-read the file immediately before every write; never edit from a stale
   snapshot.
4. Verify after every write (re-read; `py_compile` for Python).
5. Release the claim when done and announce in `CONTRIBUTION_LOG.md`.
