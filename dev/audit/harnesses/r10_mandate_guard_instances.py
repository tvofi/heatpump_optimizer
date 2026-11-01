#!/usr/bin/env python3
"""R10-FLY-MANDATE-REVOKE-GUARD: the two field instances, replayed against a tree.

    python3 dev/audit/harnesses/r10_mandate_guard_instances.py <tree root> guard <scratch dir>
    python3 dev/audit/harnesses/r10_mandate_guard_instances.py <tree root> score

guard: #201 comment 6546832523 as first posted (read from the API's edit
history, so no copy of the text is kept here), and the same text with the
group's name replaced, each handed to the tree's
`gh_comment.py post --dry-run` for #201. One line per body:
`RESULT body=<field|field-without-word> rc=<rc> last=<its last line>`.
Defect present: the field text exits 0. Fixed: it exits 2 (REFUSED) and the
null body exits 0. The fixed tree reads the live #201 thread for its grants.

score: #3045's round-1 head b02ffd17 against the base a7dd7f50d, with its
body's claimed figure and the true one, through the tree's gate.
`RESULT claim=<figure> measured=<score.py's line or None> accepted=<bool>`.
Defect present: both claims are accepted with nothing measured. Fixed: the
claim the scorer does not print is refused and the true one accepted.
"""
import json
import os
import subprocess
import sys

COMMENT = 6546832523
BASE, HEAD = "a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0", "b02ffd170d5049d8869689cbc889a5cf46097a1e"
GROUP = "R10-FLY-MANDATE-REVOKE-GUARD"
SEC = "## Summary\n\nx\n\n## Raise justification\n\nPayments tried: x\n{line}\n\n## Tests\n\nx\n"


def first_text() -> str:
    node = (subprocess.run(
        ["gh", "api", f"repos/tvofi/heatpump_optimizer/issues/comments/{COMMENT}", "--jq", ".node_id"],
        capture_output=True, text=True, check=True).stdout.strip())
    q = ('query($id:ID!){node(id:$id){... on IssueComment{userContentEdits(first:20){nodes{editedAt diff}}}}}')
    out = json.loads(subprocess.run(["gh", "api", "graphql", "-f", f"query={q}", "-f", f"id={node}"],
                                    capture_output=True, text=True, check=True).stdout.strip())
    edits = out["data"]["node"]["userContentEdits"]["nodes"]
    return min(edits, key=lambda e: e["editedAt"])["diff"]


def main(argv):
    root, arm = os.path.abspath(argv[0]), argv[1]
    sys.path.insert(0, os.path.join(root, "tools/policy"))
    os.chdir(root)
    import budget_raise_gate as g
    if arm == "score":
        for claim in ("Architecture score: dS +0.0012 IMPROVES", "Architecture score: dS +0.0000 NULL"):
            body = SEC.format(line=claim)
            if hasattr(g, "measured_score"):
                measured = g.measured_score(BASE, HEAD)
                ok, _ = g.justified(body, lambda: measured)
            else:
                measured, (ok, _) = None, g.justification(body)
            print(f"RESULT claim={claim.split('dS ')[1]!r} measured={measured!r} accepted={ok}")
        return 0
    text = first_text()
    if GROUP not in text:
        print(f"RESULT precondition: the first text does not name {GROUP}; the instance is not this one")
        return 1
    os.makedirs(argv[2], exist_ok=True)
    for label, t in (("field", text), ("field-without-word", text.replace(GROUP, "the mandate guard's group"))):
        f = os.path.join(argv[2], f"{label}.md")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(t)
        r = subprocess.run([sys.executable, "tools/pr/gh_comment.py", "post", "--repo", g.DEFAULT_REPO,
                            "--issue", str(g.MANDATE_ISSUE), "--body-file", f, "--dry-run"],
                           capture_output=True, text=True)
        last = (r.stdout + r.stderr).strip().splitlines()[-1]
        print(f"RESULT body={label} rc={r.returncode} last={last[:40]!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
