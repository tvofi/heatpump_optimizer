Fix review: merge cc78cc831ea51cd98f14fb7cce96001cd108fb55
bus-nonce: 7ead16cd2d786a87c765b810fc9a29c7

# Fix review — PR #2870 (R10-ORCH-REVIEW-PACKET), round 2, head cc78cc831ea51cd98f14fb7cce96001cd108fb55

Round 2 reviews **the repair and the merge**, not the group. Detached worktrees
at `~/hpo-seats/review-2870-r2/wt` (head) and `~/hpo-seats/review-2870-r2/base410`
(round 1's head, `410d3988`), merge base `34cd75bf1fe506334611ba6c074c223317370e67`,
three-dot reads. The head was the PR head when the review started and when this
was posted; it did not move.

## The two reds, re-run at both ends

- At the head: `python3 -I tools/audit/seat/selftest_wiring.py --check` →
  `selftest_wiring: 99 self-testing, 99 wired, 0 unwired`, rc 0 (real 0.18);
  `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` →
  `cloud_dispatch self-test: 77 checks, 0 failed`, rc 0 (real 21.72).
  Carry: dismissed: both re-run green
- At `410d3988` the same two commands reproduce round 1's reds exactly:
  `UNWIRED tools/audit/seat/review_packet.py: no workflow run line names its
  self-test`, `98 self-testing, 97 wired, 1 unwired`, rc 1; and
  `Refusal: bus.sh dispatch refused: review_packet: REFUSED git merge-base
  origin/main <synthetic head>: fatal: Not a valid commit name`, rc 1.
  Carry: dismissed: round 1 reproduced
- CI at the head agrees, and the wiring step **ran**, not merely read: job
  `122309519259` (`governance / instrument-self-tests`) success, its "Show the
  review packet refusing its own fixtures" step success; latest `gate`
  `122330797512` success; `pr-contract / pr-contract` `122330330409` success.
  Carry: dismissed: CI green at head

## The REFUSE / UNAVAILABLE split — both arms, live

Driven through the **real** `bus.sh dispatch` and the **real** renderer, in a
scratch repo (`~/hpo-seats/review-2870-r2/live/seat`) whose `origin/main`
resolves to its head and which carries its delivery row; state under a scratch
`HPO_BUS_STATE`.

- REFUSE: `dispatch 7 <head> r1 --harness-file inside_harness.py` (inside the
  tree) → render rc 1 `review_packet: REFUSE independence: --harness-file is
  inside the tree; name it by --harness`; dispatch rc 1; `$S/dispatched`
  absent; no packet named. **Records nothing.**
  Carry: dismissed: recorded nothing
- UNAVAILABLE, failing `gh`: render rc 3, dispatch rc 0, one record
  `7 <head> reviewer2 <nonce>`, output `bus: review-packet: unavailable --
  review_packet: UNAVAILABLE: gh api repos/o/r/pulls/7: gh: auth required`.
  **Records and proceeds.**
  Carry: dismissed: recorded and proceeded
- UNAVAILABLE, working directory outside a checkout (real renderer through a
  wrapper): render rc 3, dispatch rc 0, recorded, `review-packet: unavailable --
  review_packet: UNAVAILABLE: the working directory is not inside a git
  checkout`.
  Carry: dismissed: recorded and proceeded
- UNAVAILABLE, no pinned interpreter under a scratch `HOME`: dispatch rc 0,
  recorded, `unavailable -- python3: no pinned interpreter …`.
  Carry: dismissed: recorded and proceeded
- Positive arm: `review_packet.py render --pr 2870 --head <head>` in the real
  checkout with real `gh` → rc 0, `## Refusals none`, `## Gate digest: green`,
  1248 lines / 70333 bytes, real 114.93. Round 1's F4 self-refutation is gone.
  Carry: dismissed: packet renders clean
- My mutation on the load-bearing line: `main`'s `except Unavailable → print
  UNAVAILABLE, return 3` replaced by `print REFUSE unavailable, return 1`.
  `review_packet.py --self-test` → `31 checks, 1 failed`, the named FAIL
  `UNAVAILABLE: a working directory outside a checkout exits 3, not 1, and
  writes nothing`; and the live outside-checkout arm flips to dispatch rc 1,
  refused, `$S/dispatched` absent — the #2870 regression shape. Restored
  byte-identical (sha256 `a209f923…`). Null control: the same live arm on the
  unmutated tree is rc 0 and records.
  Carry: dismissed: mutant killed
- The body's `repo()` mutant re-run: `review_packet.py --self-test` →
  `31 checks, 1 failed`, FAIL `repo(): a git read runs in the checkout the
  working directory is in, not the tool's install`. `cloud_dispatch.py
  --self-test` stays `77 checks, 0 failed` under it, and that is the repair
  working, not a gap in the arm: an install-path read now degrades to
  UNAVAILABLE instead of breaking the dispatch. Restored byte-identical.
  Carry: dismissed: mutant killed

## Round 1's "unclassified new file" arm

- `closure.orphan_files()` prints `0` at the head **and** at `410d3988`.
  Carry: dismissed: arm does not reproduce
- `closure.is_inert()` is `True` by prefix for both new files
  (`tools/audit/seat/review_packet.py`, `dev/audit/harnesses/r10_review_gather_share.py`)
  at both heads.
  Carry: dismissed: classified at both heads
- The classification is `tests/closures.json`'s `inert_reads` pair —
  `tests/entities.py: tools/audit/seat/review_packet.py`,
  `tests/harness_headers.py: dev/audit/harnesses/r10_review_gather_share.py` —
  identical at both heads.
  Carry: dismissed: the real classification
- Round 1 did not block on an unclassified file: its F6 was **non-blocking**
  and itself states that `inert_reads` pair. Its block 1
  (`root-cause-detectable`) is the two reds, and both reproduce at `410d3988`.
  So the report that round 1's block was mis-specified is itself the
  mis-specification; the measurements behind it are right.
  Carry: dismissed: round 1 reproduced

## Merge, scope, and the untouched files

- `git merge-tree --write-tree origin/main HEAD` exits 0 (tree
  `b889b4e8e851ef8fe0ae7096746024f14775d6c9`) against `origin/main`
  `4db1d3e28`; no conflict; both claim files are byte-identical to the merge
  base. `mergeStateStatus: BLOCKED` is the draft/approval state, not a conflict.
  Carry: dismissed: merges cleanly
- The seven non-merge commits in `410d3988..cc78cc831` touch only
  `tools/audit/seat/review_packet.py`, `bus.sh`, `cloud_dispatch.py`,
  `tools/pr/ci_predict.py`, `INSTRUMENTS.md` and
  `.github/workflows/governance.yml`. The branch's own nine paths are
  byte-identical between the code head `5936aab2f` and the merge head;
  `closures.json` and `INSTRUMENTS.md` differ from it only by main's
  `plan_audit.py` additions, with the branch's entries still present.
  Carry: dismissed: scope holds
- `VERSION`, the manifest version, `RELEASE_NOTES.md`, both claim files, the
  structure and mutation budgets, the mutation ledger and every golden fixture
  are untouched by the three-dot diff.
  Carry: dismissed: nothing moved

## `## Red checks` against the head's real runs

- The head's 55 check runs contain no failure. The three red contexts the body
  answers are real and are at `410d3988`: `gate` job `122012634486`,
  `governance / instrument-self-tests` job `122007070159` (two failing steps)
  and `pr-contract / pr-contract` job `122012407506`; each is named in the body
  with a cheaper detector, its standing cost and a process state. The head's
  `pr-contract` run (started 16:46:37Z, after the body's last edit at
  16:10:10Z) is green, which is the body's acceptance.
  Carry: dismissed: answered and green

## Non-blocking findings

- Non-blocking: the body's figures are stale after the main merge. It quotes
  `selftest_wiring: 98 self-testing, 98 wired, 0 unwired` twice; at this head
  the same command prints `99/99/0` (main added
  `tools/audit/seat/plan_audit.py`). It states the three-dot merge base is
  `484d9902` and origin/main's tip `524c1896b`; at this head they are `34cd75bf1`
  and `4db1d3e28`, and the predictor figure "against 484d9902" now reads
  against `34cd75bf1`. Its `## Head` also still carries the previous head's
  `e82f4d23` paragraph. The conclusions survive (0 unwired; diffstat `10 files
  changed, 891(+), 14(-)`, re-derived), but re-take the figures and drop the
  stale paragraph.
  Carry: R10-ORCH-REVIEW-PACKET
- Non-blocking: the body calls `dev/audit/harnesses/r10_review_gather_share.py`
  "the reviewer gather-share measurement the body's figure comes from", but the
  body quotes no gather-share figure any more (round 1's 49% was removed as
  unre-derivable). The file is honestly labelled as the fixer's own in its
  docstring and is inert; either quote the figure with its re-measurement
  instruction or drop the file and the sentence.
  Carry: R10-ORCH-REVIEW-PACKET

## Numbers re-derived, and the one I could not

- Re-derived at this head: `review_packet.py --self-test` 31/0;
  `bus.sh --self-test` 92/0 (66.07 s); `cloud_dispatch.py --self-test` 77/0;
  `selftest_wiring.py --check` 99/99/0; the three-dot diffstat 10/891/14;
  `ci_predict --base origin/main` no red predicted, rc 0 (14.20 s);
  `rules_sync --check` ok; `policy_lint --report` 0 errors / 50 files;
  `policy_lint --budgets` rc 0; `carry_audit.py check` 10 routed, 0 unrouted;
  `merge-tree` rc 0; the live render rc 0.
  Carry: dismissed: re-derived
- Not re-derived: `ci_predict.py --self-test` timed out at 420 s on this host
  and printed nothing, so the body's "5 failed" is not verified here; CI's own
  step at the head ("Show the CI predictor …", job `122309519259`) passed,
  which is that check's `0 failed` on Linux. The WIRING arm I drove directly
  instead: a planted unwired tool **in the diff** predicts
  `UNWIRED tools/x_unwired.py: no workflow run line names its self-test`, the
  same tool **outside the diff** predicts nothing, and a wired tool in the diff
  predicts nothing. The render timings are host- and PR-specific and are not
  comparable to the body's #2864 numbers.
  Carry: dismissed: CI ran it

## Policy approval

`dev/governance/roles/fix-review.md` is unchanged since round 1 and remains the
only policy file: it adds two obligations (start from the packet; re-read live
checks) and loosens none, paid inside the same paragraph; `policy_lint
--budgets` rc 0, `--report` 0 errors, `rules_sync --check` ok. `/dev/governance/roles/`
is `@tvofi`'s under CODEOWNERS, so **the owner's approving review is still owed
at merge**, under the cited mandate; this verdict is not it and the orchestrator
must surface it.

## Evidence

`~/hpo-seats/review-2870-r2/evidence/`: `HEAD.txt`,
`selftest-wiring-head.txt`, `selftest-wiring-base410.txt`,
`cloud-dispatch-head.txt`, `cloud-dispatch-base410.txt`,
`arm-refuse-dispatch.txt`, `arm-unavailable-dispatch.txt`,
`arm-unavailable-outside.txt`, `mutation-unavailable-arm.txt`,
`mutation-repo-clouddispatch.txt`, `render-2870-head.txt`,
`bus-selftest-head.txt`, `ci-predict-selftest-head.txt`.
