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
written: no state ref, or no PLAN.html at the newest one (the workflow deploys
the site without a plan and warns). A closed round's state ref stays the newest
until `closeout.py --apply` deletes it, so its page is served until then; only
after that delete, and before the next round's state ref, is there no page.
Refusals, rc 1 and nothing
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


#: (old, new, the check that must fail). Each old string appears once in this file.
MUTANTS = {
    "string_order": ("    rounds = [int(m[1]) for r", "    rounds = [m[1] for r",
                     "the newest round is the highest N, by number, never by string order (10 > 9)"),
    "leak_published": ("    why = refusal(text, ident)\n", "    why = None\n",
                       "refused, rc 1 and nothing written: a page naming a home directory"),
    "attribution_published": (" + ref_privacy.attribution(text)\n", "\n",
                              "refused, rc 1 and nothing written: a page carrying a tool's attribution"),
    "absent_refused_red": ('        return 2, f"plan_public: NOTHING TO PUBLISH: no {state_docs', '        return 1, f"plan_public: NOTHING TO PUBLISH: no {state_docs',
                           "nothing to publish, rc 2 and nothing written: no PLAN.html at the newest ref (an older round's is never taken)"),
    "host_ident_dropped": ("ident or ref_privacy.Identity.of_host()", "ident",
                           "the CLI over a scratch repository: a clean page is staged, rc 0"),
    "main_rc0": ("    return rc\n", "    return 0\n",
                 "the CLI over a scratch repository: a page naming a home directory is refused, rc 1 and nothing written"),
    "main_url_rc1": ("        print(PLAN_URL)\n        return 0", "        print(PLAN_URL)\n        return 1",
                     "url prints PLAN_URL alone, rc 0"),
}


def self_test(mutants: bool = True) -> int:
    fails: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            fails.append(name)

    page = "<!doctype html><html><body>plan</body></html>\n"
    refs = ("refs/remotes/origin/handoff/audit-r9-plan\nrefs/remotes/origin/handoff/audit-r10-plan\n"
            "refs/remotes/origin/handoff/audit-r10-roster\nrefs/remotes/origin/handoff/audit-r11-planx\n")
    ident = ref_privacy.Identity.made({"/ho" + "me/alice"}, {"alice"}, 1234, {"box"})

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
        "a page naming a home directory": ({want: page.replace("plan", "/ho" + "me/alice/wt/plan")}, refs),
        "a page naming a session scratch root": ({want: page.replace("plan", "/t" + "mp/claude-" + "1234/x")}, refs),
        "a page carrying a tool's attribution": ({want: page + "Co-Authored-By: " + "Claude <x@y>\n"}, refs),
    }
    for name, (pages, refs_out) in cases.items():
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            rc, msg = stage(out, out, fake(pages, refs_out), ident)
            check(f"refused, rc 1 and nothing written: {name}",
                  rc == 1 and "REFUSED" in msg and not (out / "plan").exists())
    for name, body, want_rc in (("a clean page is staged, rc 0", page, 0),
                                ("a page naming a home directory is refused, rc 1 and nothing written",
                                 page.replace("plan", "/ho" + "me/alice/wt/plan"), 1),
                                ("no state ref, rc 2 and nothing written", None, 2)):
        with tempfile.TemporaryDirectory() as d:  # main() as the workflow runs it: no ident, the host's
            repo, out = Path(d) / "repo", Path(d) / "site"
            # tests/ beside this tool's own tree: a mutant copy's __file__ sits in a scratch directory
            sys.path.insert(0, str(Path(ref_privacy.__file__).resolve().parents[3] / "tests"))
            from throwaway_git import throwaway_git_init
            env = throwaway_git_init(repo, "-q")
            g = ["git", "-C", str(repo)]
            if body is not None:
                f = repo / "handoff" / "round10" / "state" / state_docs.PLAN_PAGE
                f.parent.mkdir(parents=True)
                f.write_text(body)
                subprocess.run(g + ["add", "-A"], env=env, check=True)
                tree = subprocess.run(g + ["write-tree"], env=env, capture_output=True, text=True,
                                      check=True).stdout.strip()
                sha = subprocess.run(g + ["commit-tree", tree, "-m", "state"], env=env, capture_output=True,
                                     text=True, check=True).stdout.strip()
                subprocess.run(g + ["update-ref", "refs/remotes/origin/handoff/audit-r10-plan", sha], env=env,
                               check=True)
            try:
                cl, io = __import__("contextlib"), __import__("io")
                with cl.redirect_stdout(io.StringIO()), cl.redirect_stderr(io.StringIO()):
                    rc = main(["stage", "--out", str(out), "--repo", str(repo)])
            except Exception as e:  # a crash is a failed case, never an aborted self-test
                rc = repr(e)
            staged = out / PLAN_DIR / "index.html"
            check(f"the CLI over a scratch repository: {name}",
                  rc == want_rc and (staged.read_text() == body if want_rc == 0 else not staged.exists()))
    url_out = __import__("io").StringIO()
    with __import__("contextlib").redirect_stdout(url_out):
        url_rc = main(["url"])
    check("url prints PLAN_URL alone, rc 0", url_rc == 0 and url_out.getvalue() == PLAN_URL + "\n")
    check("PLAN_URL is under the Pages site and ends in the staged directory",
          PLAN_URL.startswith(PAGES_URL) and PLAN_URL.endswith(f"/{PLAN_DIR}/"))
    if mutants:
        import importlib.util
        # the code under mutation is all but the table, which spells every old string again
        code, mark, rest = Path(__file__).read_text().partition("#: (old, new, the check")
        table, sep, tail = rest.partition("\n\ndef self_test(")
        for mid, (old, new, case) in MUTANTS.items():
            n = code.count(old) + tail.count(old)
            if n != 1:
                check(f"mutant {mid} applies (old string x{n})", False)
                continue
            with tempfile.TemporaryDirectory() as d:
                mp = Path(d) / "plan_public.py"
                mp.write_text(code.replace(old, new) + mark + table + sep + tail.replace(old, new))
                spec = importlib.util.spec_from_file_location(f"pp_mutant_{mid}", mp)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                out = __import__("io").StringIO()
                saved, sys.stdout = sys.stdout, out
                try:
                    mod.self_test(mutants=False)
                finally:
                    sys.stdout = saved
            check(f"mutant {mid} killed by: {case}", f"FAIL {case}" in out.getvalue())
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
