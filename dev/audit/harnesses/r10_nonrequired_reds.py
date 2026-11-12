#!/usr/bin/env python3
"""r10-hotfix-nonrequired-reds: who owes a `## Red checks` answer, base vs head.

    python3 dev/audit/harnesses/r10_nonrequired_reds.py --base <sha>

Runs `policy_lint.mjs --pr-body` from <base> and from the working tree over the
same body and diff paths (the reporter's own script touched), and prints the
reds each owes. The head reads the required set live (`merge_train.py
owed-reds`), so it needs `gh` with a token. Case D, a body naming every red, is
the null control: both ends owe nothing.
"""
import argparse, os, pathlib, re, subprocess, tempfile

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
CASES = [("A reporter red, reporter input touched", "unnamed", ["tests / nightly-status"]),
         ("B required unit red", "unnamed", ["tests / typing"]),
         ("C non-required red", "unnamed", ["docs / links"]),
         ("D null: every red named", "named", ["tests / nightly-status", "tests / typing", "docs / links"])]


def owed(lint: pathlib.Path, body: pathlib.Path, paths: pathlib.Path, reds: list) -> list:
    r = subprocess.run(["node", str(lint), "--pr-body", str(body), "--head", "0" * 40, "--paths-file", str(paths),
                        "--existing-file", str(paths), *[x for n in reds for x in ("--red", n)]],
                       capture_output=True, text=True, cwd=ROOT)
    return re.findall(r"check `([^`]+)` is red and `## Red checks` does not name it", r.stdout)


def main() -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--base", required=True)
    base = a.parse_args().base
    body = (ROOT / "tools/policy/fixtures/policy-rot/prepr/unnamed-red.md").read_text()
    # The fixture's section is the literal `none`; naming every red replaces it.
    # A fixture whose section moved stops here rather than measure a body naming none.
    unanswered = "## Red checks\n\nnone\n"
    assert body.count(unanswered) == 1, "unnamed-red.md's `## Red checks` no longer reads `none`"
    named = body.replace(unanswered, "## Red checks\n\n" + "".join(f"- `{n}`: answered.\n" for n in CASES[3][2]))
    # The base copy sits beside the head's, so its relative imports resolve.
    old = ROOT / "tools/policy" / f".base_policy_lint_{os.getpid()}.mjs"
    old.write_text(subprocess.run(["git", "show", f"{base}:tools/policy/policy_lint.mjs"], capture_output=True,
                                  text=True, check=True, cwd=ROOT).stdout)
    try:
        with tempfile.TemporaryDirectory() as td:
            t = pathlib.Path(td)
            (t / "unnamed").write_text(body); (t / "named").write_text(named)
            (t / "paths").write_text("tests/nightly_status.py\n")
            for label, b, reds in CASES:
                print(f"{label}: base owed={owed(old, t / b, t / 'paths', reds) or 'none'}"
                      f" | head owed={owed(ROOT / 'tools/policy/policy_lint.mjs', t / b, t / 'paths', reds) or 'none'}")
    finally:
        old.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
