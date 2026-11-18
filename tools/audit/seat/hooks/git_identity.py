#!/usr/bin/env python3
"""SessionStart hook: pin the orchestrator checkout's git identity from a state file.

    python3 -I tools/audit/seat/hooks/git_identity.py [--state DIR]

WHY. A commit made from the orchestrator's checkout under the host's default
identity is refused by the identity contract (decision 0011) only after it is
pushed. $HPO_STATE_DIR/git-identity holds two lines, the name then the email;
this hook sets them as the checkout's LOCAL config when they differ, and prints
one `GIT-IDENTITY set` line saying so. Silent when they already match, and
INERT without orch-checkout or without the identity file: it never invents an
identity. It touches local config only, never the working tree or HEAD.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _git(repo: str, *a: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)


def report(state: Path) -> list[str]:
    try:
        repo = (state / "orch-checkout").read_text().strip()
        ident = (state / "git-identity").read_text().splitlines()
    except OSError:
        return []
    if not repo or len(ident) < 2 or not ident[0].strip() or not ident[1].strip():
        return []
    out = []
    for key, want in (("user.name", ident[0].strip()), ("user.email", ident[1].strip())):
        have = _git(repo, "config", "--local", "--get", key)
        if have.returncode == 0 and have.stdout.strip() == want:
            continue
        r = _git(repo, "config", "--local", key, want)
        out.append(f"GIT-IDENTITY set {key}" if r.returncode == 0 else f"UNREADABLE git-identity {key}")
    return out


def main(argv: list[str]) -> int:
    state = os.environ.get("HPO_STATE_DIR", "")
    if argv[:1] == ["--state"] and len(argv) > 1:
        state = argv[1]
    if state:
        for ln in report(Path(state)):
            print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
