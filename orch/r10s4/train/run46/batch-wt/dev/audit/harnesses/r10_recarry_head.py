#!/usr/bin/env python3
"""R10-RECARRY-HEAD: does each `## Head` note writer put its note where pr-contract reads it?

    python3 dev/audit/harnesses/r10_recarry_head.py <tree>

<tree> is a checkout or `git archive` export (base or head). Every python
heredoc in the seat openers (open_pr.sh, update_pr.sh, handoff_push.sh) that
writes a `## Head` note is extracted from <tree> and run, as the script runs
it (PYTHONPATH=<tree>/tools/pr), over three bodies whose `## Head` heading is
preceded by text the first substring `## Head` matches:

  quoted  prose quoting `## Head` (#2400's shape)
  fenced  a fenced example holding a `## Head` line and a blank line
  crlf    a body saved with CRLF line ends (a browser edit); the writers' text-mode
          read normalises it, so it reads named at both ends -- a second control

and a plain body as the null control. `app_push.sh --recarry` is driven by its
own `--self-test` (the R10-RECARRY-HEAD arms), not here. The verdict per run
is pr-contract's reader, `policy_lint.mjs --pr-body --head H` from the checkout
holding this harness (the writers vary with <tree>, the reader does not):
`named` when `## Head` names H, `unnamed` when it does not, `crash` when the
writer exits non-zero. A reader that prints no `PR-BODY:` summary line refuses
the run (rc 1) rather than reading as named.
"""
import os, re, subprocess, sys, tempfile

H = "d" * 40
SITES = ("tools/audit/seat/open_pr.sh", "tools/audit/seat/update_pr.sh", "tools/audit/seat/handoff_push.sh")
TAIL = "## Head\n\n`%s`\n\n## Figures\n\nf\n" % ("0" * 40)
BODIES = {
    "plain": TAIL,
    "quoted": "Intro: update_pr.sh words the `## Head` note.\n\n" + TAIL,
    "fenced": "Example:\n\n```\n## Head\n\n`x`\n```\n\n" + TAIL,
    "crlf": TAIL.replace("\n", "\r\n"),
}


def heredocs(text):
    for m in re.finditer(r"python3 - ([^\n]*)<<'(\w+)'\n(.*?)\n\2\n", text, re.S):
        if "## Head" in m.group(3) or "prefix(" in m.group(3):
            yield text[: m.start()].count("\n") + 1, m.group(3)


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


ROOT = str(repo_root(__file__))


def verdict(body):
    out = subprocess.run(["node", "tools/policy/policy_lint.mjs", "--pr-body", body, "--head", H],
                         capture_output=True, text=True, cwd=ROOT).stdout
    if "PR-BODY:" not in out:
        sys.exit("r10_recarry_head: REFUSE: the reader printed no PR-BODY: line for %s" % body)
    return "unnamed" if "`## Head` does not name" in out else "named"


def main(tree):
    tree = os.path.abspath(tree)
    rows = 0
    with tempfile.TemporaryDirectory() as d:
        for site in SITES:
            for line, code in heredocs(open(os.path.join(tree, site)).read()):
                cells = []
                for shape, text in BODIES.items():
                    p = os.path.join(d, "body.md")
                    with open(p, "w", newline="") as f:
                        f.write(text)
                    r = subprocess.run([sys.executable, "-", p, H, "c" * 40, "7", ""], input=code, text=True,
                                       capture_output=True, env={**os.environ, "PYTHONPATH": os.path.join(tree, "tools/pr")})
                    cells.append("%s=%s" % (shape, "crash" if r.returncode else verdict(p)))
                rows += 1
                print("%s:%d %s" % (site, line, " ".join(cells)))
    print("writers: %d" % rows)
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]) if len(sys.argv) == 2 else 2)
