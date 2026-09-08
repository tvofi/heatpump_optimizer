`Fix review: merge 9ad48cf9`

Detached worktrees at `9ad48cf9bb6685f306776fdfb22a3dfb907af0a8` and `b34af6b7` (both removed; main tree `git status --porcelain` = 0 lines). Scope: `git diff b34af6b 9ad48cf` (two files, 48+/6−) plus the live `## Red checks`. Every number below I drove myself; none taken from the body.

## Instance 5 — `policy_lint.mjs`, shallow clone

Built a real shallow clone rather than simulating one: bare mirror with `refs/heads/main` = `6b71e85`, plus refs at each head, then `git clone --depth 1 --no-single-branch file:///tmp/origin618.git`. `git rev-parse --is-shallow-repository` → `true`, `origin/main` → `6b71e85`, `.git/shallow` non-empty.

**Pre-fix (`b34af6b7`) in that clone — the defect reproduces exactly, including the self-contradiction:**
```
node .claude/workflows/policy_lint.mjs   RC=1
  skip     provenance             this clone is shallow, so git cannot say whether deadbee is an ancestor of origin/main
FIXTURE VACUOUS: checkProvenance did not refuse a SHA no object in this clone carries. ... and this clone is not shallow.
node .claude/workflows/policy_lint_mutants.mjs   RC=1
MUTANTS: null control FAILED -- the unmutated acceptance returned 1, so no mutant below proves anything.
```
Two lanes down, and the failure message asserts "not shallow" two lines under its own output saying it is. Confirmed.

**Post-fix (`9ad48cf9`) in that clone:**
```
policy_lint.mjs          RC=0   FIXTURE ok: 37 error(s) hold 56 pins across 7 check classes
                                skip     provenance-deadbeef    this clone is shallow, ...
policy_lint_mutants.mjs  RC=0   PIN  checkProvenance  FIXTURE VACUOUS: checkProvenance did not refuse 04a99eb,
                                     a parentless commit that cannot be an ancestor of anything
                                MUTANTS ok
```
Full clone at the same head: `FIXTURE ok: ... 57 pins`, RC=0. 56 vs 57 — exactly one fewer, and `checkProvenance` is **PINNED, not SKIPPED**.

**The mutant that matters (full clone, production conflates exit 128 again).** Anchor asserted `count == 1`, `const shallow = git([...]).trim() === 'true'` → `const shallow = true`; `node --check` ok:
```
RC=1   skip provenance ... this clone is shallow ...
       FIXTURE VACUOUS: ... and this clone is measured non-shallow above.
```
Guarding the arm did not disable it. File restored byte-identical (`git status --porcelain` = 0).

**Guard removal (shallow clone), `shallowHere = false`:** RC=1, `FIXTURE VACUOUS`. The guard is load-bearing. Restored clean.

**The guard's own honesty — this is the test I pushed hardest on, and it holds.** The author's claim is that `skip <name>-pin` would understate because the parentless-witness arm still drives the check. Two independent routes say the witness arm really does run in a shallow clone:

1. The mutants lane's own `PIN checkProvenance` evidence in the shallow clone names the **parentless witness** (`did not refuse 04a99eb`), not the deadbeef arm.
2. My own harness: in the shallow clone I emptied production directly —
```
python3 ... assert s.count("function checkProvenance() {\n  const sha = provenanceShaSource()") == 1
        → "function checkProvenance() {\n  if (1) return []\n  const sha = ..."
node --check ok;  node policy_lint.mjs  RC=1
FIXTURE VACUOUS: checkProvenance did not refuse 04a99eb, a parentless commit that cannot be an ancestor of anything
```
So the check *is* driven under the guard, and `PIN` is earned. The lane is not reporting a pin for a check it did not drive. Also confirmed by inspection and by run that the new line cannot be misread as a full skip: the lane matches `/^\s*skip\s+(\w+)-pin\b/` and `provenance-deadbeef` has no `-pin` suffix (`\w+` excludes `-`) — and `grep` finds nothing anywhere (`policy_lint_mutants.mjs`, `governance.yml`, `prepr.sh`) that reads the `pins` integer back, so 56 breaks nothing.

## Instance 4 — `check-wave-script.mjs`

**`t()` read, not trusted:** `const t = (n, c, d = '') => { c ? (pass++, console.log('  ok   ' + n)) : (fail++, console.log('  FAIL ' + n + ' ' + d)) }` — detail prints on FAIL only. The body's claim about the helper is correct, so a floor alone would not disclose the population.

**Pre-fix (`b34af6b7`), rosters moved aside:** output at 4 rosters and at 0 rosters is **byte-identical** (`diff` → no output), both RC=0, `26 passed, 0 failed`; zero occurrences of a `scope` line. That is a stronger reproduction than the body's "three identical verdicts".

**Post-fix (`9ad48cf9`):**
```
full population   RC=0   scope  4 roster(s), 59 group(s), 4 distinct stage(s)      26 passed, 0 failed
zero rosters      RC=1   scope  0 roster(s), 0 group(s), 0 distinct stage(s)
                         FAIL every resume.stage ... rosters=0 groups=0 ... at-risk=0    25 passed, 1 failed
zero rosters, floor removed (asserted anchor, node --check ok)
                  RC=0   scope  0 roster(s), 0 group(s), 0 distinct stage(s)        26 passed, 0 failed
```
The `scope` line is printed on the **passing** run, so disclosure is unconditional, and independent of the floor (it still prints with the floor removed). The floor is load-bearing. (The `FAIL (probe, expected) threw: deliberate` line appears in every run including the null control and is not counted — checked.)

**Population numbers re-derived from `origin/main`, not read from the body:** 7 rosters / 84 groups / 4 stages at `6b71e85`; 4 / 59 / 4 at head. The 30% figure is the group drop (84→59 = 29.8%); the roster drop is 43%.

**The stated limit is honest.** `rosters.length > 0` refuses zero only. I looked for anything ratcheting the population: `tests/structure_budgets.json` has 24 metric keys and none mentions roster/wave/group; the only roster references in `tests/` are `tests/entities.py:9978-9979`, a closure-scoping fixture for #493, unrelated. Nothing ratchets it — the body says exactly that.

## The delta broke nothing (at head, full clone)

```
policy_lint.mjs         RC=0  TOTAL: 0 error(s) across 35 policy file(s); FIXTURE ok ... 57 pins
policy_lint_mutants.mjs RC=0  MUTANTS ok (all seven PIN)
brief_lint.mjs          RC=0  TOTAL: 0 across 4 file(s); 931dffe fixture 12 error(s) (9 required); GUARD ok
check-wave-script.mjs   RC=0  scope 4 roster(s), 59 group(s), 4 distinct stage(s); 26 passed, 0 failed
rules_sync.mjs --check  RC=0  RULES-SYNC ok
bash tools/audit/prepr.sh RC=0  every step ok; "no version edit"; "claim files byte-identical to origin/main"; MODE: SCOPED
PYTHONPATH=$PWD/tests/hastub python3 tests/entities.py  RC=0  ALL 1112 ENTITY CHECKS PASSED
python3 tests/structure.py  RC=0  STRUCTURE RATCHET PASSED
```
Exit statuses read from `$?` on the command itself, never through a pipe. `node --check` clean on both changed files and on every mutant before running it.

**Version/manifest/notes:** `git diff 6b71e85...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is **empty**.
**Caps:** the delta does not touch `tests/structure_budgets.json` at all (`git diff --stat b34af6b 9ad48cf -- tests/structure_budgets.json` empty), and I drove the real `POLICY_GLOBS` matcher over both changed paths — `policy_lint.mjs` `false`, `check-wave-script.mjs` `false`. No cap moves for them.
**Claims:** three-dot on both claim files empty; `prepr.sh` reports byte-identical to `origin/main`. Nothing claimed, nothing drifted, so `env_drift --all` has no fixture to compare (the delta is two `.mjs` files, no solver path).
**Conflict (step 13):** `git merge-tree --write-tree origin/main 9ad48cf9` → RC=0, empty stderr, tree `d1d7633`. No conflict; `mergeable_state: unstable` is the draft/checks field, not a merge state.

## `## Red checks` — the prediction came true

Enumerated all 40 `Governance` runs on `claude/repo-governance-audit-tgt5j4`, not sampled. PR #618 opened 11:48:58Z, so its heads are the runs from 11:49:01Z on: `e6230a39`, `095ac806`, `f20b7577`, `b34af6b7`, `9ad48cf9` — the five the table names. Every row in the table checks out exactly (run ids, `created` timestamps, and the count of passing runs).

**The prediction.** The body predicts `b34af6b7` "will gain a second failure from this body edit, by construction". It did:
```
34235045216  b34af6b7  pull_request  failure  2026-09-08T13:56:02Z
34235061133  9ad48cf9  pull_request  success  2026-09-08T13:56:12Z
```
And by exactly the stated mechanism — job `pr-contract`, step "Check the body against the contract":
```
ERROR [pr-body] /tmp/pr-body.md: `## Head` does not name b34af6b, which is the head this ran on.
PR_HEAD: b34af6b752f4b4926234676ed2305a8043a972e0
```
That is a prediction that came true, not one left standing after it failed. The table's `b34af6b7` row is now a snapshot (2 failures / 4 passing runs, not 1 / 2), but the sentence immediately below the table states the omission and its cause, so the body discloses its own limit rather than mis-stating the record.

**`f20b7577`.** Runs `34225054910` and `34225202347`, both success, no failure — the claim holds. It is now no longer the *only* clean head in the table, since `9ad48cf9` is also clean; but `9ad48cf9` is clean by exactly the mechanism `f20b7577` was cited to demonstrate, so the sentence's point is confirmed rather than falsified.

**Head at time of writing:** `9ad48cf9` — 21 check runs, all `success` or `skipped`, zero red, `pr-contract` (102090519667) success. The body's `none` is correct.

**Root-cause trigger (step 11).** All four in-window failures are `pr-contract` and nothing else — verified per run (`34224594181` job list: `policy-docs` success, `wave-script` success, `pr-contract` failure; `34225039727` and `34225841799`: `failed_jobs: 1`, `pr-contract`; `34235045216`: `failed_jobs: 1`, `pr-contract`). No other gate check went red on any head of this PR, so the single check the body names and answers is the complete set. The answer given — cheaper detector `policy_lint --pr-body … --head …` (prepr step 7), standing cost a second, and a recorded finding of no countermeasure with the reasoning — is one of the two legitimate shapes `defect-root-cause.md` allows. Trigger answered.

**Step 12 — head at posting:** re-fetched, live `claude/repo-governance-audit-tgt5j4` = `9ad48cf9bb6685f306776fdfb22a3dfb907af0a8`. Unmoved; every number above is at the head I name.

## Observations (outside the delta — not blocks)

1. **`prepr.sh` skips the very check this branch changed.** Line 112 gates `check-wave-script.mjs` on `web-fix-wave.js` having changed, so my `prepr.sh` run printed `skip wave-script — web-fix-wave.js untouched` while `check-wave-script.mjs` itself was the file under change. The CI `wave-script` job is unconditional and passed at head, so nothing shipped unmeasured, and the fixer drove the script directly. Same shape as this PR's own findings, one file over.
2. **`brief_lint.mjs` exits 1 on a shallow seat**, at `b34af6b7` and `9ad48cf9` identically (`FIXTURE VACUOUS: 931dffe acceptance pins missing: [W1-G13] path: card_geometry.mjs`). Pre-existing, unchanged by the delta, and RC=0 in a full clone. The body's Limits discloses shallow-clone citation errors at head, but frames them as errors rather than as a third lane going red on a shallow seat. I did not re-derive the body's "18 citation errors" figure — that section is outside my delta scope and I am not reporting it as confirmed.
3. Cosmetic only: the new `else {` in `policy_lint.mjs` leaves `pins += 1` and its `if` block at the old indentation. Behaviour is correct and measured at both 57 (full) and 56 (shallow); flagging it only so a later reader does not mistake it for a scoping bug.