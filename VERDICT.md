Fix review: merge 47c5b0ff0075b03342d6844aaf01cbb5a8aedc28

bus-nonce: 1cc073cda8d629d363913807953ee4f9

Round: 1 (first review of this PR).

## What was measured, and by whom

The pre-study committed no harness, and the fixer's `lane-proof.sh` is the
fixer's own instrument (disclosed as such in the body). Per contract step 9 I
built my **own** stand-in instead: a scratch tree carrying the head's
`tools/coverage/coverage_tree.sh` verbatim, the real package, a stubbed
`tests/run.sh`, and six stub scripts of **my own** module mapping (features →
services+config_flow; boost → debugger import plus `store_keys`/`_dumps` body
calls; plan_view/doc_claims as the HPO_PLANDATA pair; entities →
coordinator+drift; finite_boundary → defrost). python 3.11.5, coverage 7.16.0,
macOS. Evidence: `evidence/lane-proof.txt`, run logs and per-script JSONs
beside it.

## Adversarial questions

1. **Same recording set — RESULT: PASS.** `W5P_LANES=1`, `2`, `3` and unset
   (new default = 3), stage `fast`, fresh `W5P_WORK` each: four `coverage.json`
   outputs identical as per-file `executed_lines` sets — 75 files, 5102
   executed lines (my stubs; the fixer's 5159 is their stand-in's, same shape,
   and I do not confirm their exact count — mine is the independent
   reproduction of the property, not the number).
2. **Failing-first arm — RESULT: PASS.** At merge base `origin/main`
   `6918cb4b2`: `W5P_LANES=3 … coverage_tree.sh fast` → `W5P_LANES must be 1
   or 2`, exit 2 (refusal precedes any measurement). Head accepts 3 (ran,
   three lanes, exit 0); `0`, `4`, `abc` all refused with the new message,
   exit 2.
3. **Mutant killed — RESULT: PASS.** Boost lane's `measure "$BOOST"` mutated
   to `measure ""` in the stand-in copy: `coverage.json` differs from the
   serial reference — `debugger.py` loses 6 lines only the boost stub
   executes, no line gained. Restored and re-run: equals serial again.
   Honestly recorded: my **first** mutant attempt survived, because my
   original stub set only imported and `coordinator`/`services` transitively
   covered `debugger`/`snapshots` — a harness flaw, diagnosed per-script and
   fixed, not a lane flaw; it is the same trap the fixer's body flags
   ("stub imports chosen for that, measured not assumed").
4. **No budget, workflow or check touched — RESULT: PASS.** The whole
   three-dot diff is exactly two files: `tools/coverage/coverage_tree.sh`
   (+30/−13, the lane case and comment only) and `dev/programme/delivery/2130.md`
   (the delivery row). No `.github/`, no `*_budgets.json`, no VERSION,
   manifest, RELEASE_NOTES or claim-file line.
5. **No (vi-a) trace — RESULT: PASS.** `grep -i 'short-replay|short_replay|
   RECORDED_ARGV|HPDR_SHORT'` over the whole diff: no match. The refusal is
   argued in the body with its own measurement (301 lines / 14 files,
   uniformly only-full); the refused work lives off-tree as stated.

## Figures re-derived (cheap ones mine, heavy ones CI's)

- `closure.py select --diff origin/main` → `MODE: SCOPED -- 0 script(s) run,
  33 scoped out` — matches the body verbatim.
- `tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `tests/env_drift.py --claims-only origin/main` → `claims hygiene:
  origin/main ok`; claim files byte-identical base→head.
- `git merge-tree --write-tree origin/main HEAD` → exit 0, no conflicts, no
  claim files involved.
- The ~11-minute wall prediction and the 75-file/5159-line fixer-stand-in
  count are **CI's / not independently confirmed** — my stand-in confirms the
  property (identical sets) with its own count (75 files, 5102 lines).

## Contract steps

- Step 4: no fixture touched, claim files identical — nothing to claim.
- Step 5: VERSION/manifest/notes untouched.
- Step 6: the class is one seam — the `W5P_LANES` dispatch; every other value
  refuses, and `1`/`2`/`3` all re-measured identical.
- Step 11: head check-runs read from the API — none red; `browser`,
  `fast (3.14)`, `coverage` in progress at review time, none concluded red.
- Step 12: head was `47c5b0ff0075b03342d6844aaf01cbb5a8aedc28` at measurement
  and re-verified immediately before publishing.

Head measured: 47c5b0ff0075b03342d6844aaf01cbb5a8aedc28
(authored code head ae47d8ca06c56102e92461279183ffd611dcae15, one commit below,
delivery row only).
