R10-FLY-INSTRUMENTS-SPLIT (owner order tvofi 2026-10-28, prompt-cache gap 6). `tools/audit/seat/INSTRUMENTS.md` was one 83,235-byte file (`wc -c` at the merge base) that seats read whole. It is now a short index: the guide's own prose, kept as it was, and one linked line per instrument giving its name and the opening clause of its own entry. Each of the 76 entries (`grep -c '^- \`'` at the merge base) moved verbatim to `tools/audit/seat/instruments/<name>.md`, under a `# \`name\`` title line.

**Policy status: not policy.** No `POLICY_GLOBS` pattern in `tools/policy/policy_lint.mjs` matches `tools/audit/seat/`, `git ls-files | node tools/policy/policy_lint.mjs --corpus-filter` prints no `audit/seat` path, and neither `dev/governance/config/policy_budgets.json` nor `corpus_excluded.json` names it. `corpus_tokens` is unchanged (see Figures). The guide calls itself "a usage guide, not policy". So the owner's pre-merge approval for policy changes does not apply.

**Citations.** `git grep -n INSTRUMENTS -- . ':!tools/audit/seat/INSTRUMENTS.md'` finds every in-tree citation. Each one names the file `tools/audit/seat/INSTRUMENTS.md` (or just `INSTRUMENTS.md`), and that file still exists and links every entry, so each citation still resolves:
- CLAUDE.md's "instruments guide", `dev/README.md`, `dev/programme/HANDOVER.md`, `tools/pr/README.md` (pinned by `tests/entities.py`'s "names the gate lease and the seat instruments" check, unchanged), `sweep_template.md`, roster `files` lists and the `gh_read.py` / `cloud_dispatch.py` comments all resolve.
- Triage and RCA records that quote line numbers (`s6-batch22.md` "lines 236-240", `s6-batch44.md` `:516`) are records of a past tree. They stay as written (fixer step 10).
- `INSTRUMENTS:` in the round-4 harness headers is a header keyword, not this file.
- The new files sit under `tools/audit/`, which `tests/closure.py`'s INERT list covers by prefix, so `tests/entities.py` has nothing to classify.

**The check.** I extended `tools/audit/seat/selftest_wiring.py --check` instead of adding a tool. That step already runs on every pull request in `instrument-self-tests`, and the scoped gate would select nothing here because `tools/` is INERT. It now also refuses four cases: an index line whose file is gone, a file linked twice or by no line, a line whose name does not match its file's entry, and a missing index. The only change to entry text is one added paragraph in `instruments/selftest_wiring.py.md` documenting the new rule (second commit). The first commit is the pure move.

Alternatives considered: a new linter (refused by the brief, and it would be another step to wire); a check in `tests/entities.py` (the gate never selects it for an INERT-only diff, so it would miss exactly the pull requests that touch the guide); `policy_lint.mjs` (it lints policy, which this is not).

Relative wording inside entries (`merge_pr.sh`: "`merge_train.py` below"; `tick_loop.sh`: "the andon, below") stays verbatim. It still holds in the index, which keeps the original order.

## Head

89078deb10478e265c2b35fccd23574746c8b848

## Mutation proof

- Owner's mutant, on the real tree: deleting the `push.sh` index line (`sed -i '/(instruments\/push.sh.md)/d' tools/audit/seat/INSTRUMENTS.md`) makes `python3 -I tools/audit/seat/selftest_wiring.py --check` exit 1 with `UNINDEXED tools/audit/seat/instruments/push.sh.md: no index line links it` / `selftest_wiring: 1 index gap(s)`. Restored, it exits 0.
- Code mutant: replacing the `UNINDEXED` append in `index_gaps()` with `pass` makes `--self-test` report `26 checks, 3 failed`: `FAIL deleting one index line leaves its file unindexed`, `FAIL an entry file no line links is refused`, `FAIL --check exits 1 on an index gap when every file is wired (rc=0)`. Restored, it reports `26 checks, 0 failed`.

## Null control

- The unmutated tree: `python3 -I tools/audit/seat/selftest_wiring.py --check` exits 0 with `99 self-testing, 99 wired, 0 unwired` and `0 index gap(s)`. In `--self-test`, the arm "a consistent index and entry set has no gap (null control)" passes.
- Move proof: a scratch script rebuilds the old file from the first commit's tree. It removes the index's one added sentence, swaps each linked line for its entry file's body minus the title, and the result is byte-identical to the merge base's `INSTRUMENTS.md` (`cmp` exits 0). Its null control: change `(#678)` to `(#679)` in `instruments/push.sh.md` and the rebuild differs (`cmp` exits 1).

## Figures

- `wc -c tools/audit/seat/INSTRUMENTS.md`: 83235 at the merge base b6f6ceca4, 12060 at the head. The index is what a seat now reads whole.
- Entries: `grep -c '^- \`' tools/audit/seat/INSTRUMENTS.md` at the merge base is 76. `ls tools/audit/seat/instruments | wc -l` at the head is 76, and `--check` reports 0 index gaps, so the two sets match one-to-one.
- `node tools/policy/policy_lint.mjs --budgets`, line `corpus:`: `~66398 tokens, cap 66434` at the merge base and the same at the head (flat; the guide is outside the corpus).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Every changed file is INERT; this is a scoped zero, not `MODE: FULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python tests/entities.py`: `ALL 2467 ENTITY CHECKS PASSED`; `tests/harness_headers.py` under the same interpreter: `ALL 112 HARNESS HEADER CHECKS PASSED` (system python3 3.11 lacks `voluptuous`, an environment gap).

## Red checks

none

## Forward-carry

none

## Friction

none
