Fix review: blocked 0812e8b2e4dfad56459eb2b11eca80de9f98c673 mutation-vacuous: s3 stale-file predicate `if stale.stem not in batches` -> `if True` (every item file unlinked, the answered current batches' too), observe `seen.get("max", cost)` -> `seen.get("max", 0)` (equivalent: GitHub's cost is never negative)

bus-nonce: f1c1d967cb71347649baf8f77729a116

## Block

Round 2 (a delta round over the reviewed head 273e5ece996438c799c6d246dc54f89e3f888e93). Head measured: 0812e8b2e4dfad56459eb2b11eca80de9f98c673, the same head the body names. This is tooling only: the diff has no `custom_components/` line, so nothing widens the scope.

The delta adds `s3`'s stale-file removal at `tools/audit/seat/corpus_mirror.py:560-562`. Its keep side is unpinned. I mutated `if stale.stem not in batches:` to `if True:`, so every `graphql/items/*.json` is unlinked, including the files of batches already answered. The mutant survives `python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants` with rc 0 and no FAIL (ev/reviewer-mutants.txt).

This mutant is not equivalent. `Mirror.each` never reads a unit again once the cursor holds it (`if i in done: ... continue`). So a pass paused partway through and then resumed would delete the files of every batch answered before the pause and never fetch them again. The same happens on any later pass under the same partition: the cursor reads `ok` and the directory is empty. The suite already has this scenario in the case "graphql floor: a reset an hour or more away pauses at the cursor instead of sleeping, and the run after it completes", which pauses and then resumes, but that case never counts files.

I added one conjunct to that case: the `ghour` item-file count must equal the cursor's batch count. With that probe, the head passes (rc 0) and the mutant fails it (rc 1, `FAIL graphql floor: ...`) (ev/unlink-all-demo.txt, driver ev/unlink-all-demo-driver.py). The re-cut needs a case of that shape, plus an in-tree mutant for the keep side.

The new `partition files` case pins only the delete side: the reviewer mutant that globs nothing is killed, as is the in-tree `partition files` mutant.

The second survivor, `observe`'s `max(seen.get("max", cost), cost)` -> `max(seen.get("max", 0), cost)`, differs only for a negative cost. `observe` does not refuse a negative cost, but GitHub never answers one, so I read it as equivalent. It is listed here because survivor_list.py reads every survivor the driver reports. The fixer can drop it at the source or leave it.

## Findings

- Follow-up: none beyond the block above. The previous verdict's findings are each resolved at this head (see Evidence). Carry: dismissed: no finding outside the block, which the re-cut settles in this PR

## Evidence

- Setup: `cloud-setup.sh --check` printed OK. I rendered the role pack from this session's main checkout. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` at the PR worktree is non-empty (174 lines), so the head's own copy of the role contract is older than main's. I used main's, through the role pack.
- Review packet: it refused with `introduced-red: unreadable: ... instrument-self-tests ... in_progress`. That was CI pending at render, not a red.
- Merge: `git merge-tree --write-tree origin/main 0812e8b2e4` exited 0 with no conflict (ev/merge-tree.txt). The head is a merge of 273e5ece99 and the authored a36a6b14a5. Its delta from 273e5ece99 touches only `tools/audit/seat/corpus_mirror.py`.
- Previous findings, each resolved at the head (ev/selftest-head.txt, `self-test: ok (with mutants)`: 135 `ok`, 72 `ok   mutant killed`, no FAIL line, matching the body):
  - `formula rounds` is killed by the new 151-request pin `(1, 2, 101, 1)`.
  - `largest cost kept` is killed by "graphql cost: the cursor keeps the last cost answered and the largest, and 'cost' prints both".
  - `2xx only` is killed by "graphql status: an answer exiting 0 with a non-2xx status is no answer ...".
  - The stale partition files are now removed: `partition files` is killed, and the reviewer's glob-nothing mutant is killed.
  - The stub's fidelity fix holds: the `rateLimit asked` mutant is killed.
- My other targeted mutants were killed:
  - `observe`'s max dropped (`seen.get("max", cost)`), killed by "graphql cost".
  - `secondary_wait`'s cap `<=` -> `<`, killed by "graphql secondary: a Retry-After of 300 s is waited, 301 s is not".
  - `isdigit` dropped, killed (rc 1).
  - Driver: ev/reviewer-mutant-driver.py.
- Figures re-derived at the head (ev/figures.txt):
  - The formula costs print `[(1, 3), (30, 92), (32, 99), (33, 102), (50, 154)]`.
  - The ITEM_FIELDS diff count is 0.
  - 72 mutants killed.
  - Not re-derived: the issue/PR search counts 1082 and 2785, the wall-time arithmetic built on them, and the body's `done: 86 mutants, 0 survived` scratch-driver run. That driver is not in the tree, and it evidently draws no predicate-to-True mutant on line 561.
- Untouched: `VERSION`, the manifest version, `RELEASE_NOTES.md`, `tests/golden/` and both claim files.
- Finder's harness: none named. The defect is an owner-reported pause on a tooling instrument, its harness is the self-test's stubbed GitHub, and the body discloses that it has not run against the live API. The class is one seam (the S3 item-batch GraphQL pass), and no enumeration rule is owed.
- Forward-carry: the body states none, and the diff changes no later stage's brief. Its one Friction item carries `dismissed: instrument proposal P-R11-MUTANT-DIFF-ORDER` (packet carry_audit: 1 routed).
- CI: `merge_train.py classify 0812e8b2e4 --pr 3868` printed `WAIT ... pending: gate red: none` on every run from 02:55Z to 02:59Z (ev/classify.log). I stopped polling because the block is on code and does not depend on CI. No required check was red when I read it, so there is no `## Red checks` answer owed. The owed-reds set is in ev/owed-reds.txt.
- Self-audit: `carry_audit.py check` over this verdict (with the body's one Friction item as the body; the packet ran the full body at the head, 1 routed) printed `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc 0.
