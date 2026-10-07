Root-cause analysis for #1985, the friction key `root-cause-unanswered`. It adds `dev/audit/rca/R9-RCA-1985.md`, its raw evidence under `dev/audit/rca/1985/`, and one `_rca` entry in `tools/audit/bugclasses.json`. It changes no production, workflow or policy file.

**Process state: (c).** I reproduced the count: 12 PRs and 17 verdicts in `v6.7.16..origin/main`. 13 of the 17 verdicts name a lane that tests the fix's own code (typing, mutation, closures, fast, env-matrix, CodeQL and others). The other 4 are body-only debt. The cause is that the body is written at the handoff, when the fixer pushes, and CI's reds arrive after it. `fix-review.md` step 11 sends every red the body does not answer to the one word `root-cause-unanswered`.

The cheaper detector already exists: `pr-contract` with its re-run workflow. It fired on 17 of 17 entries, 11 before the verdict and 6 when the `Tests` workflow completed. So no check is built. I propose one change to the owner: split out a separate `red-check` verdict class. That is a policy change, so it is not landed here.

Refs #1985. This does not close the issue, because the grammar split waits on the owner.

## Head

bb28e9cb83667c96e85cc20c5c533cd2b9cae3bb, measured against `origin/main` 3910026e on 2026-10-07.

## Mutation proof

n/a: no production or check code changes. The change is an analysis document, its evidence files and one register entry. `python3 tools/audit/fold_ledger.py check` reads the register entry, and it reported `0 violation(s)` with 97 rca entries.

## Null control

n/a: no detector is built. I did run a control on the measurement itself. The default `check-runs` listing (`filter=latest`) showed `pr-contract` green at #1993 and #1996. With `filter=all` and the per-attempt API, each head shows three failed attempts. The analysis uses the `filter=all` reading. Section 2 of the document records this trap.

## Figures

- 12 PRs / 17 entries, 57 merged: `GITHUB_TOKEN=$(gh auth token) node tools/policy/policy_lint.mjs --stats --since v6.7.16` (output in `dev/audit/rca/1985/stats_v6.7.16.txt`)
- 17 entries, enumerated independently with 0 API failures: section 6 of `dev/audit/rca/R9-RCA-1985.md` (`entries.txt`, `seq.txt`)
- 12/17 bodies passed `pr-contract` at the first run; 11/17 had `pr-contract` failed before the verdict; 6/17 verdicts came before `Tests` completed: `gh api "repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs?filter=all&per_page=100" --paginate` (`timeline_all.txt`)
- 11/370 verdict-carrying PRs before 2026-10-02 against 27/97 from then: every `Fix review:` first line on the 501 PRs merged since 2026-09-16 (`verdicts_since_0916.txt`)
- `python3 tools/audit/fold_ledger.py check`: 0 violation(s)
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `GATE_SCOPE=auto bash tests/run.sh`: `MODE: SCOPED -- 0 script(s) run, 31 scoped out.`

## Red checks

none

## Forward-carry

`dev/audit/rca/R9-RCA-1985.md` section 5 records two items:

- The `red-check` grammar split. It is policy, so it is proposed to the owner and not landed.
- The `web-fix-wave.js:489-495` route. It sends `root-cause-unanswered` to a root-cause seat with no body-repair round. This is owed by whoever next edits that script, and it is recorded for the orchestrator's record.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
