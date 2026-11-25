Fix review: blocked e60d25b9bdf1533647cace5cb190901109d8829c mutation-vacuous: ledger_unread window filter survives (check_scopes.py:1427 win = rows unfiltered)

bus-nonce: 8f5a11f8a7bcd0b24b526d29b3bdd3e3

Round: 2. This is a delta review over the reviewed head b15a9f2cadb869915afbd317c08d1acd900259d2: `git diff b15a9f2c e60d25b9`, which is the repair 9ff0d214 and 2aa21692 merged onto b15a9f2c. e60d25b9 merges no main commit, so the delta has no main resolution to check.

## Block

- mutation-vacuous: the window filter in the new `ledger_unread` (`tools/audit/check_scopes.py:1427`, `win = [r for r in rows if r.get("t") and a <= at(r["t"]) < b]`) can be replaced by `win = [r for r in rows if r.get("t")]`, so it reads the whole ledger. After that change every self-test still passes. The whole `check_scopes.py --repo . --self-test` exits 0 (`ev/mutants.txt`, D5), and `ledger_round_self_test` holds all 8 arms (`ev/ledger_arms.txt`).
  - Why the arms miss it: every arm puts the class rows (`whole`, 2026-01-01T12:00:00Z) inside the graded window. No arm has a class whose only row falls outside the window.
  - What it breaks: `tokens.tsv` is cumulative, because `collect` runs daily over every transcript. With the filter gone, a cloud row from any other round satisfies the "seat class with no row" check. `round_ledger_gaps` would then print no `LEDGER unread` for a graded window with no cloud row. That is the same silent pass review/3898 blocked in round 1, now one line from regressing unseen.
  - Owed: one arm where a seat class has a row only outside the window, for example the cloud row dated before tag v9.0.0. It must print `seat classes with no row in the window: cloud`.
  - The other new lines are pinned. D2 (drop the missing-classes clause), D3 (drop the unkeyed clause), D4 (drop the orchestrator exemption), D6 (drop the unread print) and D7 (return `[]` on unread, losing the refusal) are each killed by the intended arm (`ev/mutants.txt`, `ev/ledger_arms.txt`).

## Findings

none

## Evidence

- RESULT: head reviewed e60d25b9bdf1533647cace5cb190901109d8829c (`ev/HEAD.txt`). `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- RESULT: `git merge-tree --write-tree origin/main e60d25b9` rc=0, no conflict (`ev/merge_tree.txt`), with the driver line `LEDGER-MERGE: resolved tests/closures.json`. The head is 79 commits behind origin/main 7aa6020f2a and merges cleanly.
- RESULT: the round-1 block's axis, dispatch paths that write the seat key, is resolved.
  - Rule: `render` now ends the first line of every event with the key, whether the event is the `publish_seat` stub or the whole prompt (`cloud_dispatch.py:421-428`). Self-test arms pin this per role and for the group seat.
  - Enumeration check: I swept `tools/` and `.claude/` with git grep, through a scout subagent. Patterns: `CLOUD (REVIEWER|FIXER|PROBE|DESIGNER)`, `environment_id`, `job_config`, `RemoteTrigger`, `PAYLOAD.json`, `seat for PR`. No cloud event or payload builder exists outside `cloud_dispatch.py`. The other hits are readers (`cloud_relay.sh:844`, `review_packet.py:673`), self-test fixtures (`cloud_relay.sh:2102`, `owed_watch.py:355-369`) or docs. The rule's output matches the stated set.
  - Residue: the local spawn is named by category, a host session's Agent tool. Its `seat=-` row now prints `LEDGER unread`, through D3 and D6, both killed.
  - Real transcript: this seat's own transcript has the dispatch event as its first `type=user` message, with no wrapper, and `HEADER` is `re.M`. So a keyed stub would be read. This seat's stub has no key because it was rendered by main's pre-PR code.
- RESULT: the round-1 surviving mutants M4 (`if first and` dropped) and M5 (`max(d["t"], stamp)` to `stamp`) are now killed by the two new token_ledger arms (`ev/mutants.txt`).
- RESULT: D1b, the key applied only when `not publish_ref`, is killed by 3 cloud_dispatch checks.
- RESULT: self-tests at the head (`ev/selftests.txt`): token_ledger 18 passed, 0 failed; cloud_dispatch 188 checks, 0 failed; check_scopes `SELF-TEST passed`.
- CI: the earlier reds are answered.
  - `codeql / Analyze (javascript-typescript)` was red at b15a9f2c, a SARIF upload server error answered in `## Red checks`. It is success at this head.
  - `gate` failure job 139469039562 is the provisional gate. Its log reads `FAIL run(s) [45688465651] at this head are still being judged; their gate decides`, and classify reads `gate red: none`.
  - `pr-contract` is skipped behind that gate.
  - `tests / nightly-status` failure is not in the owed-reds set.
  - `merge_train.py classify e60d25b9... --pr 3898` read WAIT, `pending: gate red: none`, at every poll from 20:02 to 20:10Z (`ev/classify.txt`). I did not wait for GREEN, because the verdict blocks on tests.
- Note: stale-body: `## Head` names merge base e3cb5c01. The head's merge base with main is 0e1eba2b.
- The selftest_closures.json delta (beat-job-rows reads `selftest_absorb.py`; `carries/**`) is instrument scope, which CI checks. It does not widen this review.
