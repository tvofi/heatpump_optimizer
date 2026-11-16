Fix review: merge 724ee26de5ee639ab76f3bb33ee534a18da30211

bus-nonce: 48c98b3aaa833ec3c99696724a84d60d
pending-ci: gate

## Scope

Round 1 (first review, full scope; no `--reviewed-head`). Head measured: `724ee26de5ee639ab76f3bb33ee534a18da30211`, merge base `6f422812d5d8b918beace0283419c153f6df66ce`. Role contract diff `merge-base...origin/main -- dev/governance/roles/` is empty. Diff: `tools/policy/policy_lint.mjs` (`checkOrphanCaps` reads `files` and `files_tokens`; acceptance drives a token-only orphan), two `files_tokens` caps dropped from `dev/governance/config/policy_budgets.json`, the delivery row `dev/programme/delivery/3673.md`. No `custom_components/` line.

## Evidence

- RESULT mutation M1 (`['files','files_tokens'].flatMap` -> `['files'].flatMap`): `node tools/policy/policy_lint.mjs` rc=1, `FIXTURE VACUOUS: checkOrphanCaps did not report the files_tokens cap ... (got [])`. Killed. `ev/mut-M1-files-only.txt`.
- RESULT mutation M2 (message names `files` instead of `${table}`): rc=1, `FIXTURE VACUOUS` (the `/files_tokens/` message pin fires). Killed. `ev/mut-M2-message-no-table.txt`.
- RESULT mutation M3 (re-add both dropped caps to `files_tokens` at the head): rc=1, `TOTAL: 2 error(s)`, one `[budgets]` error each for `tools/audit/briefs/nudge.md` and `tools/audit/harnesses/README.md`. Killed. `ev/mut-M3-readd-caps.txt`.
- RESULT mutation M4 (the new `ocTok` acceptance drive replaced by `[]`): rc=1, `FIXTURE VACUOUS`. Killed. `ev/mut-M4-drop-tok-drive.txt`. (A first M4 attempt with a wrong indent did not apply and is recorded as `ev/mut-M4-noop.txt`: FIXTURE ok, not a survivor.)
- RESULT head: `node tools/policy/policy_lint.mjs` rc=0, `TOTAL: 0 error(s) across 55 policy file(s)`, `FIXTURE ok: ... 279 pins` (`ev/policy_lint-head.txt`). Base null control: rc=0, `TOTAL: 0`, `278 pins`, no mention of either orphan path although both caps are present there (`ev/policy_lint-base.txt`): the escape the body describes reproduces at the base. Pin delta +1 matches `pins += 3` -> `+= 4`.
- Both dropped paths are absent at the merge base and at the head (`git ls-tree` empty, `ls` missing); neither had a `files` (line) cap at the base, matching the body's "token cap with no line cap" for `tools/audit/harnesses/README.md`. `tools/audit/harnesses/README.md` likewise.
- Class enumeration: the body's rule is the extended check over the tree; at the head it returns nothing and with the caps re-added exactly the two dropped ones (M3). The many `tools/audit/briefs/*` caps that remain are not orphans: `trackedFiles` spells moved policy files by their canonical old names (`POLICY_GLOBS` comment, R9-RO-5), so they are measured, and the lint (which would report them) is clean. One-table-per-class: the budget file's only per-file cap tables are `files` and `files_tokens` (its top-level keys), both now read.
- RESULT budget raises: `budget_raise_gate.raises_between(mb, head, ...)` -> `[]`; grader control (`files_tokens["CLAUDE.md"]` removed over the base budget) -> one `cap removed while the file it caps is still in the tree` raise, so the empty list is not a grader reading nothing. `ev/raise-gate.txt`, driver `ev/raise-gate-driver.py` (built by this reviewer, disclosed).
- RESULT `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`; `score.py --diff` -> `Architecture score: dS +0.0000 NULL`; `closure.py select --diff <mb>` -> `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, RUN `tests/entities.py`. All match the body's Figures. `tests/entities.py` itself I did not finish locally (my 220 s cap; partial log `ev/entities.txt`); its result is CI's (`tests / closures`, `tests / fast (3.14)` success at this head), cited, not re-run.
- `VERSION`, manifest and `RELEASE_NOTES.md`: untouched (`git diff mb head --stat` empty).
- `git merge-tree --write-tree origin/main 724ee26d...` rc=0: merges cleanly (`ev/merge-tree.txt`).
- Body `## Head` names `724ee26de5ee639ab76f3bb33ee534a18da30211`, the head measured.
- Finder's harness: the review packet names none; the finding's instrument is the lint itself, run at both ends above. No committed external harness exists for this governance-only seam.
- Forward-carry: body says none; Carry 0 from R11-INTAKE-R10-RESIDUE is built in this PR, nothing handed on.
- CI: `gate` concluded failure twice at this head (jobs 133448215889, 133450146733); its log reads `FAIL run(s) [43905168301] at this head are still being judged; their gate decides` — a sequencing red while the test run was in flight, not a defect, and `merge_train.py classify` reads it as pending. `tests / nightly-status` failure is outside the `owed-reds` set (`ev/owed-reds.txt`). Classify log: `ev/classify-log.txt`.
- Head re-read before return: `fix/r11-policy-token-cap` still at the measured head (`ev/head-recheck.txt`).
- CI wait: `merge_train.py classify 724ee26d... --pr 3673` printed `WAIT ... pending: gate red: none` on every run 17:16-17:45 UTC (rc=3); the review is complete, so `pending-ci: gate` stands for the relay.

## Findings

none
