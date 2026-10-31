Fix review: merge c67b85385aa18245575d6722e939939ec62a0c89

bus-nonce: c25c1688878966d29c402c92d5b1e913

Round 1. Record PR (triage s8 batch 88, P325 REJECT). Diff vs merge base: two new files, `dev/programme/triage/s6-batch88.md` and `dev/programme/delivery/3035.md`; no production code, no budget, claim file, VERSION or closure touched, so steps 1-5 and 14 have nothing to move.

## Findings

- Figure (e) names no enumerator: the ruling defines V and H but commits no script, and my own enumeration (ev/enumeration-class.txt, ev/ definitions below) gives 228 / 27 / 148 / 6 / 9, not 231 / 12 / 153 / 9 / 7. The direction (context-only is a small minority, ~1% of merges) and the REJECT hold either way, so this does not block, but the exact figures are not reproducible from the tree. Carry: dismissed: the ruling's conclusion survives every definition tried (6 to 9 of ~230 merged PRs, none after 10-24 except #3014); the probe is a one-off triage measurement and the ruling's own caveat says the 7 "real" rows may include claim-file rows.

## Evidence

- Head measured: c67b85385aa18245575d6722e939939ec62a0c89 (ev/HEAD.txt). Contract diff of dev/governance/roles/ against merge base: empty.
- (a) P17 at roster group R10-FLY-CARRY-DOC-CONTEXT (`dev/programme/rosters/wave-r10-groups.json`, S, `tools/pr/app_approve.sh`): brief reads "a context-only line difference introduced by main carries in *.md files ... code files strict. Fixture controls: md-context yes / py-context no / +line no." Confirmed.
- (b) `tools/pr/app_approve.sh:390` at origin/main 4822c8f9b: `norm()` is `sed -e '/^index /d' -e 's/^@@ .*/@@/'`, so offsets and function line are dropped. Confirmed; line number exact.
- (c) #3014 (42b228ec to c41c4053), diffed myself: `tests/closure.py` context lines `"DISCLAIMER.md"` / `blueprints/...yaml` against comment lines; `tests/doc_claims.py` context `check_image_dimensions()` / `check_doc_wiring()` against `check_marker_census()` / `check_card_figures()`. Confirmed as stated.
- (d) range-diff `=` for merge-forwards: consistent with git's behaviour (it compares branch commits' patches, not the merged tree); not re-run per head.
- (e) Own enumerator: merge commits on origin/main first-parent since 2026-10-17 (579); V = 40-hex in the subject of the `origin/verdict/<N>` tip (418 have one), H = `<merge>^2`. Classes: V=H 228; branch-own non-merge commits in V..H not reachable from `<merge>^1` 27; merges only, `norm()`-equal 148; differing only in context lines (change lines `+`/`-` byte-equal) 6 (#2669 #2622 #2585 #2558 #2444 #2368); real change-line difference 9. Of the ruling's 9 context-only PRs, 6 reproduce; #2589 and #2577 show branch-own commits under my definition and #2584 a real difference. Unreproduced by me: the ruling's own probe script.
- (f) Re-open trigger (5 or more delta reviews of context-only code heads finding nothing) is stated and checkable.
- Merge with origin/main: `git merge-tree --write-tree` exit 0, clean (ev/merge-tree.txt).
- Packet: carry_audit 0 findings; figure_lint 2 resolved, 0 refused; no refusals.
- CI: `merge_train.py classify` exit 0, GREEN at the head (pending: none, red: none), after waiting through the in-progress prelude, coverage and instrument-self-tests runs. Head still the PR head at posting.
