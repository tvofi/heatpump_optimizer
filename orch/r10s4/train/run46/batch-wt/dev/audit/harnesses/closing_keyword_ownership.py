#!/usr/bin/env python3
"""The closing-keyword ownership rule, and every seam it returns on preflight.sh.

`tools/pr/preflight.sh` arm 1b refuses a body where ONE closing keyword names
SEVERAL references: GitHub's rule is KEYWORD #N -- the number follows the
keyword with nothing between them -- so a second reference under the same
keyword has no keyword of its own and is silently never closed. The arm's first
version spelled three separators (whitespace, a comma, an "and"); the round-1
review of #2342 ran the class's own rule over 200 merged bodies and returned six
more seams that version let through. This harness IS that rule, made runnable.

THE RULE, stated once here and implemented independently of the awk in the
script -- agreement between the two implementations is what this measures:

    a closing keyword OWNS AT MOST ONE REFERENCE. Count the closing-keyword
    sites (KEYWORD [:] WS REF) and the references in one CLAUSE; the clause
    carries an unowned reference -- a seam -- when it has at least one site and
    more references than sites. A clause is a sentence inside a paragraph: a
    blank line ends one, and so does `.`, `!` or `?` followed by whitespace.

CLAUSE SCOPE IS THE RULE, NOT A CONCESSION. The same test over the WHOLE BODY
returns 25 seams on the 200-merged-PR corpus, and every one carries its second
reference in a LATER clause: a `Part of #N.` / `Leaves #N open.` site -- the
tree's own convention for "closes one, touches another", and the opposite of a
close in the second case -- or a prose mention after a blank line or a sentence
end. A body-wide rule refuses bodies that are correct, which `preflight.sh`'s own
section 5 refuses to do. `--corpus` prints both counts so the two scopes can be
compared on real input rather than argued about.

WHAT IT RUNS, per shape: the rule's verdict, the script's exit code, and arm
1b's own REFUSE line. A seam the rule returns that the script does not refuse is
`seams_open`; a refusal the rule does not call a seam is `refused_but_not_seam`.
Both must be 0. The script runs from a directory that is not a checkout -- arm
1b is a property of the body text alone, and the policy-corpus arm it skips
there is a `check`, never a refusal -- and the intended list declares both
numbers, so the exit code attributes to arm 1b alone.

    python3 dev/audit/harnesses/closing_keyword_ownership.py
    gh pr list --state merged --limit 200 --json number,body > /tmp/bodies.json
    python3 dev/audit/harnesses/closing_keyword_ownership.py --corpus /tmp/bodies.json

NULL CONTROLS. `--script <path>` runs the same matrix against another copy:
against the round-1 head (`git show 5c35cd9ba:tools/pr/preflight.sh`) the six
separator seams each exit 0 and `seams_open` reads 6, so a head run printing 0
is measuring the script rather than this table. And `NOT_OWNED` runs the other
direction -- shapes the rule returns NO seam for, which a rule widened into the
whole body would refuse.

RESULT seams_open=0
RESULT refused_but_not_seam=0
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

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
DEFAULT_SCRIPT = ROOT / "tools/pr/preflight.sh"

REF = r"(?:https?://[^ ]*/issues/|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#|GH-|#)[0-9]+"
KW = r"(?:\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b)"
SITE = re.compile(rf"{KW}\s*:?\s+{REF}", re.I)
ANY_REF = re.compile(REF, re.I)
CLAUSE_END = re.compile(r"[.!?]\s+")
# The arm's own line, in either spelling: the SEPARATOR TEST is the exit code
# below (the intended list declares both numbers, so with arm 1b gone these
# bodies exit 0), and this is the cross-check that the refusal came from arm 1b
# rather than from another arm.
ARM_LINE = re.compile(r"several (?:references in one clause|issues)")

# The twelve instances the round-1 reviewer's rule returned (evidence/class-probe.txt
# at review/2342). Eleven of them are the six seams; the last two are the shapes
# whose scope this harness argues for, kept beside them so the difference is
# visible rather than asserted.
REVIEWER = [
    ("whitespace", "Closes #2231 #2230."),
    ("comma", "Closes #2231, #2230."),
    ("and", "Closes #2231 and #2230."),
    ("slash", "Closes #2231/#2230."),
    ("spaced-slash", "Closes #2231 / #2230."),
    ("ampersand", "Closes #2231 & #2230."),
    ("plus", "Closes #2231 +#2230."),
    ("paren", "Closes #2231 (#2230)."),
    ("semicolon", "Closes #2231; #2230."),
    ("word-then", "Closes #2231 then #2230."),
    ("word-twice", "Closes #2231 twice #2230."),
    ("newline", "Closes #2231\n#2230"),
    ("site-split-across-lines", "Closes\n#2231 / #2230"),
]

# Generated, not listed by hand: every printable ASCII separator, every
# connector word a body might use, and the layouts a wrapping editor produces.
PUNCT = ["!", '"', "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", "/", ":",
         ";", "<", "=", ">", "?", "@", "[", "]", "^", "_", "`", "{", "|", "}",
         "~", "\\", "..", "->", "=>", "|", "//",
         "\u2192", "\u2014", "\u00b7", "\u2026", " \u2192 "]
WORDS = ["and", "also", "plus", "then", "twice", "along", "with", "via", "per",
         "covering", "namely", "i.e.", "viz", "too"]
LAYOUTS = ["#2230", "\n#2230", "\t#2230", "\n\n\n#2230", "\r\n#2230",
           "\n  #2230", " \n #2230", "\nand #2230", "\nand\n#2230",
           " and\n#2230"]
# The four reference forms the first arm pins, and the keyword's spellings and
# casings: a seam is a seam whichever form the second reference takes.
FORMS = ["GH-2230", "gh-2230", "tvofi/heatpump_optimizer#2230",
         "https://github.com/tvofi/heatpump_optimizer/issues/2230"]
KEYWORDS = ["CLOSES #2231 #2230.", "closes #2231 #2230.", "Closes: #2231 #2230.",
            "Fixed #2231 #2230.", "resolves #2231 #2230.",
            "Fixes #2231, #2230.", "Resolved #2231 and #2230.",
            # The casing rows that matter: these separators are the ones the
            # round-1 separator list already refused, so a case-sensitive
            # keyword class would leave them looking covered while the second
            # reference escaped -- the arm is `-i` like check 1's grep or it is
            # not the same rule.
            "CLOSES #2231; #2230.", "Resolved #2231 -> #2230.",
            "FIXED #2231 / #2230."]

# Shapes the rule returns NO seam for. A rule that counted references across the
# clause end -- or refused any body holding two references -- would red every one
# of these, so they are the scope's null control and the arm's own.
NOT_OWNED = [
    ("one-keyword-one-reference", "Closes #2231."),
    ("part-of", "Closes #2231.\n\nPart of #2230."),
    ("leaves-open", "Closes #2231. Leaves #2230 open."),
    ("superseded-by", "Closes #2231. #2230 is superseded by it."),
    ("two-keywords-one-clause", "Closes #2231 and fixes #2230."),
    ("two-keywords-next-line", "Closes #2231.\nCloses #2230."),
    ("no-keyword-two-refs", "See #2231 and #2230 for context."),
    ("bare-reference-paragraph", "Closes #2231.\n\n#2230"),
    ("across-a-sentence", "Closes #2231. #2230."),
    ("heading-then-reference", "Closes #2231\n\n## Notes\n\n#2230 is unrelated."),
    ("prose-mention", "Closes #2231. The report in #2230 was unrelated."),
]

def clauses(body: str, whole_body: bool = False) -> list[str]:
    """The body's clauses, or one clause when the scope is the whole body."""
    if whole_body:
        return [" ".join(body.split())] if body.strip() else []
    out: list[str] = []
    for para in re.split(r"\n[ \t]*\n", body):
        if not para.strip():
            continue
        joined = " ".join(para.replace("\r", "").split())
        if not joined:
            continue
        parts = CLAUSE_END.split(joined + " ")
        out.extend(p.strip() for p in parts if p.strip())
    return out


def seams(body: str, whole_body: bool = False) -> list[str]:
    """The clauses where a closing keyword owns more than one reference."""
    found = []
    for clause in clauses(body, whole_body):
        sites = len(SITE.findall(clause))
        if sites and len(ANY_REF.findall(clause)) > sites:
            found.append(clause)
    return found


def arm_rc(script: Path, body: str, tmp: str) -> tuple[int, bool]:
    """(exit code, arm 1b printed its refusal line) for one body."""
    p = subprocess.run(
        ["bash", str(script), "2231", "2230"],
        input=body, capture_output=True, text=True, cwd=tmp,
    )
    return p.returncode, bool(ARM_LINE.search(p.stdout))


def matrix(script: Path) -> list[dict]:
    shapes: list[tuple[str, str]] = []
    shapes += REVIEWER
    shapes += [(f"punct:{c}", f"Closes #2231 {c} #2230.") for c in PUNCT]
    shapes += [(f"word:{w}", f"Closes #2231 {w} #2230.") for w in WORDS]
    shapes += [(f"layout:{i}", f"Closes #2231{s}") for i, s in enumerate(LAYOUTS)]
    shapes += [(f"form:{f}", f"Closes #2231 / {f}.") for f in FORMS]
    shapes += [(f"keyword:{i}:{k.split()[0]}", k) for i, k in enumerate(KEYWORDS)]
    shapes += [(f"not-owned:{n}", b) for n, b in NOT_OWNED]
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, body in shapes:
            rule = bool(seams(body))
            rc, printed = arm_rc(script, body, tmp)
            rows.append({
                "shape": name, "body": body, "rule_seam": rule,
                "rc": rc, "arm_line": printed,
            })
    return rows


def summarise(rows: list[dict], script: Path, label: str) -> int:
    open_seams = [r for r in rows if r["rule_seam"] and r["rc"] != 1]
    over = [r for r in rows if r["rc"] == 1 and not r["rule_seam"]]
    ungated = [r for r in rows if r["arm_line"] and r["rc"] == 0]
    print(f"== {label}  ({script})")
    for r in rows:
        want = "seam" if r["rule_seam"] else "pass"
        got = "REFUSED" if r["rc"] == 1 else "passed"
        mark = "  " if (r["rule_seam"] == (r["rc"] == 1)) else "XX"
        print(f"  {mark} {r['shape']:28} rule={want:5} script={got:8} rc={r['rc']}"
              f"  {r['body']!r}"[:150])
    print(f"  RESULT shapes={len(rows)}")
    print(f"  RESULT seams_open={len(open_seams)}"
          f" {' '.join(r['shape'] for r in open_seams)}")
    print(f"  RESULT refused_but_not_seam={len(over)}"
          f" {' '.join(r['shape'] for r in over)}")
    print(f"  RESULT refusal_not_gating={len(ungated)}")
    return 1 if (open_seams or over or ungated) else 0


def corpus(path: Path) -> int:
    prs = json.load(open(path))
    clause_rows, body_rows = [], []
    for pr in prs:
        body = pr.get("body") or ""
        if seams(body):
            clause_rows.append(pr["number"])
        if seams(body, whole_body=True):
            body_rows.append(pr["number"])
    only_body = sorted(set(body_rows) - set(clause_rows))
    print(f"== corpus {path}  ({len(prs)} merged bodies)")
    print(f"  RESULT corpus_clause_scope={len(clause_rows)} {clause_rows}")
    print(f"  RESULT corpus_whole_body={len(body_rows)}")
    print(f"  RESULT whole_body_only={len(only_body)} {only_body}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--script", default=str(DEFAULT_SCRIPT),
                    help="the preflight.sh under test (default: this tree's)")
    ap.add_argument("--corpus", help="a `gh pr list --json number,body` file")
    a = ap.parse_args()
    rc = 0
    if a.corpus:
        rc |= corpus(Path(a.corpus))
    else:
        script = Path(a.script)
        if not script.is_file():
            print(f"no script at {script}")
            return 1
        rc = summarise(matrix(script), script, "ownership matrix")
    return rc


if __name__ == "__main__":
    sys.exit(main())
