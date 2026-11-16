Fix review: blocked 5fd0fc537375027f219394c11994cf1239624271 class-open: d1-inputs still omits the configured entity slot CONF_COMPRESSOR_FREQ_SENSOR, and the enumerator survivors of round 1 are unchanged at this head

bus-nonce: 75a17dda374e864ed799d23892d6727b
pending-ci: gate

Round 2 (delta scope over the reviewed head 673af8e9896e4da83ac093b7ac46143d16305a8a). Measured from a detached worktree at 5fd0fc537375027f219394c11994cf1239624271, merge base 6aa7ddc71216c4bc357db0097839ce40ff94e263.

## Block

The delta from 673af8e9896e4da83ac093b7ac46143d16305a8a to 5fd0fc537375027f219394c11994cf1239624271 is a merge of origin/main and nothing else. It does not change `tools/audit/enumerate.py` or any dimension brief: `git diff 673af8e9 5fd0fc53 -- tools/audit/enumerate.py dev/governance/dimensions/D1.md` is empty. On this pull request's own paths, the delta touches only `dev/audit/config/scopes.json`, `dev/governance/config/policy_budgets.json`, `tests/layout.json` and `tools/ci/selftest_closures.json`, and each of those is main's side of the merge (`ev/delta_checks.txt`). Neither ground of the previous verdict is resolved. I re-ran both at this head:

1. `d1-inputs` is still one short of its population. `enumerate.py d1-inputs` exits 0 and prints 50 lines (`ev/d1_inputs_head.txt`). `const.py:1265` still declares `CONF_COMPRESSOR_FREQ_SENSOR`, and the universe does not include it. Its only frequency line is `CONF_COMPRESSOR_FREQ_ENTITY`, which is a different slot at `const.py:1260`. What is owed is unchanged from round 1: put the slot in the universe by a rule that does not depend on the name's suffix, and add a self-test arm that fails without it.
2. The self-test still leaves the round-1 survivors standing. I re-planted M2 (`or k in LIFE_CALLS` removed): `SELF-TEST passed (134 arms)` at rc 0, while `d1-lifecycle` fell from 41 lines to 16 (`ev/mutant_M2_head.txt`). The enumerator is byte-identical to the one round 1 measured, so the other nine survivors named there (M1, M3, M4, M5, M8, M12, M18, M25, M27) stand on the same code. I did not re-run them one by one.

## Findings

- Follow-up: round 1's finding stands unchanged. `COMMON.md` states no rule that a finder reports examined over a universe, so each brief restates the sentence. Carry: dismissed: the group owning COMMON.md is carries-open and carry_audit lists no live target; the body's payment (4) already records the alternative and the saving is a sentence per brief

## Evidence

- Head re-read: `git ls-remote origin refs/heads/fix/r11-pre-briefs-census` prints 5fd0fc537375027f219394c11994cf1239624271 (`ev/HEAD.txt`).
- `git merge-tree --write-tree origin/main 5fd0fc53`: exit 0, tree 09623e578900dd445f1d13185e0aba20c96c76b3, no conflict (`ev/merge_tree.txt`). The merge base equals origin/main 6aa7ddc712.
- `git diff 6aa7ddc712...origin/main -- dev/governance/roles/` is empty, so the frozen contract is current. The three-dot diff does not touch `VERSION`, `custom_components/`, `RELEASE_NOTES.md` or `tests/golden/` (`ev/delta_checks.txt`). The delta contains no production code, so the scope is not widened.
- The `policy_budgets.json` delta is the merge resolution: `corpus_tokens` 70678 -> 67155, D11 rows from main's rewrite of D11, and the retired `nudge.md` rows removed. These match the merge commit's stated `--budgets` figures. I did not re-run `policy_lint --budgets` at this head.
- RESULT self-test at the head: `SELF-TEST passed (134 arms)`.
- CI: `merge_train.py classify 5fd0fc537375027f219394c11994cf1239624271 --pr 3625` read `WAIT ... pending: gate red: none` (rc 3) on every run from 02:33:34Z to 03:05:13Z (`ev/classify_1.txt`, `ev/classify_poll.txt`). No required check was red, so no `## Red checks` answer is owed at this reading. The block above does not depend on CI.
- `carry_audit.py check` was run on this verdict as the sole comment, with an empty body file. The packet's own `carry_audit at the head` already reads the body: 9 routed, 0 unrouted.
