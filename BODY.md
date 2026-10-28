R10-RCA-HEADMOVED: the root-cause record for #2389 (`head-moved (rework)`),
which the owner asked for on 2026-10-18. It measures what still moves heads
under a review now that K5 (`fixer.md`'s absorb rule) and the relay freeze
(#2792) have landed. It also builds the one countermeasure that passed the cost
test: `carry()` now carries a merge of a seat's own handed-off main merge.

Refs #2389.

The record is `dev/audit/rca/R10-RCA-HEADMOVED.md`. Its harness and outputs are
in `dev/audit/rca/headmoved/`, and `dev/audit/config/bugclasses.json` cites it.

- **Process states:**
  - (c) `carry()` reads one hop of history.
  - (b) `nudge.md` §2's carry-first rule: 6 instances.
  - (a) No freeze on non-roster heads for the orchestrator's own pushes: 2
    after the split.
- **Cost-test verdicts:**
  - CM-1 (built): standing cost within self-test noise; 8 of 75 entries flip
    to `CARRY: yes`.
  - CM-2 (the brief's autofix-pin candidate): refused, already in the tree.
  - CM-3 (§11's file-disjointness clause): owner's decision.
  - Buckets 1 and the post-split breaches: recorded refusals.

**Disposition of #2389: stays open.** Every group that lists it is accounted
for in the record's section 7:

- **R10-FLOW-ROSTER-FREEZE:** arm (a) merged. Roster-PR breaches went from 3 to
  0. Close-out #2903 has no head-move arm.
- **R10-FLOW-BODY-ONLY:** not started. `update_pr.sh:64` still merges main
  unconditionally.
- **R10-FLY-ROW-HEAD-CARRY:** not started. 0 of the 75 entries are row-only
  moves.
- **R10-FLY-CARRY-DOC-CONTEXT:** not started. It reaches 2 of the 75.

Three of the four have not landed, and the count is unchanged under its keying.
Neither the keying rule nor the future bodies are changed by this pull request.

**Owner approval at merge.** CM-1 widens what `tools/pr/app_approve.sh --carry`
accepts without a reviewer turn. That is an approval instrument, so the owner
reviews it, though the path is not code-owned.

## Head

`25339ace561a6fd3be20e09a8df2e664c1574147`, cut from `origin/main`
`6d86acc909f7fc465e5736771daf8fa45c1373a4` (tip at 2026-10-28T10:14Z).

## Mutation proof

- **Fix removed.** `tools/pr/app_approve.sh` restored to main's `carry()` with
  the new cases kept: `app_approve self-test: 258 checks, 2 failed`.
  - `CARRY: a merge of a handed-off head that is itself a carried main merge
    (#2876's shape)` got 1, wanted 0.
  - `refused for the handed-off head's own merge, which the outer diffs cannot
    see` got 0, wanted 1.
- **Inner carry's answer ignored** (`e=$(carry "$v" "$2" "$main"; true)`):
  `258 checks, 3 failed`.
  - `NO CARRY: a merge of a handed-off head whose own main merge was
    hand-resolved`
  - its `not the automatic merge` reason
  - `NO CARRY: a merge of a branch that is not main`
- **Fixed:** `258 checks, 0 failed`.

## Null control

- Main's unmodified `app_approve.sh --self-test`, run from `tools/pr/`: `254
  checks, 0 failed`.
- Over all 75 historical pairs (`hm6_out.tsv`), the fixed carry changes no
  `yes` to `no`. 48 refusals stand. The 8 new `yes` are all shaped as a merge
  of a handed-off main merge. In each, the own patch moved only in paths the
  carry already excludes.

## Figures

- 588 bus refs; 75 re-verifications after a `merge` on 55 PRs, 21 of them after
  2026-10-25T07:38Z: `python3 dev/audit/rca/headmoved/hm.py 2026-10-08 --carry`
- Today's carry, 64 of 75 `yes`: `hm.py`'s last column. Carry at the time, 19 of 75: `python3 dev/audit/rca/headmoved/hm2.py`
- Bucket counts, blocked counts and lags (record section 2): `python3 dev/audit/rca/headmoved/hm4.py` and `python3 dev/audit/rca/headmoved/hm5.py`
- 8 flips under the fixed carry; 1 of them passes §11 whole: `python3 dev/audit/rca/headmoved/hm6.py`
- 467 and 87 PR merges either side of the split: `git log --first-parent --merges --since=2026-10-14T00:00Z --until=2026-10-25T07:38Z --format=%s origin/main | grep -c '^Merge pull request'`, and the same from 2026-10-25T07:38Z to 2026-10-28T03:40Z
- 59 rework re-verifications on 44 PRs, and `5 / 7 head-moved`: `node tools/policy/policy_lint.mjs --stats --since v7.0.0`
- Self-test times: main 38.3, 37.7, 37.1 s; fix 38.3, 37.5, 37.1 s: `bash tools/pr/app_approve.sh --self-test`, 3 runs each

## Red checks

none

## Forward-carry

- **R10-FLY-CARRY-DOC-CONTEXT.** CM-1 edits `carry()`'s merge-parent test
  (`tools/pr/app_approve.sh:237-240`). That group's change is in the final
  comparison (`:313-318`), a different hunk. Measured reach of its `.md` arm in
  this window: 2 of 75 (#2547, #2645), both before 2026-10-25. Lands in
  `dev/audit/rca/R10-RCA-HEADMOVED.md` section 7. Carry: R10-FLY-CARRY-DOC-CONTEXT
- **R10-FLY-ROW-HEAD-CARRY.** 0 of the 75 re-verifications were moves limited
  to the PR's own delivery row, so its verdict side has nothing to carry in this
  window. Its CI-result side was not measured here. Re-measure before building.
  Lands in `dev/audit/rca/R10-RCA-HEADMOVED.md` section 7. Carry: R10-FLY-ROW-HEAD-CARRY

## Friction

- tools/audit/seat/ref_privacy.py: unclear: on a cloud seat, where `$HOME` is `/root`, `--check` refuses the citation `dev/governance/roles/root-cause.md` as `home-directory`, and `scrub --write` rewrites nothing ("0 of 1 file(s) rewritten"). The record drops the path instead. Routed to the open group that already edits `ref_privacy.py` (its PUSHERS carry). Carry: R10-FLOW-BODY-ONLY
