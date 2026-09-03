# Tools/collab — concurrent-writer helpers

Small utilities that reduce read-modify-write collisions when multiple humans
and AI agents edit this repo from a shared network drive.

- **`claim.py`** — claim / release / scan TTL'd ownership locks for files being
  edited. Prevents two writers from editing the same file at the same time.
- **`atomic_write.py`** — write a file via a same-directory temp file + atomic
  `os.replace()`, so readers never see a half-written file.

The full multi-writer protocol lives at the repo root:
[`COLLABORATION_CONVENTIONS.md`](../../COLLABORATION_CONVENTIONS.md).
