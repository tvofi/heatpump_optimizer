R10-FLY-INSTRUMENTS-SPLIT (owner order tvofi 2026-10-28, prompt-cache gap 6). `tools/audit/seat/INSTRUMENTS.md` was one 83,235-byte file (`wc -c` at the merge base) that seats read whole. It is now a short index: the guide's own prose, kept as it was, and one linked line per instrument giving its name and the opening clause of its own entry. Each of the 76 entries (`grep -c '^- \`'` at the original base b6f6ceca4; 79 after the conflict merge, see Head) moved verbatim to `tools/audit/seat/instruments/<name>.md`, under a `# \`name\`` title line.

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

ddc4f1fe7249428598dacf6174d33611a4f33765

Conflict merge (fixer step 6, after the handoff): `origin/main` at 9071062b0 (2026-10-29T05:10Z) merged into ceb41a60b, never rebased. Main had touched `tools/audit/seat/INSTRUMENTS.md` since the split's base (#2916 beatd, #2930 owed_unactioned, the cloud-seat pointer-event and orphans-classifier commits); the content conflict is resolved as a union, the split's index taking main's entries:
- `owed_unactioned.py` (added on main): new `instruments/owed_unactioned.py.md`, index line after `orchestrator_tick.py`, before `plan_audit.py` -- main's position.
- `beatd.py` (added on main): new `instruments/beatd.py.md`, index line after `heartbeat.sh`.
- `beatd_shims/git` (added on main): new `instruments/beatd_shims_git.md` (the `shims_seat-python.md` naming for a path), index line after `beatd.py`, before `train.sh`.
- `cloud_dispatch.py` and `cloud_relay.sh` (changed on main): main's bullets replace the base bullets inside their entry files.
Each new entry file is main's bullet verbatim under a `# \`name\`` title. The resolution delta against ceb41a60b is those three files, the two edited entries and three index lines; no other file of the split changed. Read-back: rebuilding the flat guide from the merged index (each linked line swapped for its entry body minus the title) and `diff`ing it against `origin/main`'s `INSTRUMENTS.md` shows exactly the split's two intended additions (the index sentence, the `selftest_wiring.py` paragraph) and nothing else; null control: changing `default 1 h` to `default 2 h` in a copy of `instruments/owed_unactioned.py.md` makes the same rebuild differ.

Previous head: ceb41a60bfe094903a2aac8b5f3f07af4cef83a4 (89078deb1 plus a merge and the delivery row).

## Mutation proof

- Owner's mutant, on the real tree: deleting the `push.sh` index line (`sed -i '/(instruments\/push.sh.md)/d' tools/audit/seat/INSTRUMENTS.md`) makes `python3 -I tools/audit/seat/selftest_wiring.py --check` exit 1 with `UNINDEXED tools/audit/seat/instruments/push.sh.md: no index line links it` / `selftest_wiring: 1 index gap(s)`. Restored, it exits 0.
- Code mutant: replacing the `UNINDEXED` append in `index_gaps()` with `pass` makes `--self-test` report `26 checks, 3 failed`: `FAIL deleting one index line leaves its file unindexed`, `FAIL an entry file no line links is refused`, `FAIL --check exits 1 on an index gap when every file is wired (rc=0)`. Restored, it reports `26 checks, 0 failed`.

## Null control

- The unmutated tree, at the merged head ddc4f1fe7: `python3 -I tools/audit/seat/selftest_wiring.py --check` exits 0 with `101 self-testing, 101 wired, 0 unwired` and `0 index gap(s)` (99 at 89078deb1; main's `beatd.py` and `owed_unactioned.py` add two). Deleting the merged-in `beatd.py` index line makes it exit 1 with `UNINDEXED tools/audit/seat/instruments/beatd.py.md`; restored, `git diff --quiet` holds. In `--self-test`, the arm "a consistent index and entry set has no gap (null control)" passes.
- Move proof: a scratch script rebuilds the old file from the first commit's tree. It removes the index's one added sentence, swaps each linked line for its entry file's body minus the title, and the result is byte-identical to the merge base's `INSTRUMENTS.md` (`cmp` exits 0). Its null control: change `(#678)` to `(#679)` in `instruments/push.sh.md` and the rebuild differs (`cmp` exits 1).

## Figures

Re-taken at the merged head ddc4f1fe7 against merge base 9071062b0 (`origin/main`'s tip, 2026-10-29T05:10Z).

- `wc -c tools/audit/seat/INSTRUMENTS.md`: 87231 at the merge base 9071062b0, 12425 at the head (83235 / 12060 at the original base b6f6ceca4 / head 89078deb1). The index is what a seat now reads whole.
- Entries: `grep -c '^- \`' tools/audit/seat/INSTRUMENTS.md` at the merge base is 79. `ls tools/audit/seat/instruments | wc -l` at the head is 79, and `--check` reports 0 index gaps, so the two sets match one-to-one.
- `node tools/policy/policy_lint.mjs --budgets`, line `corpus:`: `~66398 tokens, cap 66434` at the head (flat; the guide is outside the corpus).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Every changed file is INERT; this is a scoped zero, not `MODE: FULL`.
- `python3 -I tools/audit/seat/selftest_wiring.py --self-test`: `26 checks, 0 failed`.
- `PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python`: `tests/structure.py` `STRUCTURE RATCHET PASSED`; `tests/entities.py` `ALL 2470 ENTITY CHECKS PASSED`; `tests/harness_headers.py` `ALL 112 HARNESS HEADER CHECKS PASSED`; `tests/closure.py selftest` `ALL 117 closure shrink pins PASSED`; `tests/layout.py` `layout self-test: ok`; `tests/env_drift.py --claims-only origin/main` `claims hygiene: origin/main ok`.

## Red checks

none. The merge resolved a content conflict, not a red check; every run_always script and the instruments self-test above is green at ddc4f1fe7.

## Forward-carry

none

## Friction

none
