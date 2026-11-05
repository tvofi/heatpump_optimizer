Fix review: blocked f190c717d0074911ac3106d7df72bb1669ee4316 mutation-vacuous: deleting the confirmGapMerge guard in fetchPullsBySha leaves every check green

bus-nonce: 1114067b2f6a53deb5a483eb39cefd75

Round 1 of the fix review for #3217 (R10-HOTFIX-RECORD-ATTRIB round 2). Measured at head f190c717d0074911ac3106d7df72bb1669ee4316, which is still the PR head (refs/pull/3217/head). Done from detached worktrees at the head and at the merge base af941ad4a296ffec76562e3161972bce3ad2dec4.

## Block

The behaviour change this PR ships is the three-line guard in `fetchPullsBySha` (tools/policy/policy_lint.mjs:2126-2128). When the subject number is not confirmed, the guard turns the enumeration into `ok:false`. No test reaches that guard. The three new acceptance pins only call the `confirmGapMerge` helper. `fetchPullsBySha` hard-wires `ghGet`, so no offline test can drive it. Every acceptance test of the window path (`pullsByShaShared`, lines 4816-4858) swaps in a stub fetcher in its place. In the tree, `fetchPullsBySha` and `confirmGapMerge` are named only in tools/policy/policy_lint.mjs.

Mutant M3 deletes the guard (the `if (resolved.source === 'subject-gap' && !confirmGapMerge(...)) { return { ok: false, ... } }` block). The self-test still prints `FIXTURE ok: 93 error(s) hold 263 pins` with rc=0. With that mutant, an empty `/commits/<sha>/pulls` answer on a subject naming a pull request whose merge commit differs is trusted again without a word. That is exactly the case the brief asks to see refused, and it survives.

To clear the block: give `fetchPullsBySha` an injectable getter (`get = ghGet`, like `confirmGapMerge`) and pin all three cases at the enumeration level:
- an API row;
- a gap whose `/pulls/<n>` merge_commit_sha equals the sha (recovered, listed in `gapShas`);
- a gap whose merge commit differs (`ok:false`).

The fixer then reruns M3 and shows it killed.

## Findings

- Refusal wording: the `why` string says "that pull request's merge commit differs" even when `/pulls/<n>` could not be read at all (HTTP error or rate limit), because `confirmGapMerge` collapses both into false. Record_row.py's Refuse names both causes. Fix it in the same repair so a red run names the real cause. Carry: R10-HOTFIX-RECORD-ATTRIB
- Divergence on the normal path: the JS API-row path (`resolvePrFromCommit` with a non-empty answer) takes the row's number without the merge_commit_sha join that record_row.py `attribute_merge` applies. The brief scopes this PR to the empty-answer case and the normal path is meant to stay unchanged, so the divergence predates this PR and is not introduced by it. Carry: dismissed: outside the group brief, which fixes the normal API path as unchanged; pre-existing
- Third reader: tools/policy/record-predicate/sweep.mjs `verifyNewest` (line 202) reads `/commits/<sha>/pulls` `.[0].number` with no subject recovery. It is the `--verify` diagnostic comparator, not an attribution path that records. A gap commit shows up there as a loud onlyMap row, not a silent drop. It predates this PR. Carry: dismissed: diagnostic comparator, over-reports loudly rather than silently mis-attributing

## Evidence

- RESULT self-test at head: `FIXTURE ok: 93 error(s) hold 263 pins across 12 check classes` (rc 0). At base af941ad4: `... hold 260 pins ...`. The body's figure, 260 to 263, is re-derived and true.
- RESULT M0 null control (unmutated): FIXTURE ok, rc 0.
- RESULT M1 (`confirmGapMerge` returns true, the body's own mutant): FIXTURE VACUOUS naming "merged at a different commit was confirmed" and "could not be read was confirmed", rc 1. Killed, and the body's mutation-proof claim is reproduced.
- RESULT M2 (returns false): FIXTURE VACUOUS "merge_commit_sha equals the sha was not confirmed", rc 1. Killed.
- RESULT M4 (sha equality dropped, `Boolean(res.ok && res.data)`): FIXTURE VACUOUS "merged at a different commit was confirmed", rc 1. Killed.
- RESULT M3 (guard in fetchPullsBySha deleted): FIXTURE ok, 263 pins, rc 0. SURVIVES.
- The run of tests/entities.py under M3 (ev/m3-entities.log) is not evidence either way: it stopped at import (`ModuleNotFoundError: homeassistant`) in this container. The finding rests on reachability: `fetchPullsBySha` is only called through the default `fetch` of `pullsByShaShared`, and every test overrides that default.
- Python half: record_row.py `attribute_merge` (main, #3194) matches on merge_commit_sha, falls back to `delivery_status.subject_number`, confirms against `/pulls/<n>`, and otherwise raises Refuse. This is consistent with the brief and was not re-mutated here (it is not in this diff).
- Finder's harness: the packet names none. The brief's measured case (616868bdc5ca returns [] for #3179) is a live-API observation. I did not re-query it, so it is not re-derived.
- merge-tree with origin/main: rc 0, no conflicts (ev/merge-tree.txt).
- VERSION, manifest, RELEASE_NOTES and the claim files are untouched by the three-dot diff.
- The body carries every heading in .github/PULL_REQUEST_TEMPLATE.md (Head, Mutation proof, Null control, Figures, Red checks, Forward-carry, Friction).
- CI at the head, read live at about 00:47Z: `merge_train.py classify` still prints `WAIT ... pending: gate red: none` (rc 3) after roughly 55 minutes of polling. tests / fast (3.14) and tests / coverage are in progress. Red: governance / delivery-status and tests / nightly-status. These are not judged here because the head's workflows have not concluded (fix-review.md step 11). Note that this diff adds dev/programme/delivery/3217.md, which delivery-status reads. Because the block stands on the mutant alone, I am returning the hotfix verdict now and not waiting for CI to conclude.
- Roles drift check: on main since the merge base, only dev/governance/roles/nudge.md changed; fix-review.md is current.
