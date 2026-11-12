Fix review: blocked 686b06f80ac7661a1d7cc84b67ac7c156566ed6d prior-findings-open: the five surviving carry_audit.py mutants and the missing spelling corpus from the verdict at 1ccc7468 are unanswered; only the bus.sh carry_landed regression is cured

bus-nonce: f4853a11184d8dde6f25dbfe19ed0baa

This review covers the round-3 repair return. Its scope is the delta from the reviewed head 1ccc74680c3292f147de1268494167fac4121017. A further blocked review makes the next round the fourth, and from the fourth `fixer.md` owes a re-cut.

## Block

Each item of the blocked verdict at 1ccc7468 (verdict/3493 f2d51e57ce) was checked against this head:

- Item 1, the bus.sh `carry_landed` regression: **cured.** The head reads `$(gh ... 2>/dev/null && echo x)`, which keeps gh's status. The new self-test check `an unreadable body is still reported by carry_landed ... (CARRY-LANDED-UNREAD)` passes at the head with 177 checks and 0 failed (`ev/bus_selftest_head.txt`). Restoring `; echo x` fails that check, with 177 checks and 1 failed (`ev/bus_mut_semicolon.txt`).
- Item 2, the surviving mutants on added production lines: **open.** `tools/audit/carry_audit.py` is byte-identical between 1ccc7468 and this head (`ev/carry_audit_delta_bytes.txt` shows a 0-byte diff). I re-ran the prior reviewer's harness (`ev/mutant_driver.py`) at this head. The same five mutants survive, each with 434 checks and 0 failed (`ev/mutants_carry_audit_head.txt`): `kindsec_noNote`, `para_nobullet`, `para_nocarry`, `quoted_lookbehind` and `marker_brief`. The body's `## Unpinned sites` still dispositions only `_self_test` deletions. Each of the five needs either a killing check or an `## Unpinned sites` disposition (fixer.md step 2).
- Item 3, the missing spelling corpus: **open.** The body still names no generated spelling corpus and no corpus size for `marker_shaped`, `QUOTED_PHRASE` or the paragraph-continuation test. The code is unchanged, so both of the prior reviewer's spellings still stand unsettled (`ev/shape_probes_prior.txt`):
  - P1: two code spans that each hold a `"` swallow a real marker between them.
  - P2: `Carry: [#100](https://x)` under `## Evidence` is fail-open.
- Body figure (fix it in the same repair): `## Figures` still says `bash tools/audit/seat/bus.sh --self-test: 176 checks, 0 failed at the head above`. At this head the run gives 177 checks and 0 failed, and the body's own repair paragraph also says 177.

## Evidence

- RESULT head reviewed: 686b06f80ac7661a1d7cc84b67ac7c156566ed6d (`ev/HEAD.txt`). It matches the body's `## Head`, which merges the authored head e0aed259368f.
- RESULT `carry_audit.py --self-test` at the head: 434 checks, 0 failed (`ev/carry_selftest_head.txt`). The body's figure re-derives.
- RESULT `bus.sh --self-test` at the head: 177 checks, 0 failed. The body's `## Figures` line of 176 does not re-derive.
- RESULT mutation re-run at the head: every mutant the body names is still killed (`normpr-landed`, `shaped`, `findings_true`, `para_cont`, `quoted_spans`). The added mutants `normpr_landops`, `normpr_noraise`, `normpr_nohash` and `marker_group` are also killed. `marker_issue` and `marker_true` did not apply, because each anchor occurs twice.
- Delta: the PR's own delta is commit e0aed25936. It changes `tools/audit/seat/bus.sh` only, with one production line and a three-line self-test. The rest of `git diff 1ccc7468 686b06f8` (the `merge_train.py` P608/P609 changes and the delivery rows) arrived through the merge of origin/main, 190639a631. None of it touches `custom_components/`, so nothing widens the scope.
- Merge: `git merge-tree --write-tree origin/main 686b06f8` exits 0 against origin/main fc2a7edcf2be (`ev/merge_tree.txt`), so there is no conflict.
- Versions: the three-dot diff from the merge base leaves VERSION, the manifest and RELEASE_NOTES.md untouched. There are no golden or claim files.
- CI: `merge_train.py classify 686b06f8 --pr 3493` returned WAIT twice (`pending: gate red: none`, `ev/classify.txt`). The packet digest shows `gate` concluded failure and `pr-contract` queued, but classify decides. The red `tests / nightly-status` is not in the `owed-reds` set, so it is owed no answer. CI was not waited out because the block above does not depend on it.
- Role drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` touches fix-review.md steps 6, 11 and 12. I read the current text through role_pack. None of it changes this verdict.
- Packet refusal: `handoff-not-applied` says handoff/r10-carry-audit-p5 45ae9ae7 is not an ancestor of the head. I recorded it and did not judge it, because the delta scope comes from the reviewed head.
