Fix review: merge f13ad4f6739d49ca45de197bea5f9f3d4a98e2af

bus-nonce: 01ffa1d43183358794c8a6d314d412bb

## Round

Round 1, record-shaped (roster batch 20). Measured at head f13ad4f6739d49ca45de197bea5f9f3d4a98e2af from a detached worktree at that SHA; `git ls-remote origin refs/pull/2861/head` printed it at the start and again before writing, so the head did not move. Merge base 2563e29228a9c2b075afed4f13b89839fcc281b2 (batch 19, #2857). origin/main was 1f82fee49addbffa3388248f66e3f9f4482daed5 at the reading; `git diff <merge base>...origin/main -- dev/governance/roles/` is empty, so the contract read is current. All diffs three-dot.

## RESULT lines

- RESULT diff: `git diff 2563e2922...HEAD --name-only` prints exactly `dev/programme/delivery/2861.md` and `dev/programme/rosters/wave-r10-groups.json`. VERSION, the manifest, RELEASE_NOTES.md and both claim files untouched (0 paths).
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` (origin/main 1f82fee49) exits 0, tree 98cb652345de8c6897051d4c6e31bdadb0674163; no driver marker.
- RESULT groups: origin/main 197, merge base 197, head 199; added exactly R10-ERREXIT-COUNTERMEASURES and R10-RECORD-API-O1, none removed (ev/counts.txt). Only five existing groups change, and only in `carry`/`resume`: R10-CARD-VOICE carry 6 -> 0, stage not-started -> done; R10-COP-GATE carry 10 -> 11; R10-UX-HEALTH carry 15 -> 16; R10-HOTFIX-BATCH-ERREXIT carry 1 -> 0 (stage already done); R10-LEGIONELLA-COMPLETION stage queued -> done, carry 0. No top-level key changes. JSON loads.
- RESULT merged-by-ref: `git merge-base --is-ancestor <c> origin/main` true for e0ffb12130436f1cef00e770aed436ac8b4f067e (#2848), 75ac453534e10c0a6ef88533ad5ff375cd6ca333 (#2841), 510787b769407ed25054177cfb0f6bd17e041e0e (#2832, the LEGIONELLA set-stage done) and 63b1cfd03 (batch 19 head); each is also an ancestor of this head.
- RESULT done-before-reroute: R10-LEGIONELLA-COMPLETION held 0 carries. R10-CARD-VOICE's six carries were dropped in c3fbc7407..052968159 before set-stage c8d51c464; each checked against #2841's diff (`git diff 75ac45353^1 75ac45353`): H1 `+const DIALOG_FONT_PX_MIN = 14;` and 22 added `max(12px` lines; H2 27 added `aria-hidden` lines; H3 6 added `font-weight: 600`; H4 `560px` x2 and `overflow-x` x2; the three corrections `hpo-text-sm, 13px` x3 and `+const DIALOG_FONT_PX_MAX = 18;`; the drift-states carry `savings_page`, `savings_empty`, `health_page`, `setup_not_published`, `advisor_empty` added to tests/card_drift.mjs. R10-HOTFIX-BATCH-ERREXIT carry 1 against #2848: nightly.yml `batch=0` then `... --event "$EVENT" || batch=$?`, the bare `batch=$?` removed. This is a grep presence check per carry, not a re-measurement of the card's px figures.
- RESULT ERREXIT carries: the four carries joined by a space are byte-identical to the "exact carry text" quoted in #2849's body `## Forward-carry` (True).
- RESULT RECORD-API-O1 carries: each of the three, less its `From #2852 (...)` prefix, is byte-identical to the corresponding item of merged #2852's final `## Forward-carry`, less its trailing `Carry:` marker (3 of 3 True, ev/cmp2852.txt). Carry 3's rewording, read against its first version at 9573269b1: the cited path of the root-cause role contract became "the root-cause role contract", the CI runner's home literal became "the CI runner account's home", and a literal host path under the root account's home became "a real host path under the root account's home". Meaning unchanged: the defect (no path-segment boundary on the home match), the measured refusal (`dev/audit/rca/ratelimit-recur.md:7`, `1 refused`), the control (`0 refused` with the home patched to the runner's) and the fix's constraint all survive.
- RESULT COP-GATE / UX-HEALTH: each appended carry, less its `From #2854 (R10-HEAT-METER), review probe/rev-2854-084d74e7: ` prefix, is found verbatim inside #2854's `## Forward-carry` quoted Text (2 of 2 True, ev/cmp2854.txt); those are the two texts probe/rev-2854-084d74e7 (92207b841) blocked carry-missing on. Earlier carries of both groups are an unchanged prefix.
- RESULT carry_audit, head roster (`python3 -I tools/audit/carry_audit.py --roster-ref HEAD pr N`): #2849 `3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)` rc 0; #2852 `4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)` rc 0. Null: #2849 against the merge-base roster prints `2 routed, 0 unrouted, 1 bad destination(s)` rc 1, so the head roster is what routes it.
- RESULT ERREXIT brief: against the orchestrator's draft group the only differing field is `brief`, and the only difference is the inserted `(at e1a684789) ` after the harness path; the brief is unchanged since its append-group commit 5651cab9a. The harness exists at e1a684789 and not in the head tree. Null: deleting ` (at e1a684789)` makes `node tools/policy/brief_lint.mjs <roster>` print 2 ERRORs (`path: dev/audit/harnesses/r10_errexit_capture.py` and `path: r10_errexit_capture.py`: "not in the tree, and not present at its cited tag ref(s) [e0ffb1213, e78cd811]"), rc 1, so the tag is load-bearing.
- RESULT roster lint: `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` prints `TOTAL: 0 error(s) across 1 file(s)`, rc 0, with the head's linter and with origin/main's linter (1f82fee49), the copy roster_edit.py's gate uses.
- RESULT brief_lint (no argument, at the head): rc 0, `TOTAL: 0 error(s) across 48 file(s)`. The ERROR lines it prints are all under its fixture self-tests (`tools/policy/fixtures/`, e.g. W1-G2..W1-G14 in wave-1b-931dffe.json, count-drift.json, carry-990003/990004.json), which the self-tests expect to fail.
- RESULT ref_privacy: `python3 -I tools/audit/seat/ref_privacy.py --check` at the head: `29 line(s) added since 2563e29228a9 judged, 0 refused`, rc 0. The instrument judges 29 of the 104 added lines; my own grep of all 104 added lines for a home-directory path or account name finds 0.
- RESULT CI: the head's check-runs API lists 55 runs: 36 success, 19 skipped, 0 failure; `gate`, both `pr-contract / pr-contract`, `tests / briefs`, `governance / delivery-status` are success. No red check, so no root-cause answer is owed; the body's "Red checks" saying the seat did not read them is moot at this head.
- RESULT body head: the body's `## Head` names f13ad4f6739d49ca45de197bea5f9f3d4a98e2af, the head measured.

## Non-blocking notes

- #2849 and #2854 are OPEN at this reading; the appended ERREXIT group and the COP-GATE/UX-HEALTH carries cite them, not a merged PR. That is the order finding-propagation.md requires (a carry lands before its producer merges), and the brief's "merged ruling" reads on the drop and set-stage ops, all of which cite merged PRs. Carry: dismissed: the carry-before-producer order is the rule, not a defect
- R10-LEGIONELLA-COMPLETION and R10-CARD-VOICE are set done with `resume.next_step` still reading "dispatch a fixer" / "dispatch a fixer at the owner's chosen design ..."; set-stage changes only `stage`. A stale next_step on a done group dispatches nothing. Carry: dismissed: a done group is not dispatched or linted, and set-stage's single-field scope is roster_edit.py's design

## Not re-derived

- The six CARD-VOICE carries are checked by the presence of their landing lines in #2841's diff, not by re-measuring the px and contrast figures; #2841's own review covered those.
- No mutation proof: the diff writes no production line, so no mutant is drawn.

## Evidence

ev/ in this probe commit: counts.txt, cmp2852.txt, cmp2854.txt, carry_audit_2849.txt, carry_audit_2852.txt, carry_audit_2849_null_mb.txt, ref_privacy.txt, brief_lint.txt, roster_lint_head.txt, roster_lint_mainlinter.txt, roster_lint_null_noat.txt, checks.txt, HEAD.txt (host paths scrubbed to `<HOME>`).
