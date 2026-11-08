R10-CI-OWN-DELIVERY-ROW (owner-approved CI-throughput lever 2, #201 comment 6707834331). R10-CI-SLIM's C7(a) stands the machinery lanes down only on an all-product pull request. Every pull request carries its own delivery row `dev/programme/delivery/<N>.md`, which is not product, so the idling could not fire on any of them.

**Step 1's recording changed the scope of this fix.** The brief said to exempt the row only for the lanes that read no row. `dev/audit/harnesses/lane_reads_delivery.py` ran every `run:` step of each machinery lane under strace, in a fresh clone of the head (f020f31c). It counted each open, directory listing and exec that names a row of the clone, or of a copy of the tree. The result is `dev/audit/harnesses/lane_reads_delivery.recording.json`:

- `tests / arch-instrument` reads **no** row. No syscall in any of its three run steps names `dev/programme`, under any root. `arch_score.py` and `arch_score_head.py` ran to `ALL TEST SCRIPTS PASSED`.
- `tests / closures` reads rows in its re-record step: the `tests/entities.py` recording, `policy_lint.mjs --record`, and `policy_lint`'s tree-wide `git grep -I -l`.
- `governance / env-matrix` reads rows. It copies the pull request's tree into `$RUNNER_TEMP/envmatrix/{pr,push-main,no-remote,shallow,…}` and runs `policy_lint` in each copy, which opens and lists every row.
- `governance / instrument-self-tests` reads rows. Step 2 (`policy_lint_mutants.mjs`, which runs `policy_lint.mjs --record --since` and its `git grep`) opens and lists the clone's rows. This lane's trace was still running when the recording was summarized (49 of its 100 run steps closed). A partial lane can only add readers, never clear one, so the verdict stands.

So this pull request does **not** idle all four lanes on a package-plus-own-row diff. `prelude.outputs` now emits two outputs:
- `machinery`: unchanged, the strict C7(a) rule. It gates the three lanes that read rows.
- `machinery_rowblind`: the same rule with exactly this pull request's own row ignored. It gates `tests / arch-instrument` alone, through a new `tests.yml` input that `ci.yml` passes.

`LANE_GATE` records which output each lane gates on, and the self-test `lane_gates` check pins it against the workflow text. A lane that reads rows therefore cannot drift to the row-blind input unseen.

The brief estimated 1,380 runner-minutes a day for idling all four lanes. That estimate does not carry over: what remains is arch-instrument's share alone, and that share is not re-measured here. Taking the row out of the other three lanes needs their row reads either shown irrelevant or removed. That is a separate change, and its seams are the readers listed above.

Transition: `ci.yml`'s prelude job restores `tools/ci/*.py` from the base, so on this pull request the base prelude runs and emits no `machinery_rowblind`. arch-instrument's steps test `!= 'false'`, so an empty input runs them (fail closed).

**Repair round (the `tests / fast (3.14)` red).** `tests/harness_headers.py` failed on its own check `every inlined walk matches the canonical helper and no depth root remains`. It printed `FAIL depth seams: dev/audit/harnesses/lane_reads_delivery.py:50: ROOT = Path(__file__).resolve().parents[3]`. Main is green because that harness is new in this diff: `depth_root_seams()` scans every harness file, and a fixed `parents[N]` root is a depth seam it refuses. ef830f662 replaces that line with the canonical `repo_root(__file__)` walk, inlined byte-for-byte from `tools/audit/repo_root.py` as every sibling harness does it. No assertion or harness was changed.

## Head

ef830f662b648d3113dadae22e23f903e6ea03fe, a fast-forward of the PR head 2a7dcd6cf. The earlier step evidence below was measured at f8c052779. The repair commit touches only `dev/audit/harnesses/lane_reads_delivery.py`'s root line. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in, per the owner's 2026-11-07 ruling.

## Mutation proof

Each mutant applied to `tools/ci/prelude.py` (M5 to `.github/workflows/tests.yml`), checked with `python3 tools/ci/prelude.py --self-test`, then restored:
- M1, own-row exemption deleted (`and f != own` removed): 2 failed, `C7a-row: a package file plus its own delivery row idles them` and `C7a-row: the prelude passes the event's number: package + row 7 on pull request 7 idles the row-blind lanes`.
- M2, the brief's mutant (every file under `dev/programme/delivery/` exempted): 4 failed. These are `C7a-row: ANOTHER pull request's row still counts as machinery`, `C7a-row: ... and so does the row when the event names no number`, `C7a-row: ... and runs the lanes that read rows` and `C7a-row: ... and row 8 on pull request 7 runs them`.
- M3, `machinery_rowblind` not passed the PR number: 1 failed, `C7a-row: the prelude passes the event's number: ...`.
- M4, the strict `machinery` output also exempts the row: 1 failed, `C7a-row: ... and runs the lanes that read rows`.
- M5, `tests / closures` gated on `inputs.machinery_rowblind`: 1 failed, `C7a-row: each machinery lane's job names exactly its own machinery input`.

Failing test first: c35565f94 is the self-test against the unchanged production code, and it fails with `TypeError: machinery() takes from 1 to 2 positional arguments but 3 were given`.

## Null control

Repair: at the PR head 2a7dcd6cf, `cd tests && python3 -c "import harness_headers; raise SystemExit(harness_headers.inline_scan())"` prints the depth-seam FAIL above with rc=1. At ef830f662 it prints nothing, rc=0. Restoring `ROOT = Path(__file__).resolve().parents[3]` makes it red again: that is the mutation proof for this repair.

At the base, `machinery` has no PR number, so a package file plus its own row runs every machinery lane (the c35565f94 red above). At the head:
- a row beside `tools/ci/gate.py` still runs the lanes;
- a row of ANOTHER pull request still counts as machinery;
- the row when the event names no number still counts;
- the own row alone runs them;
- an empty or unread changed list runs them;
- an unreadable script table runs them;
- a push runs them, for both outputs.

These are the `C7a-row:` checks in `python3 tools/ci/prelude.py --self-test` (76 checks, 0 failed).

The `--refresh-index` arm (`python3 dev/audit/harnesses/lane_reads_delivery.py --refresh-index --lanes closures --out <dir>`) refreshes the clone's index before any step runs, which removes git's rehash of a fresh checkout. Under it the closures re-record step still prints `open=128508 list=18`, so its reads are the steps' own and not that rehash.

The recording's own controls are in the `control` lane: a planted reader of a row (`cat`, plus `git show HEAD:<row>`), a planted copy of the row directory read whole, and a one-row fixture. They print `RESULT control_hits=3 copy_reader=True fixture_reader=False` (`python3 dev/audit/harnesses/lane_reads_delivery.py --lanes control --out <dir>`). So a tracer recording nothing would not read as clean, and a fixture repository is not counted as the clone. The fixture control caught two scan errors in the inherited harness, both fixed in 245cb2055. Copies of the tree went uncounted, which hid env-matrix's reads, and an absolute argv into a fixture was counted.

## Figures

- Lane read verdicts: `dev/audit/harnesses/lane_reads_delivery.recording.json` `verdict`, from `python3 dev/audit/harnesses/lane_reads_delivery.py --lanes <lane> --out <dir>` per lane, then `--summarize`. The rule is in the file's `rule` field.
- Control: `python3 dev/audit/harnesses/lane_reads_delivery.py --lanes control --out <dir>` prints `RESULT control_hits=3 copy_reader=True fixture_reader=False`.
- Self-test: `python3 tools/ci/prelude.py --self-test` prints `prelude self-test: 76 checks, 0 failed`.
- Diff mutants: `python3 -I tools/audit/seat/mutant_run.py --diff <merge-base>...HEAD --cmd "python3 tools/ci/prelude.py --self-test" --max-mutants 0 --report-only` ran 19 mutants on the added lines of `tools/ci/prelude.py` in 5 s wall (at f8c052779). 5 SURVIVED, listed under `## Unpinned sites`; the other 14 were killed.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff <merge-base> --workdir <dir>` prints `MODE: FULL` (`.github/workflows/ci.yml` changes the gate itself), so the suite is left to CI.
- `tools/pr/prepr.sh` with `MUTANT_CMD="python3 tools/ci/prelude.py --self-test" MUTANT_MAX=0` and this body: rc=0 at ef830f662, 355 s wall. Its diff-mutant step ran the same 19 mutants (the harness lines are outside the driver's scope) and left the same 5 survivors, all answered under `## Unpinned sites`. Main has not been merged in. `git merge-tree --write-tree origin/main HEAD` reports no conflict, and the owner's 2026-11-07 ruling says to hand off at the first clean head.
- Repair: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED` at ef830f662. `cd tests && python3 -c "import harness_headers; raise SystemExit(harness_headers.inline_scan())"` exits 0 in 0.7 s at ef830f662 and 1 at 2a7dcd6cf.

## Unpinned sites

- `tools/ci/prelude.py:553 CALL_DEL`: deletes the self-test check `an empty list still runs them`. Deleting an assertion cannot redden its own suite. The fail-closed `not files` arm it pins predates this diff (C7a's own empty-list check).
- `tools/ci/prelude.py:554 CALL_DEL`: deletes the self-test check `an unread changed list still runs them`. Equivalent by construction, as for 553.
- `tools/ci/prelude.py:561 CALL_DEL`: deletes the self-test check `... and runs the lanes that read rows`. It is the check that kills M2 and M4 above, so its work is shown there.
- `tools/ci/prelude.py:564 CALL_DEL`: deletes the self-test check `... and row 8 on pull request 7 runs them`. It kills M2 above.
- `tools/ci/prelude.py:567 CALL_DEL`: deletes the self-test check `a push with the row still runs them`. Equivalent by construction. The push arm (`ev != "pull_request"`) is also pinned by `C7a: a push always runs them (null control)`.

## Red checks

- `tests / fast (3.14)` (and the required `gate`, which reports it): class: own diff. `tests/harness_headers.py`'s depth-seam check refused the new harness's `parents[3]` root; repaired in ef830f662. Cheaper detector: `harness_headers.inline_scan()` alone takes 0.7 s and measures nothing about the machine. `tools/pr/prepr.sh` leaves all of `harness_headers.py` to CI, because the script holds the EXCLUSIVE gate lease (`gate_lock.py needs-lease` answers `lease`). So the structural check rides inside a lease-deferred run, and no seat-side step runs it. Countermeasure not built here: it changes `prepr.sh`, which is outside this group. Carried below.

## Forward-carry

- The row reads of `tests / closures`, `governance / env-matrix` and `governance / instrument-self-tests` are listed in `dev/audit/harnesses/lane_reads_delivery.recording.json`. They stop the own-row exemption from reaching those three lanes. Carry: dismissed: the brief's own rule (exempt only the lanes that read no row) decides them here; whether to remove those reads is a new lever for the owner to price
- `tools/pr/prepr.sh`: run `harness_headers.inline_scan()` (0.7 s, no lease) as its own step, so a depth seam is refused before the push instead of in `tests / fast`. Carry: dismissed: tooling outside this group's scope; recorded here for the root-cause seat

## Friction

- `fixer.md`: cost: the cloud seat's `BASH_ENV` (`/etc/profile.d/hpo-toolchain.sh`) re-exports `RUNNER_TEMP` into every non-interactive bash, so harness lanes run side by side shared one runner temp and env-matrix's step failed. The harness now clears it (f020f31c4). Carry: dismissed: repaired in this diff
