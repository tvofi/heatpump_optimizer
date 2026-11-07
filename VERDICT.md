Fix review: blocked 01e9c61273753db2526fb19b6b44ece19167128b class-open: tests/nightly_status.py reads every lanes=beat stamp dispatch as the nightly and turns ABSENT red

bus-nonce: a1b69a7cc3fc28b8873af5a467d09ef8

Round 1. Measured head 01e9c61273753db2526fb19b6b44ece19167128b (the head on the PR when this verdict was written, and the head named in the body's `## Head`). Merge base dee8b413fd7d. This verdict is from a detached checkout at that head. No finder's harness is committed for this group (the packet says "Finder's harness: none named"). The harness for the block is my own: `ev/beat_nightly_status.py`, disclosed under step 9.

## Block

The diff makes the stamp's record flush dispatch nightly.yml on `main` with `lanes=beat`. On that run every REQUIRED_LANES job is skipped. `tests/nightly_status.py` picks the newest concluded `schedule`/`workflow_dispatch` run on main (`_discover` keeps every main dispatch; `pick_runs` takes the newest completed one). It then grades that run with `missing_lanes`, which counts a skipped lane as missing and returns `ABSENT`, `EXIT_RED`.

So after this merges, every stamp flush becomes the run `nightly-status` reads. The check goes red on every pull request until the next full nightly concludes. While it is red, it reports the beat instead of the last real nightly, so a real nightly failure's job list is hidden behind "did not run".

Before this diff, the same dispatch ran every lane, and a flush was a full verifying nightly. `defect-root-cause.md` names `nightly.yml` as something `nightly-status` reads, so this is the diff's own seam. It is neither in the diff nor dispositioned in the body: the body never mentions nightly_status or the run selection.

Reproduction: `ev/beat_nightly_status.py` evaluates each job's `if:` with tests/entities.py's own `_workflow_job`/`_gh_if`/`_gh_eval` and feeds the resulting job list to `nightly_status.verdict`:
- head nightly.yml, lanes=beat: `RESULT lanes=beat nightly_status=ABSENT rc=1 ran=['record-autofix']`
- head nightly.yml, lanes=all (null control): `RESULT lanes=all nightly_status=PASSED rc=0`
- base nightly.yml, same beat payload (the base has no input, so every lane runs): `RESULT lanes=beat nightly_status=PASSED rc=0`

A cure in the group's own files: give nightly.yml a `run-name:` that marks a beat run, for example `${{ inputs.lanes == 'beat' && 'Nightly record beat' || 'Nightly' }}`. Then have `nightly_status._discover` drop a dispatch whose `display_title` marks a beat, before `pick_runs`. Add an entities pin that a beat run is never the graded run, with a null control that a lanes=all dispatch still is.

## Findings

- class-open, as in `## Block`: tests/nightly_status.py's run selection (`_discover`/`pick_runs`/`missing_lanes`) grades a lanes=beat flush dispatch as the nightly, and reads ABSENT red after every stamp. Carry: R10-FLY-STAMP-FLUSH-COST
- The brief's "measure before and after on one beat-only dispatch: its jobs and runner-minutes by the runs jobs API" is not done. The body says so (no dispatch right) and defers it to the first stamp after merge. That deferral is owed after the merge, and its measurement must also confirm nightly-status's reading of that run (above). Carry: R10-FLY-STAMP-FLUSH-COST

## Evidence

- Mutation proof (step 1), re-run by me on the committed tree and restored each time (`git status --short` clean):
  - drop `if head: argv += ["--head", head]` in `disposition_gate_argv`: stamp self-test FAIL "rows gate: the stamp's head is passed to the instrument, one window with rule 4" and "rows gate: disposition_gate forwards its head to the command" (`ev/mutant1-drop-head.txt`)
  - `dispatch_record_beat` posting `{"ref": "main"}`: FAIL "record beat: dispatch_record_beat posts lanes=beat" (`ev/mutant2-payload.txt`)
  - main() rule 5 calling `disposition_gate(last_tag)`: FAIL "rows gate: main's rule 5 passes the stamp head" and "main() runs the disposition gate, before the manifest rule" (`ev/mutant3-main-head.txt`)
  - every `&& inputs.lanes != 'beat'` deleted from nightly.yml (`ev/mutant-nightly.diff`): entities FAIL "lanes=beat skips every heavy nightly lane and runs record-autofix; no input runs every lane", plus the derivation null control (`ev/entities-mnightly-fails.txt`)
  - `delivery_status.gather` span reverted to `origin/main` (`ev/mutant-delivery-status.diff`): entities FAIL "delivery_status --head selects its window  [gather(head=M1) returned [102, 101], expected [101]]" (`ev/entities-mds-fails.txt`)
- RESULT stamp_self_test=pass at the head (`ev/stamp-selftest-head.txt`).
- `tests/entities.py` at the head in this container: 3 of 2650 failed (rc=1). The three are "the coverage job reuses only an entry main's push run saved…", "the release ZIP holds the integration folder at its root…" and "the Pages workflow deploys on a release tag…". These are workflow-run probes, not this diff's checks. Both mutants add only their own failures over this set, which is the same at head and in both mutants. CI's gate is green at this head. I did not re-run entities at the base, so I am not re-deriving the body's figure "ALL 2650 ENTITY CHECKS PASSED" in this container. The count 2650 matches.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (`ev/structure-head.txt`). No `*_budgets.json`, VERSION, manifest or RELEASE_NOTES.md in the three-dot diff.
- Delivery row `dev/programme/delivery/3296.md` is in the diff; packet carry_audit and figure_lint at the head are clean (FIGURES: 4 resolved).
- `git merge-tree --write-tree origin/main 01e9c612…` at origin/main 98a3aab6: rc=0, tree dee8b413… (`ev/merge-tree.txt`). There is no conflict.
- CI: `merge_train.py classify 01e9c612… --pr 3296` gave `GREEN 01e9c61273753db2526fb19b6b44ece19167128b pending: none red: none` (rc 0, `ev/classify-1.txt`). All check-run pages are in `ev/check-runs.tsv`, 160 rows. Concluded reds: tests / nightly-status (128480692664, plus its duplicate listing 128501222702 with identical times); pr-contract / pr-contract (128492906044 / 128501198033, 18:41); gate (128481833681, 128487511325, 128493108261); gate and arch-score cancelled (128481461227, 128480844487) at 17:55. The body's `## Red checks` names nightly-status, pr-contract and gate, and answers each. A later pr-contract run, 128500799416 (19:12, after the last red concluded at 18:41), is green and the gates after it are green. So rule 11 holds, and nightly-status is outside the required set under the owner ruling. The cancelled arch-score at 17:55 is superseded by a green arch-score and is not required.
- Step 4 (claims): the diff touches no golden or claim file and no solver code, so no drift is expected.
- `head` in stamp main() is bound at `head = sh("git", "rev-parse", "HEAD")` and rebound by `flush_before_tag` before rule 5, so `disposition_gate(last_tag, head=head)` reads the same head rule 4 enumerates. Checked by reading; the self-test pins it only by source text.
- Role contract current: `git diff merge-base...origin/main -- dev/governance/roles/` shows only the one-sentence "Evidence names differ beyond case" addition, which this verdict follows.
