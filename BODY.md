R10-FLY-PACKET-RED-PATHS (triage P282, P285). The review packet's `red-unanswered` signal called `policy_lint.mjs --pr-body` with `--head` and `--red` only, so policy_lint's main-graded-reporter exemption, which reads the diff's paths, never applied: every pull request was refused on main's `tests / nightly-status` red (#2933, #2946, #2948, #2925, and P285's nine). `review_packet.py`'s `unanswered_reds` writes the diff's paths to `--paths-file`, the paths the base already had to `--existing-file`, and passes `--base`. Both lists come from one helper, `diff_paths(base, head)` (`git diff --name-only --no-renames [--diff-filter=a] base...head`, as `prepr.sh`'s `body_check` derives them), which `gather` calls. A path list policy_lint refuses (its `ERROR [pr-body] --paths-file`/`--existing-file` early exit) now raises UNAVAILABLE instead of reading as "no unanswered red". The exemption list is not copied: policy_lint stays its one implementation, as `body_check` keeps it.

Alternatives: copying the reporter list into review_packet.py lost (two implementations of one exemption, the drift `body_check` avoids); having review_packet call `prepr.sh`'s `body_check` lost (a shell function of a 3000-line script, and it reads `HEAD` of the checkout rather than the packet's head). For the round-1 wiring finding, asserting on policy_lint's bare rc lost: policy_lint exits 1 on any body error, including the unanswered reds this signal reports, so only its two path-list refusals are keyed.

Round 2: answers verdict/2962 round 1 (mutation-survivor M2, `--existing-file` dropped; finding M5/M6, gather's wiring unpinned).

## Head

`f130bd950eb94a5466a510ebdbef81f8eb99912c`, one commit on the reviewed head `34ce6c99b6bf5dd7f64f6b1d78a6eb6a53460d7e`, merge base origin/main `ce5940c0d1d8f611a818d53e7fffcafb48b356c1` (origin/main's tip at 2026-10-29T18:46:57Z; `git merge-tree --write-tree origin/main HEAD` exits 0). The code before this round: `67e55b1abe25bc12ba91afc19c71e81cbc754800` (authored), `93d2acd2e306c223e1a0d0d1a946eb6d4db82e5f` (the orchestrator's automatic merge of origin/main `ce5940c0d`), `34ce6c99b` (this PR's own delivery row only).

## Mutation proof

Each mutant applied by exact string replacement to `tools/audit/seat/review_packet.py`, `python3 tools/audit/seat/review_packet.py --self-test` run, file restored (driver: a scratch script, one replacement per mutant, asserting each target occurs once):

- M1, `"--paths-file", str(pf), ` deleted: `51 checks, 4 failed` — `red-unanswered: main's nightly-status red is not owed by a diff touching only a test file`, `red-unanswered: main's delivery-status red is not owed by a diff adding only its own delivery row`, `red-unanswered: a path list policy_lint refuses is UNAVAILABLE, not no unanswered red`, `diff_paths -> red-unanswered: the row the diff adds owes main's delivery-status nothing`.
- M2 (the verdict's survivor), `"--existing-file", str(ef),` deleted: `51 checks, 2 failed` — `red-unanswered: main's delivery-status red is not owed by a diff adding only its own delivery row`, `diff_paths -> red-unanswered: the row the diff adds owes main's delivery-status nothing`.
- M5, `--diff-filter=a` → `--diff-filter=A` in `diff_paths`: `51 checks, 2 failed` — `diff_paths: an added delivery row is touched, and only a file the base had is existing`, `diff_paths -> red-unanswered: …`.
- M7, `existing` derived without the filter (equal to `touched`): `51 checks, 2 failed`, the same two.
- M8, the path-list refusal guard disabled (`if False and re.search(`): `51 checks, 1 failed` — `red-unanswered: a path list policy_lint refuses is UNAVAILABLE, not no unanswered red`.
- Restored: `51 checks, 0 failed`.

## Unpinned sites

- `gather`'s `red_unanswered = unanswered_reds(…)` line, M6 (replaced by `red_unanswered = []`): survives, `51 checks, 0 failed`. Disposition: not killable by the self-test without driving `gather`, which reads `gh` and runs policy_lint from the checkout `repo()` names, so a throwaway checkout carries no policy_lint to run. Every input that line consumes is now pinned (`diff_paths` over a real three-dot diff, `unanswered_reds` through policy_lint, the refusal guard), so what is left is the call itself. Not added to `dev/audit/harnesses/r10_seat_selftests_mutants.py`: a hot file #2959 holds a merge verdict on (the packet's `hot-file` refusal at the first handoff).

## Null control

Self-test arms, driven through policy_lint itself, body `## Red checks` `none`:
- reds `tests / nightly-status` and `typing`, diff touching only `tests/x.py`: `typing` alone (the arm);
- the same reds, diff touching `tests/nightly_status.py`: both (null 1, the reporter's own script);
- the same reds, diff touching `.github/workflows/nightly.yml` and `.github/workflows/governance.yml` (#2954's): both, so a diff touching nightly.yml is still refused on nightly-status (null 2, P285; the brief's kept null);
- red `governance / delivery-status`, diff adding only `dev/programme/delivery/9999.md` (not in existing): nothing owed (the M2 arm); the same row in existing: `governance / delivery-status` owed (its null);
- `diff_paths` over a throwaway checkout whose head edits `kept.txt` and adds the delivery row: touched `{kept.txt, row}`, existing `{kept.txt}`, and that pair through `unanswered_reds` owes delivery-status nothing (M5/M7 arm; under M5 or M7 the row is existing and the red is owed);
- an empty path list: UNAVAILABLE (M8 arm); every other arm above returns a list, not UNAVAILABLE (its null);
- no concluded red: nothing read.

## Figures

- Self-test: `python3 tools/audit/seat/review_packet.py --self-test` prints `review_packet self-test: 51 checks, 0 failed` at `f130bd950`; at `34ce6c99b` it printed 46 (the verdict's figure), so this round adds the five arms named in Null control after the existing four (rule: one `check(` call per arm).
- Mutants: see Mutation proof; M3 (`--base` dropped) is not re-taken (the verdict graded it no finding: the self-test's head is not a commit, so the red history is skipped either way).
- Class seams, rule: `git grep -l -E -- '--red\b' -- 'tools/**' '.github/**' '.claude/**'` (policy_lint.mjs itself excluded), each file's policy_lint call read for `--paths-file` and `--existing-file`:
  - `.github/workflows/pr-contract.yml`: passes both, already guarded;
  - `tools/pr/prepr.sh` `body_check`: passes both, already guarded; its self-test calls at `unnamed-red.md` and `plred` pass non-reporter reds (`fast (3.14)`, `mutation`) on purpose pathless, which owes them in either reading;
  - `tools/audit/seat/body_patch.sh` `contract`: passes both, already guarded;
  - `tools/audit/seat/record_row.py`: passes `--paths-file` and `--existing-file`, already guarded;
  - `tools/ci/alert_list.py`: names `--red` in prose only, no policy_lint call;
  - `tools/audit/seat/review_packet.py` `gather` → `diff_paths` + `unanswered_reds`: closed in this diff.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`; run_always lines `env_drift.py --claims-only origin/main` (`claims hygiene: origin/main ok`), `closure.py selftest` (`ALL 117 closure shrink pins PASSED`), `layout.py` (`layout self-test: ok`) green; `harness_headers.py` not run here: this seat's interpreter has no `voluptuous` (`ModuleNotFoundError`), left to CI, and the diff adds no harness. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- prepr: `bash tools/pr/prepr.sh <body>` at `f130bd950`: every step ok or skipped except `closures`, refused in this seat's environment, not on the diff (`no interpreter that parses the tree was found`: no seat venv at `/root/.local/state/hpo/venv-ci`, and the ambient interpreter lacks the tree's imports), so the closure re-derivation is left to CI; `ci predict` predicts no red once the body passes (`prepr.sh --body-check`: pr-body, carry, preflight, figures and ref_privacy ok).

## Red checks

none

## Forward-carry

none

## Friction

none
