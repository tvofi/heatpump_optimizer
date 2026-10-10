Fix review: merge b4b8beda40fd5c00594398f7be8cbdabaab11cd3

Round 3 on #2114. Rounds 1 and 2 established the fix is sound (head block
`ALL 14 PASSED`, deletion reproduces the body's `1 of 14 FAILED`,
`gain=+0.000000`; merge base red on Accelerate, head green) and that the
carry destination `dev/programme/carries/carry-201.json` is the one
`finding-propagation.md` itself names for a stage with no live roster group.
Round 2 blocked on `fast (3.14)`: five retired-path guard refusals from the
carry edit's own two lines. This round measures only the repair.

RESULT guard: `python3 -I tests/layout.py --guard --base 969c3a5c84d0`
(the merge base of this head) reads `layout: GUARD: 0 refusal(s) against
969c3a5c84d0`, EXIT=0. The check that blocked is green at the head, run by
this reviewer, not taken from the body.

RESULT carry diff: `git diff 4f0bde165 b4b8beda4 --
dev/programme/carries/carry-201.json` is ONE hunk, 4 changed lines (2 -, 2 +),
and the only deltas are the five path tokens -- `.claude/workflows/brief_lint.mjs`
-> `tools/policy/brief_lint.mjs`; `docs/decisions/0009` ->
`dev/governance/decisions/0009-agent-identities-for-author-and-approver.md`;
`tools/audit/briefs/D13.md` -> `dev/governance/dimensions/D13.md`;
`tools/audit/round5/D13/seat-a/dora_cfr.py` ->
`dev/audit/rounds/round5/D13/seat-a/dora_cfr.py`; `tools/audit/briefs/D11.md`
-> `dev/governance/dimensions/D11.md`. Every other byte of the entry --
finding, control, voiding perturbation, remeasure instruction, the `carries`
array -- is identical. Nothing was dropped. `node tools/policy/brief_lint.mjs`
on the file: `0 error(s), 0 warning(s)`, exit 0.

RESULT successor paths exist: `git cat-file -e` at the head confirms all five
(the reviewer ran all five, not two) -- plus the two spot-checked read back
above. The carry cites no path missing from the tree.

RESULT reviewed behaviour untouched: `PYTHONPATH=tests/hastub python3
tests/features.py` at the head, exit 0, `ALL 3986 FEATURE CHECKS PASSED`,
two-zone arm `RESULT f21_p3_two_zone=1 j_plain=110.436632
j_continuation_off=111.267093 continuation_gain=+0.830461
j_seeded_half_price=110.129674`; single-zone null `+0.000000`, `67.730056`
both arms -- round 1's numbers, unchanged. (The brief's note about a
macOS-local features.py closure red: the pre-fix platform red; at this head
the script itself is green on this Accelerate box.)

RESULT red checks: the commit's own check-runs at b4b8beda4 list NO red
conclusion. `fast (3.14)` is success at this head; the body's `## Red checks`
names it, the check-run id, the five refusals and the repair with the
cheaper-detector answer (the guard itself fired correctly -- the defect was
the branch's edit, not a detection gap). Several runs (closures, coverage,
Analyze (python)) were still in progress when read; none red. No
root-cause-unanswered.

Head-moved rule satisfied: `git ls-remote origin refs/heads/fix/r9-blas-kernel-red`
read b4b8beda40fd5c00594398f7be8cbdabaab11cd3 immediately before publishing,
and the PR API's head field agrees.

Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2114c/evidence (guard-head.log,
carry201.diff, carry-lint.log, paths-exist.txt, features-head.log,
check-runs-head.txt, head.txt naming the 40-hex head).

bus-nonce: e9aa3248e9ede1c2c594e011fb1fa979
