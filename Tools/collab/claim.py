#!/usr/bin/env python3
"""Claim / release / scan ownership locks for files edited on a shared drive.

Project Volusia lives on a network share edited by multiple humans and AI
agents. The claim protocol prevents two writers from editing the same file at
the same time (read-modify-write race). Claims carry a TTL so a crashed worker
never blocks work — an expired claim is treated as free.

Usage:
    python claim.py claim   <path> [--owner NAME] [--minutes 60] [--force]
    python claim.py release <path> [--owner NAME] [--force]
    python claim.py status  [<path>]
    python claim.py scan

Exit codes: 0 ok, 1 usage/error, 2 claim refused (held by someone else).
See COLLABORATION_CONVENTIONS.md at the repo root for the full protocol.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]  # .../Project-Volusia
CLAIMS_DIR = ROOT / "claims"
DEFAULT_TTL_MIN = 60


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _now() -> float:
    return time.time()


def _lock_path(path: Path) -> Path:
    clean = str(Path(path).resolve()).replace(":", "").replace("\\", "/").strip("/")
    return CLAIMS_DIR / (clean.replace("/", "__") + ".lock")


def _read(lock: Path) -> Optional[dict]:
    try:
        return json.loads(lock.read_text(encoding="utf-8"))
    except Exception:
        return None


def claim(path, owner: str, minutes: int, force: bool) -> int:
    CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
    lock = _lock_path(path)
    expires_epoch = _now() + minutes * 60
    data = {
        "file": str(Path(path).resolve()),
        "owner": owner,
        "claimed_at": _iso(),
        "expires_at": _iso(),
        "expires_epoch": expires_epoch,
    }
    existing = _read(lock) if lock.exists() else None
    if existing and existing.get("expires_epoch", 0) > _now() and not force:
        print(
            f"REFUSED: {data['file']} is claimed by {existing.get('owner')} "
            f"until {existing.get('expires_at')} — pick different work or ask the owner."
        )
        return 2
    if existing:
        reason = "expired" if existing.get("expires_epoch", 0) <= _now() else "forced"
        print(f"WARNING: overwriting {reason} claim by {existing.get('owner')}.")
    tmp = lock.with_name(lock.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, lock)  # atomic on the same volume
    print(f"CLAIMED: {data['file']} by {owner} until {data['expires_at']} ({minutes}m TTL).")
    return 0


def release(path, owner: Optional[str], force: bool) -> int:
    lock = _lock_path(path)
    if not lock.exists():
        print(f"RELEASE: no claim existed for {path}.")
        return 0
    existing = _read(lock) or {}
    if not force and owner and existing.get("owner") != owner:
        print(f"REFUSED: {lock.name} claimed by {existing.get('owner')}, not {owner}. Use --force if you must.")
        return 2
    lock.unlink(missing_ok=True)
    print(f"RELEASED: {path} (was claimed by {existing.get('owner', 'unknown')}).")
    return 0


def status(path: Optional[Path]) -> int:
    if path is not None:
        lock = _lock_path(path)
        data = _read(lock) if lock.exists() else None
        if data:
            marker = "ACTIVE" if data.get("expires_epoch", 0) > _now() else "EXPIRED"
            print(f"{marker}: {json.dumps(data)}")
        else:
            print(f"UNCLAIMED: {path}")
        return 0
    return scan()


def scan() -> int:
    if not CLAIMS_DIR.exists():
        print("No claims directory yet (nothing claimed).")
        return 0
    locks = sorted(CLAIMS_DIR.glob("*.lock"))
    if not locks:
        print("No active claims.")
        return 0
    now = _now()
    for p in locks:
        data = _read(p) or {"file": p.name}
        marker = "ACTIVE" if data.get("expires_epoch", 0) > now else "EXPIRED"
        print(f"{marker}  {data.get('file')}  — {data.get('owner', '?')} until {data.get('expires_at', '?')}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("claim", help="Claim a file for editing")
    pc.add_argument("path")
    pc.add_argument("--owner", default=os.environ.get("USERNAME") or os.environ.get("USER") or "agent")
    pc.add_argument("--minutes", type=int, default=DEFAULT_TTL_MIN)
    pc.add_argument("--force", action="store_true")
    pc.set_defaults(fn=claim)

    pr = sub.add_parser("release", help="Release a claim")
    pr.add_argument("path")
    pr.add_argument("--owner", default=os.environ.get("USERNAME") or os.environ.get("USER") or "agent")
    pr.add_argument("--force", action="store_true")
    pr.set_defaults(fn=release)

    ps = sub.add_parser("status", help="Show claim for a path (or all)")
    ps.add_argument("path", nargs="?", default=None)
    ps.set_defaults(fn=status)

    pscan = sub.add_parser("scan", help="List all claims")
    pscan.set_defaults(fn=scan)

    args = p.parse_args()
    try:
        if args.cmd == "claim":
            return args.fn(args.path, args.owner, args.minutes, args.force)
        if args.cmd == "release":
            return args.fn(args.path, args.owner, args.force)
        if args.cmd == "status":
            return args.fn(Path(args.path) if args.path else None)
        return args.fn()
    except Exception as e:  # noqa: BLE001 - CLI boundary
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
