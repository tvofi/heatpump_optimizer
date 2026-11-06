#!/usr/bin/env python3
"""plan_public.py -- stage the ongoing round's plan page for the public site.

    python3 -I tools/audit/seat/plan_public.py stage --out DIR [--repo DIR]
    python3 -I tools/audit/seat/plan_public.py url
    python3 -I tools/audit/seat/plan_public.py --self-test

WHY THIS EXISTS (R10-OUTSIDE-INTAKE; tvofi, 2026-11-06: "the plan html for an
ongoing round should be made publically available from a suitable place in the
developer documentation"). `state_docs.py --plan` commits the round's plan page
as `PLAN.html` to the orphan state ref, where GitHub serves it only as source.
The Pages workflow (`.github/workflows/pages.yml`) runs `stage` from the
dispatched ref's tree before it checks out the release, and copies what it
writes into the site, so the page is served at PLAN_URL beside the product
page. The beat's `plan-beat` row dispatches that workflow after each push of
the state ref that carried a new page, so the public page refreshes at each
sweep that moved the plan.

STAGE reads the remote-tracking state refs (`origin/handoff/audit-r<N>-plan`,
the layout `state_docs.state_of` owns), takes the highest round N's PLAN.html
and writes it as `<out>/plan/index.html`. Nothing to publish, rc 2 and nothing
written: no state ref, or no PLAN.html at the newest one (between rounds: the
workflow deploys the site without a plan and warns). Refusals, rc 1 and nothing
written, which turn the deploy red: a page that is not an HTML document, and a page `ref_privacy` reads a host path, account name, uid or
session scratch root in, or a tool's attribution -- a public page carries
none of them. The UNAVAILABLE page `plan_page.py` writes over a stale plan is
an HTML document and is published as it is: the honest page, never the last
good one dressed as current.

URL prints PLAN_URL, the one place the public address is spelled; the
developer documentation and `outside_intake.py`'s answers link it.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ref_privacy  # noqa: E402
import state_docs  # noqa: E402

PAGES_URL = "https://tvofi.github.io/heatpump_optimizer/"
PLAN_DIR = "plan"
PLAN_URL = f"{PAGES_URL}{PLAN_DIR}/"
_STATE_REF = re.compile(r"^refs/remotes/origin/handoff/audit-r(\d+)-plan$")
_HTML = re.compile(r"^\s*<!doctype html", re.I)


def git(repo: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return p.returncode, p.stdout


def newest_round(refnames: list[str]) -> int | None:
    rounds = [int(m[1]) for r in refnames if (m := _STATE_REF.match(r.strip()))]
    return max(rounds) if rounds else None


def refusal(text: str, ident=None) -> str | None:
    """Why `text` may not be published as the public plan page, or None."""
    if not _HTML.match(text):
        return "not an HTML document"
    why = ref_privacy.leaks(text, ident or ref_privacy.Identity.of_host()) + ref_privacy.attribution(text)
    return f"{', '.join(why)} in the page" if why else None


def stage(repo: Path, out: Path, run=git, ident=None) -> tuple[int, str]:
    rc, refs = run(repo, "for-each-ref", "--format=%(refname)", "refs/remotes/origin/handoff/")
    n = newest_round(refs.splitlines()) if rc == 0 else None
    if n is None:
        return 2, "plan_public: NOTHING TO PUBLISH: no origin/handoff/audit-r<N>-plan ref; fetch the state refs first"
    st = state_docs.state_of(n)
    rc, text = run(repo, "show", f"refs/remotes/origin/{st.ref}:{st.dir}/{state_docs.PLAN_PAGE}")
    if rc != 0 or not text:
        return 2, f"plan_public: NOTHING TO PUBLISH: no {state_docs.PLAN_PAGE} at origin/{st.ref}"
    why = refusal(text, ident)
    if why:
        return 1, f"plan_public: REFUSED: round {n} {state_docs.PLAN_PAGE}: {why}"
    dest = out / PLAN_DIR / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)
    return 0, f"plan_public: round {n} {state_docs.PLAN_PAGE} from origin/{st.ref} -> {PLAN_DIR}/index.html"


def self_test() -> int:
    fails: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            fails.append(name)

    page = "<!doctype html><html><body>plan</body></html>\n"
    refs = ("refs/remotes/origin/handoff/audit-r9-plan\nrefs/remotes/origin/handoff/audit-r10-plan\n"
            "refs/remotes/origin/handoff/audit-r10-roster\nrefs/remotes/origin/handoff/audit-r11-planx\n")
    ident = ref_privacy.Identity.made({"/home/alice"}, {"alice"}, 1234, {"box"})

    def fake(pages: dict, refs_out: str = refs):
        def run(repo, *args):
            if args[0] == "for-each-ref":
                return 0, refs_out
            return (0, pages[args[1]]) if args[1] in pages else (128, "")
        return run

    want = f"refs/remotes/origin/handoff/audit-r10-plan:handoff/round10/state/{state_docs.PLAN_PAGE}"
    check("the newest round is the highest N, by number, never by string order (10 > 9)",
          newest_round(refs.splitlines()) == 10)
    with tempfile.TemporaryDirectory() as d:
        out = Path(d)
        rc, msg = stage(out, out, fake({want: page}), ident)
        got = (out / "plan" / "index.html").read_text() if (out / "plan" / "index.html").exists() else None
        check("a clean page at the newest state ref is staged as plan/index.html, rc 0", rc == 0 and got == page)
    for name, (pages, refs_out) in {
            "no state ref at all": ({}, "refs/remotes/origin/main\n"),
            "no PLAN.html at the newest ref (an older round's is never taken)":
                ({want.replace("r10", "r9").replace("round10", "round9"): page}, refs)}.items():
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            rc, msg = stage(out, out, fake(pages, refs_out), ident)
            check(f"nothing to publish, rc 2 and nothing written: {name}",
                  rc == 2 and "NOTHING TO PUBLISH" in msg and not (out / "plan").exists())
    cases = {
        "a page that is not an HTML document": ({want: "plan: 3 groups\n"}, refs),
        "a page naming a home directory": ({want: page.replace("plan", "/home/alice/wt/plan")}, refs),
        "a page naming a session scratch root": ({want: page.replace("plan", "/tmp/claude-1234/x")}, refs),
        "a page carrying a tool's attribution": ({want: page + "Co-Authored-By: " + "Claude <x@y>\n"}, refs),
    }
    for name, (pages, refs_out) in cases.items():
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            rc, msg = stage(out, out, fake(pages, refs_out), ident)
            check(f"refused, rc 1 and nothing written: {name}",
                  rc == 1 and "REFUSED" in msg and not (out / "plan").exists())
    check("PLAN_URL is under the Pages site and ends in the staged directory",
          PLAN_URL.startswith(PAGES_URL) and PLAN_URL.endswith(f"/{PLAN_DIR}/"))
    if fails:
        print(f"{len(fails)} self-test check(s) failed: " + ", ".join(fails))
        return 1
    print("plan_public self-test: all checks passed")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stage")
    s.add_argument("--out", required=True, type=Path)
    s.add_argument("--repo", type=Path, default=Path.cwd())
    sub.add_parser("url")
    a = ap.parse_args(argv)
    if a.cmd == "url":
        print(PLAN_URL)
        return 0
    rc, msg = stage(a.repo, a.out)
    print(msg, file=sys.stderr if rc else sys.stdout)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
