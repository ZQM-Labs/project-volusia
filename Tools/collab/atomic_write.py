#!/usr/bin/env python3
"""Atomically write a file: same-directory temp file + atomic os.replace().

Readers on the shared drive never observe a half-written file. Pair with
claim.py: claim the path first, atomically write, verify, release.

Usage:
    python atomic_write.py <path> --content "all file text"
    echo "all file text" | python atomic_write.py <path>

See COLLABORATION_CONVENTIONS.md at the repo root for the full protocol.
"""

import argparse
import os
import sys
from pathlib import Path


def atomic_write(path: Path, content: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(content, encoding="utf-8", newline="\n")
        os.replace(tmp, path)  # atomic rename on the same volume
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
    return path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("path")
    p.add_argument("--content", default=None, help="Text to write. If omitted, stdin is read.")
    args = p.parse_args()
    content = args.content if args.content is not None else sys.stdin.read()
    out = atomic_write(args.path, content)
    print(f"ATOMIC WRITE OK: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
