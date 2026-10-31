Fix review: merge 35b1ef2e52d3622f9aef104b6e76a32204b9a2dd

bus-nonce: b3d3729556f459a473d1e4090578314c

Round 1. Record PR (triage s8 batch 80, P317); the diff adds two files (delivery row, triage batch file) and no production code, so there is no mutant, golden, claim file, version or budget to check.

## Evidence
- Head measured: 35b1ef2e52d3622f9aef104b6e76a32204b9a2dd. CI via merge_train.py classify: GREEN, pending none, red none. Packet gate digest was pending at render; re-read live.
- merge-tree: git merge-tree --write-tree origin/main 35b1ef2e52d3622f9aef104b6e76a32204b9a2dd exits 0, no conflict.
- Cited sites re-read at origin/main: body_refusal called at review_packet.py:427, gh_comment.py:141, ci_probe.py:255 and 278; defined ref_privacy.py:300. All match.
- prepr.sh --body-check (1567-1600) runs privacy_line (1586), which is ref_privacy.py --check on refs and diff-added lines (prepr.sh:271-277); it never reads the body text. Matches the record.
- body_push.sh is at tools/audit/seat/body_push.sh: line 45 runs prepr --body-check, line 90 runs ref_privacy guard on ref and commits. Matches.
- R10-FLY-NO-FOOTERS exists in wave-r10-groups.json, size S, as the record says.
- carry_audit at the head: 0 finding items, 0 unrouted. figure_lint: 1 resolved, 1 not verified (a bare git grep, flags not checked), 0 refused.
- Not re-derived: seat-ledger.md:2325 (#2958), the held op b80-P317.txt, and #3024's c15dfa5a are not in the repository tree, so I could not confirm them; the ruling's logic does not depend on them beyond the two named instances.
- The ruling is narrow and consistent with the cited code: one call at the single step both writers pass, dispatch kept as backstop, no second call site.
