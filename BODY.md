R10-D15-GRADER: two D15 instrument follow-ups from the #2214 and #2209 reviews. Part of #2268. Both arms of that issue are delivered here. The roster group's `fixes` list is empty, so this pull request uses no closing keyword.

**(a) Bundle pins keyed on the brief.** `tools/policy/check-wave-script.mjs` armed its three bundle pins on `BUNDLE_DIMS` in `.claude/workflows/audit-find.js`. That is the same declaration the pins grade. So a driver declaring an empty set, the wrong dimension, or an extra dimension passed every pin. The pins now take their dimension set from `dev/governance/dimensions/D15.md` existing (read through the block's own `briefs` listing). They then drive the finder prompts against that set. The null-control pin now runs unconditionally. Which briefs take a bundle is a design choice, written beside the pins: D15's Inputs name one, and no other brief does.

**The same class, closed alongside (fixer.md step 8).** Rule: every pin in the file whose test is armed on a declaration in the driver it grades. Command: `grep -n "once \|armed\|not declared" tools/policy/check-wave-script.mjs`. It returns three seams:
- the bundle pins: closed by (a);
- the `ROUND_DIR` pin: closed in this diff;
- the `CURRENT` pin: closed in this diff.

Every driver now declares both `ROUND_DIR` and `CURRENT`, and `prepare_baseline.sh` declares `CURRENT_PATHS`. So an undeclared constant is now a gap rather than a pass. A positive-control pin covers each undeclared arm.

**(b) M1 restart-gap threshold.** M1 of `dev/governance/dimensions/D15.md` now defines a restart gap: consecutive `cycle_rows[].t` at least three `optimization_interval` apart. The interval comes from the download's `config` (the key sits beside `debug`, from `diagnostics.config_view`), or 30 min when absent. Three intervals is past one skipped cycle. M1 also answers the #2209 reviewer's point (c), that a fast restart leaves no gap: a tag dated between the last gap and the cycle leaves the version unknown, never the older one. `tools/audit/seat/d15_restart_gaps.py` applies the rule to a bundle and takes a `--plant` perturbation. It sits under `tools/audit/seat/`, which `tests/layout.json` already places. No gate script reads it, so it adds no closure row and needs no layout entry. The D15.md payment is spent prose inside D15's own caps, and no budget moves:
- the `DebugCollector.async_bundle` aside, replaced by the condition a finder sees (the download's `replay` is null);
- "beside the download", which the Inputs line already says;
- "real-bundle-only", which restates the line saying a synthetic-only anomaly is a lead.

## Approval

`dev/governance/dimensions/D15.md` is policy (a dimension brief). The orchestrator approves it at the merge head under mandate 6175172275 (tvofi's #201 comment: scope all, 2026-10-14 to 2026-10-28). This pull request raises no budget. D15's caps hold, and `policy_lint.mjs --budgets` prints the measured line and token counts against them.

## Head

76d4f8a2e1bdcfa4de9fec60fcd1b68731084b0a, merge base 811df3cf3362ea0c626bcfdf8bf4a3cf2937c846 (origin/main merged in once).

## Mutation proof

Each driver mutant is one `sed` on `.claude/workflows/audit-find.js`, then `node tools/policy/check-wave-script.mjs`, then the file is restored. Each was run at the head and with the merge base's copy of the check. The base copy came from `git show <merge-base>:tools/policy/check-wave-script.mjs`, written in place and restored after.

| mutant | at the merge base | at the head |
|---|---|---|
| `BUNDLE_DIMS = new Set([])` | passes (0 failed) | FAIL `once D15.md exists, its finders carry the named bundle ...` |
| `BUNDLE_DIMS = new Set(['D14'])` | passes (0 failed) | FAIL the same, plus FAIL `...and no other finder is handed the bundle (null control)` |
| `BUNDLE_DIMS = new Set(['D15', 'D14'])` | passes (0 failed) | FAIL `...and no other finder is handed the bundle (null control)` |
| relative-path refusal disabled (`if (false) throw`) | FAIL `a relative bundle path is refused before Prepare (declared)` | FAIL `a relative bundle path is refused before Prepare (D15 brief)` |
| `const ROUND_DIR =` to `let ROUND_DIR =` (undeclared to the reader) | passes (0 failed) | FAIL `both drivers write where fold_ledger.py reads (not declared)` |
| `const CURRENT = [` to `let CURRENT = [` | passes (0 failed) | FAIL `audit-find.js CURRENT is prepare_baseline.sh's CURRENT_PATHS (not both declared)` |

Predicate mutant: in the head's check, `const bundleDims = ['D15'].filter(...)` was replaced by `const bundleDims = []`, and run against the empty-`BUNDLE_DIMS` driver. It passes with 0 failed. So the brief key is what kills that mutant.

Restart-gap reader: `GAP_INTERVALS = 3` was changed to `2`. The 3600 s arm (one skipped cycle) then reads `restart_gaps=1`, against 0 unmutated.

## Null control

- With the driver unmodified, `node tools/policy/check-wave-script.mjs` reports 0 failed at the head. At the merge base it also reports 0 failed, with one pin fewer: the undeclared-arm control is new.
- Restart gaps on the synthetic week: `restart_gaps=0` unplanted. With one skipped cycle (`--plant 3600`) it also reads 0.

## Figures

Run at the head with the seat interpreter first on PATH (python 3.14). `$B` is the output of `PYTHONPATH=tests/hastub:tests python3 tools/replay/dbg_bundle_gen.py --days 7 --out $OUT`, i.e. `$OUT/bundle.json` (336 cycle rows, 1800 s apart, no `config`). `$W` is the same bundle wrapped as a download with `data.config.optimization_interval = 120`.

- `node tools/policy/check-wave-script.mjs` rc=0, 0 failed. Each mutant's line is in the table above.
- `PYTHONPATH=tests/hastub:custom_components python3 tools/audit/seat/d15_restart_gaps.py --bundle $B --plant <S>`, reading `restart_gaps` (interval 1800 s, source default): S=0 gives 0; S=3600 gives 0; S=5400 gives 1; S=12054 gives 1 (the owner's upgrade gap).
- The same command with `--bundle $W` (interval 7200 s, source config): S=12054 gives 0; S=21600 gives 1. At a 120 min interval the owner's gap is under three intervals, so M1 reads the version as unknown, never the older one.
- The same command on a bundle with no cycle rows: rc=2, `REFUSED fewer than two cycle rows`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, with RUN `tests/entities.py`.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh` rc=0: `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` rc=0.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` rc=0, `Architecture score: dS +0.0000 NULL`.
- `node tools/policy/policy_lint.mjs` rc=0. `node tools/policy/policy_lint.mjs --budgets` rc=0, and it prints D15.md's lines and tokens against its caps.
- `node tools/policy/brief_lint.mjs` rc=0. `node tools/policy/rules_sync.mjs --check` rc=0. `python3 -I tools/audit/seat/tmp_paths.py --check` rc=0.
- `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is empty.

## Red checks

none at handoff. CI's `wave-script` lane grades this head with the base's copy of the check, so the new pins first run in CI after this merges. The figures above are the head's own copy. R10-TICK-DRIVERS edits `audit-find.js` and merges second, so it re-runs this check (architect note 8).

## Forward-carry

`dev/governance/dimensions/D15.md` M1, in this diff, is the destination for (b). The reader `tools/audit/seat/d15_restart_gaps.py` is for the D15 dispatch prompt to name. The orchestrator writes that prompt, and D15.md has 1 token of headroom, so it cannot name the reader itself.

## Friction

fixer.md#18: contradiction: step 18 puts a rerunnable harness in dev/audit/harnesses/, but tests/harness_headers.py reads that directory, so a new file there is a predicted closures red that only a Linux recording clears; this one went to tools/audit/seat/ instead.
budgets-D15: cost: D15.md sat at 0 tokens of headroom, so a 1-sentence rule cost three unrelated prose cuts.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
