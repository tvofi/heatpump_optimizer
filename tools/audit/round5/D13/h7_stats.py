#!/usr/bin/env python3
"""D13 / round 5 -- the verdict vocabulary `policy_lint.mjs --stats` can read.

METRIC (one line). The number of distinct verdict words the production
`--stats` mode reports it read from `.claude/workflows/web-fix-wave.js`
(`verdict_grammar_classes`, the bracketed list on its first line) and the
number of distinct verdict-class rows its histogram then prints
(`verdict_class_rows`), measured over the window by RUNNING the production
entry point:

  node .claude/workflows/policy_lint.mjs --stats --since <ref-before-the-window>

THE CLAIM THIS MEASURES. `policy_lint.mjs` extracts the reviewer's vocabulary
with `VERDICT_LITERAL_RE = /"Fix review:\\s+([a-z]+)/g` over the wave script's
source, and the wave script teaches THIRTEEN words: `merge`, `blocked`, and the
eleven of `VERDICT_CLASSES` (the prompt names them by interpolating
`${VERDICT_CLASSES.join(', ')}`, which a literal scan cannot see, and the block
class in the grammar sits AFTER the head SHA, not at the verdict position). So
the histogram's verdict arm has one key in practice, and the eleven block
classes -- the wave script's own reason for having a vocabulary at all -- reach
no window-level count.

WHY A WORKTREE AND NOT AN EVAL. The instrument under measure is the CLI, and the
CLI reads its input from ROOT. Perturbing the input therefore means perturbing a
TREE, so this harness takes a detached worktree of the pinned baseline under the
temp root, applies a ONE-LINE edit to `.claude/workflows/web-fix-wave.js` there,
re-runs the same command, and removes the worktree. No live pull request and no
production file is touched.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 /tmp/heatpump-orch/audit-r5-D13/h7_stats.py
  ... --perturb verdict-word   # a third WORD at the verdict position
  ... --perturb class-list     # the eleven class words spelled out in the prompt

PERTURBATION AND DIRECTION. `--perturb verdict-word` adds one literal
`"Fix review: <word> ..."` to the reviewer prompt: `verdict_grammar_classes`
must RISE by 1 (2 -> 3), which is the control that the number is keyed on the
production file's text and not on a constant in this harness.
`--perturb class-list` replaces `${VERDICT_CLASSES.join(', ')}` with the eleven
words spelled out -- the change the instrument's own comment says would make its
arm informative -- and is a NULL CONTROL: the printed grammar must stay at 2,
because the extractor reads the word after `Fix review:` and never the class.
A run whose `--perturb class-list` moved the grammar would show this harness
measuring a rewrite of its own rather than the production reader.

MACHINE: any; the numbers are API-derived counts and the CLI's own output.
`RESULT api_failures=0` and `RESULT stats_enum_skipped` (the CLI's own
`UNCHECKED this run` line) are both required before a figure is evidence.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13lib as L  # noqa: E402

WAVE = ".claude/workflows/web-fix-wave.js"
LI = ".claude/workflows/policy_lint.mjs"


def git(*args):
    return subprocess.run(["git", "-C", str(L.ROOT)] + list(args),
                          capture_output=True, text=True)


def window_ref():
    """The commit before the window's oldest first-parent commit.

    `--stats --since <ref>` enumerates `<ref>..<main>`, so this reproduces the
    harnesses' own window without sharing their code path.
    """
    commits = L.window_commits()
    oldest = commits[0]["sha"]
    return git("rev-parse", f"{oldest}^1").stdout.strip()


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t, "environment"
    p = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if p.returncode == 0 and p.stdout.strip():
        return p.stdout.strip(), "gh auth token (read-only, this box)"
    raise SystemExit("no GITHUB_TOKEN/GH_TOKEN and `gh auth token` gave none: "
                     "the CLI would refuse to enumerate and report a window "
                     "with no pull request in it.")


def run_stats(root, since, tok):
    cmd = ["node", LI, "--stats", "--since", since]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=root,
                       env=dict(os.environ, GITHUB_TOKEN=tok))
    out = p.stdout + p.stderr
    if p.returncode not in (0, 1):
        raise SystemExit(f"the production CLI exited {p.returncode}: {out[-400:]}")
    return out


def parse(out):
    """(grammar classes, verdict rows, friction rows, enum-skipped?) from the CLI's text."""
    m = re.search(r'verdict grammar \[([^\]]*)\] read from', out)
    classes = [c.strip().strip('"') for c in m.group(1).split(",")] if m else []
    rows, block = [], []
    for line in out.split("\n"):
        m = re.match(r'^CENSUS\tverdict class\t(\d+)\t(\d+)\t(.+)$', line)
        if m:
            rows.append((m.group(3).strip(), int(m.group(1)), int(m.group(2))))
            if m.group(3).strip() != "merge":
                block.append(m.group(3).strip())
    fric = len(re.findall(r'^CENSUS\tfriction rule id\t', out, re.M))
    skipped = "UNCHECKED this run, not confirmed empty" in out
    return classes, rows, block, fric, skipped


def patch_wave(root, mode):
    """The one-line production edit, applied inside the worktree."""
    path = os.path.join(root, WAVE)
    text = open(path).read()
    if mode == "verdict-word":
        anchor = ('or "Fix review: blocked ${fix.head_sha} <class>: <why>"')
        if anchor not in text:
            raise SystemExit("verdict-word perturbation did not apply: the "
                             "reviewer prompt's verdict literal was not found")
        text = text.replace(
            anchor, anchor + ' or "Fix review: fold ${fix.head_sha}"', 1)
    elif mode == "class-list":
        anchor = "${VERDICT_CLASSES.join(', ')}"
        if text.count(anchor) < 1:
            raise SystemExit("class-list perturbation did not apply: the "
                             "interpolated class list was not found")
        # the eleven words, spelled out where the prompt interpolates them
        text = text.replace(
            anchor, "mutation-vacuous, harness, null-control, claims, version, "
                    "head-moved, carry-missing, root-cause-unanswered, "
                    "preflight-mismatch, conflict, other", 1)
    else:
        raise SystemExit(f"unknown perturbation {mode!r}")
    open(path, "w").write(text)


def main():
    argv = sys.argv[1:]
    perturb = argv[argv.index("--perturb") + 1] if "--perturb" in argv else "none"
    since = window_ref()
    tok, src = token()
    print(f"window ref (the commit before the window's oldest first-parent): {since}")
    print(f"credential source: {src} (read-only; this harness writes nothing)")

    base = tempfile.mkdtemp(prefix="d13-stats-")
    wt = os.path.join(base, "wt")
    p = git("worktree", "add", "--detach", wt, L.BASELINE_SHA)
    if p.returncode != 0:
        raise SystemExit(f"git worktree add failed: {p.stderr.strip()[:300]}")
    try:
        out0 = run_stats(wt, since, tok)
        classes0, rows0, block0, fric0, skip0 = parse(out0)
        print(f"\n[pinned tree] verdict grammar read: {classes0}")
        print(f"[pinned tree] verdict-class rows: {rows0}")
        print(f"[pinned tree] friction rows: {fric0}  enum-skipped line: {skip0}")
        print(f"[pinned tree] classes taught by the wave script: "
              f"{len(L_classes(wt))} {L_classes(wt)}")
        if perturb == "none":
            out1 = ""
        else:
            patch_wave(wt, perturb)
            print(f"\nperturbation {perturb}: {WAVE} edited in {wt}")
            out1 = run_stats(wt, since, tok)
        classes1, rows1, block1, fric1, skip1 = (
            parse(out1) if out1 else ([], [], [], 0, False))
        if out1:
            print(f"[perturbed]   verdict grammar read: {classes1}")
            print(f"[perturbed]   verdict-class rows: {rows1}")

        # the reviewer's block vocabulary, read off the wave script the same way
        # the CLI reads its verdict words: the CLASSES declarations.
        taught = L_classes(wt)
        L.result("verdict_grammar_classes", len(classes0))
        L.result("verdict_class_rows", len(rows0))
        L.result("verdict_class_rows_other_than_merge", len(block0))
        L.result("block_class_rows", len([b for b in block0
                                          if b not in ("blocked", "merge")]))
        L.result("classes_taught_by_wave_script", len(taught))
        L.result("friction_histogram_rows", fric0)
        L.result("stats_enum_skipped", int(skip0))
        if out1:
            L.result("perturbed_verdict_grammar_classes", len(classes1))
            L.result("perturbed_verdict_class_rows", len(rows1))
            L.result("perturbed_block_class_rows",
                     len([b for b in block1 if b not in ("blocked", "merge")]))
            L.result("delta_grammar_classes",
                     len(classes1) - len(classes0))
        L.result("perturbation", perturb)
    finally:
        git("worktree", "remove", "--force", wt)
        shutil.rmtree(base, ignore_errors=True)
    L.footer()


def L_classes(root):
    """`VERDICT_CLASSES` as the wave script declares it, read from the tree."""
    text = open(os.path.join(root, WAVE)).read()
    m = re.search(r"const VERDICT_CLASSES = \[([\s\S]*?)\]", text)
    if not m:
        raise SystemExit("VERDICT_CLASSES not found in the wave script")
    return [w for w in re.findall(r"'([^']+)'", m.group(1))]


if __name__ == "__main__":
    main()
