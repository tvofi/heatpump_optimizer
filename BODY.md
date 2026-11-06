Triage batch 126 rules on the existing set under the owner's 5 % and 10 % rule: P391 on the non-production CI lanes and P392 on the triage seat itself. This is the repair of round 1's `figures-uncited` block.

- **P391: DEFER.** Twelve lanes fail the bar at the upper bound, together 24 % of sampled runner hours. Each is a proposal for the owner through the orchestrator; nothing is removed. Required safety lanes and production tests are listed separately and not ruled.
- **P392: DEFER.** The seat costs about 7 to 12 % of local tokens and has no measured benefit. It is ruling on itself, and the entry says so.

The diff is four files against the merge base: `dev/audit/harnesses/r10_triage_p391.py`, the harness that prints every figure (INERT under `dev/audit/`); `tests/closures.json`, one line recording that `tests/harness_headers.py` reads it (written by `tools/pr/ci_predict.py --apply-inert`); `dev/programme/triage/s6-batch126.md`, the ruling; and `dev/programme/delivery/3238.md`, the delivery row. No product behaviour changes.

**Round 1's findings, each answered:**
1. **Figures carried, not cited.** Fixed: the listing scripts land as the harness, and the ruling opens with one command per arm at harness commit `41c5e7bc8`, with fixed windows. Every API figure was re-taken through it. Three figures that came from an earlier ad-hoc sample (`merge-main.yml`, `gate-sweep.yml`, `dependabot-automerge.yml` costs) are marked "withdrawn: not re-derivable within budget", and no proposal rests on them. The token figures come from this host's transcripts, and the ruling says beside them that another seat cannot re-run them.
2. **The five git counts.** Re-derived with the git arm at main `9315526f8` over 2026-10-29T00:00Z to 2026-11-05T07:30Z: `ci: pin killed` 29, `ci: record delivery` 52, `ci: record nightly` 13, `ci: re-record closures` 7, and 229 merges on the first parent. The reviewer's 27 and 239 counted to a later main. The 5 % test now uses 232 branches (262 pull requests merged; record branches recur). **The nearest case moves to 29 commits over 232 branches, 12.5 %: `mutation-pins` was already kept as not refuted, so P391's DEFER does not change.**
3. **Body wording.** This body names the four files and gives the Red checks reason below.
4. **`tvofi` authorship of 34ee0cc0 and 08d62371: a non-defect.** The instruments wrote them, not this seat, by design. `tools/audit/seat/delivery_row.sh` `commit_row` (lines 37 and 38) signs the row as `tvofi`, through `--author` and the committer environment, so that a seat's identity variables cannot re-sign it. `update_pr.sh` line 71 and `open_pr.sh` line 105 merge main with `-c user.name=tvofi`. `pr-contract` passed at the reviewed head. No carry.

## Head

`1eaa5ed53c84c691be20a7eb6fadf408ae163f9b`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P391 and P392 `DEFER` and P393 `None`, and a carry citing either ruling is refused as not an ACCEPT ruling. The harness is evidence and has no consumer in the gate.

## Null control

P393 reads `None`. With the file absent, a carry citing it is refused as not on the roster branch or origin/main.

## Figures

- `git diff --stat b88684a218923f85de66f1e8fb1833e31a76a154...<head>`: 3 files changed, 434 insertions(+) (the code; the delivery row is the PR's own).
- Agreement lane repair (`AGREEMENT REFUSED unregistered=2`): the harness restated two grammars. It now imports `MERGE_RE` from `dev/audit/harnesses/record_burst_replay.py` for the merge-subject count, and its cache key is built by a character test instead of the regex `[^A-Za-z0-9._-]` that `tools/audit/seat/ref_privacy.py` also wrote (that one is a different mapping, `-` in a self-test; sharing it would have changed cache keys). Nothing is registered. Null controls: the key function is equal to the old regex on non-ASCII input (`KEY-SAME`), and the git arm's six RESULT lines are byte-identical old against new (`diff` exit 0). Now `agreement.mjs` prints `RESULT divergent=0 unregistered=0 dead=0 refused=0`. The API arms were not re-run: no cache exists on this host and none was spent; their figures are cited at `41c5e7bc8`, whose API-reading code is unchanged.
- Every ruling figure is printed by the harness arm the ruling names, at `41c5e7bc8`.
- No capped file is touched.

## Red checks

`none`. The reviewed head's check-runs read no failure and no cancellation. This head's checks run after its push.

## Forward-carry

none

## Friction

none
