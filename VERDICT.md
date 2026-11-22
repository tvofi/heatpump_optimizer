Fix review: blocked 273e5ece996438c799c6d246dc54f89e3f888e93 mutation-vacuous: formula_cost round->int (requests/100 floored instead of rounded), observe graphql_cost max->last (seen["max"] = cost), status-range 2xx guard dropped (equivalent: gh exits non-zero on a non-2xx)

bus-nonce: dfb8a3ca6d8194c21b8e13e885cd91df
pending-ci: gate

## Block

Round 1 (first review; no --reviewed-head). Head measured: 273e5ece996438c799c6d246dc54f89e3f888e93 (the PR body's head). Tooling only: no `custom_components/` line in the diff.

The in-tree MUTANTS table holds (67 killed, no FAIL), but six targeted mutants of my own on the added production lines leave three survivors of `python3 -I tools/audit/seat/corpus_mirror.py --self-test --no-mutants` (ev/reviewer-mutants.txt):

- `formula_cost`: `return max(1, round(requests / 100))` -> `max(1, int(requests / 100))` survives. The case "cost: the formula counts each connection once per parent node, rounds the hundreds and is at least 1" pins 149, 10101 and 5101 requests, and each has a fractional part under .5, where rounding and flooring agree, so the case does not detect a floor. The cap pins (92 at 30 items, 102 at 33) agree under both rules too. The commit `1cfbe54f94` says the formula's rounding is "pinned", and it is not. A case where the two rules differ (e.g. `query{a(first:150){b(first:1){x}}}`, 151 requests: 2 by round, 1 by floor) kills it.
- `observe`: `seen["last"], seen["max"] = cost, max(seen["max"], cost)` -> `= cost, cost` survives. The `cost` command's "max" figure, which the body says "the first real scan measures", is unpinned: no case reads `cursor["graphql_cost"]`.
- `query`'s `attempt`: `code == 0 and status is not None and 200 <= status < 300` -> `code == 0 and status is not None` survives. I read it as equivalent while `gh api` exits non-zero on any non-2xx answer. I list it because survivor_list.py reads every survivor the driver reports. Either pin it with a stub answering rc 0 with a non-2xx status line, or drop the redundant guard.

The other three of my mutants are killed: `graphql_wait`'s floor branch `max(wait, next-now, 0)` -> `wait`, `_gate`'s graphql branch disabled, and `observe`'s `limit <= 0` guard reduced to the reset check.

Same seam, code: the "partition" change drops a stale batch key from the cursor but keeps its file. After a 50-item pass then a 30-item pass over the stub's 250 items, `corpus/graphql/items/` holds 14 files: the 5 old `1-50 ... 201-250` files beside the 9 current ones, so every item is stored twice (ev/stale-partition-files.txt). The body says those items "are read once more under the new keys", but nothing removes the old files. The owner's paused 50-item corpus is exactly that case. MANIFEST's universe and examined counts are right, but a reader of the directory gets overlapping, older snapshots. The re-cut should delete (or move aside) the file of each dropped key, with a case that counts the files.

## Evidence

- Setup: `cloud-setup.sh --check` OK; role-pack rendered at main. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 273e5ece99` exits 0, no conflict (ev/merge-tree.txt).
- `python3 -I tools/audit/seat/corpus_mirror.py --self-test` at the head prints `corpus_mirror self-test: ok (with mutants)`, 127 `ok`, 67 `mutant killed`, 0 FAIL (ev/selftest-head.txt). This matches the body.
- Figures re-derived at the head (ev/figures.txt): formula costs `[(1, 3), (30, 92), (32, 99), (33, 102), (50, 154)]`. Raw requests are 308 per item (9240 at 30, 15400 at 50). The ITEM_FIELDS diff count is 0. `closure.py select --diff 1207ee13b0` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, and `tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Not re-derived: the issue/PR counts 1082 and 2785 (they need a search call this seat did not spend) and the wall-time arithmetic built on them.
- Untouched: the diff touches no part of `VERSION`, the manifest version, `RELEASE_NOTES.md` or `tests/golden/`. There are no claim-file changes and no fixtures moved.
- Finder's harness: none named. The finding is an owner-reported rate-limit pause on a tooling instrument, and its harness is the self-test's stubbed GitHub. There is no committed reproduction against the live API, which the body discloses ("Not yet run against GitHub").
- Class: one seam (the S3 item-batch GraphQL pass is the instrument's only GraphQL caller); no enumeration rule is named or needed.
- Forward-carry: the body states none, and the diff changes no later stage's brief.
- CI: `merge_train.py classify 273e5ece99 --pr 3868` printed `WAIT 273e5ece996438c799c6d246dc54f89e3f888e93 pending: gate red: none` on every run, 20:13Z to 20:43Z (ev/classify.log). No required check is red, so there is no `## Red checks` answer owed.
