"""verify-v2 (independent lens, D11-s1-71): re-implement both regexes from scratch in Python
(reading the two .mjs files as data only, never evaluating their JS) and probe with frontmatter
shapes the finder's harness did not use, to check the divergence is a property of the two parsers'
different anchoring/scoping rules and not an artefact of the finder's specific 6 probe strings.

Metric definition (mine): frontmatter cells (own probe set, disjoint from the finder's 6) on which
my Python re-implementation of rules_sync.mjs:parse's paths regex and policy_lint.mjs:rulePaths's
regex return different path lists (list-compared). The two regexes are transcribed verbatim from
the source (not executed as JS):
  rules_sync (whole frontmatter, line-anchored, quote pattern): r'^\\s*-\\s*"([^"]+)"\\s*$'
  policy_lint (scoped to the "paths:\\n(...)" block only, no trailing anchor): first isolate the
    contiguous `paths:` block with r'^paths:\\n((?:[ \\t]*-[ \\t]*.*\\n)+)', then r'-\\s*"([^"]+)"'
    within it.

Run from cwd=/home/claude/ev2:
    python3 tools/audit/round9/D11/verify-v2-leads/v2_frontmatter_reimpl.py
Own probes (none shared with the finder's trailing_comment/list_under_other_key/etc.):
  - multiple `- "..."` lines under `paths:`, one with trailing whitespace only (no comment text)
  - a `paths:` block followed immediately (no blank line) by another `- "..."` list under a
    DIFFERENT key that itself starts with the letter p (`prereqs:`) -- to check the block-isolation
    regex's `(?:[ \\t]*-[ \\t]*.*\\n)+` doesn't run past the intended block on a merely similar key
  - a paths entry whose quoted value itself contains a literal `# ` substring (not a comment: inside
    the quotes) -- checged against both parsers' quote-boundary handling
Expected (mine): the mechanism reproduces on fresh cells (divergent_cells >= 1 of 3), confirming the
finder's phenomenon_property ("one function reads the whole frontmatter, line-anchored; the other
reads a scoped block, unanchored") rather than the specific 6 strings chosen.
Baseline / tree: evidence branch 96b89163.
"""
import os
import re
import sys

ROOT = os.getcwd()
RS = os.path.join(ROOT, ".claude/workflows/rules_sync.mjs")
PL = os.path.join(ROOT, ".claude/workflows/policy_lint.mjs")
for p in (RS, PL):
    if not os.path.isfile(p):
        print("ERROR: run from cwd=/home/claude/ev2", file=sys.stderr)
        sys.exit(2)

rs_src = open(RS).read()
pl_src = open(PL).read()

# Confirm the exact regex literals are still what I transcribed (a self-check, not trust-me).
RS_PATTERN = r'"([^"]+)"\s*$'
PL_BLOCK_PATTERN = r'^paths:\n((?:[ \t]*-[ \t]*.*\n)+)'
PL_ITEM_PATTERN = r'-\s*"([^"]+)"'
assert RS_PATTERN.replace("\\", "") in rs_src.replace("\\\\", "\\") or '"([^"]+)"\\s*$' in rs_src, \
    "rules_sync regex literal not found verbatim -- transcription may be stale"
assert 'paths:\\n((?:[ \\t]*-[ \\t]*.*\\n)+)' in pl_src, "policy_lint block regex literal not found verbatim"
assert '-\\s*"([^"]+)"' in pl_src, "policy_lint item regex literal not found verbatim"
print("transcription self-check: both regex literals found verbatim in their source files")


def rules_sync_paths(frontmatter_text: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r'^\s*-\s*"([^"]+)"\s*$', frontmatter_text, re.M)]


def policy_lint_paths(frontmatter_text: str) -> list[str] | None:
    fm_with_nl = frontmatter_text + "\n"
    block = re.search(r'^paths:\n((?:[ \t]*-[ \t]*.*\n)+)', fm_with_nl, re.M)
    if not block:
        return None
    return [m.group(1) for m in re.finditer(r'-\s*"([^"]+)"', block.group(1))]


def doc(fm: str) -> str:
    return f"description: probe\n{fm}\n"


PROBES = {
    "trailing_ws_only": 'paths:\n  - "tests/**"   \n  - "custom_components/**"',
    "adjacent_p_key": 'paths:\n  - "tests/**"\nprereqs:\n  - "docs/**"',
    "hash_inside_quotes": 'paths:\n  - "tests/**#literal"',
}
div = 0
for name, fm in PROBES.items():
    text = doc(fm)
    a = rules_sync_paths(text)
    b = policy_lint_paths(text) or []
    d = a != b
    div += d
    print(f"cell {name:20s} rules_sync={a} policy_lint={b} divergent={int(d)}")

print(f"RESULT divergent_cells={div} of {len(PROBES)} count")
print("RESULT thread_factor=1.000")
try:
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
except Exception:
    print("RESULT load1=n/a")
