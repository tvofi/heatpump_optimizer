Fix review: blocked a5de7df1fac197d42d448e400bba72deb6e4bea7 defect: _bound_instants descends into a trie Domain on a stored "" key, so a corrupt instant leaf now drops the whole store (accuracy, snapshots) where the base loaded it
bus-nonce: dc269303e69472fdd54a39329b93174c

Round 1. Reviewer: review-2375 (fresh context, detached worktree at the head).
Measured head: a5de7df1fac197d42d448e400bba72deb6e4bea7, which is 8508252635 plus one
github-actions[bot] commit, "ci: pin killed mutants". That commit adds 19 files under
tests/mutation_ledger/killed_by/ and nothing else. Every file is a new killed_by pin
(features.py 8, finite_boundary.py 6, debug_collect.py 5). No production line moved,
so my harness figures taken at 8508252635 still hold at a5de7df1f.
Baseline: merge base 52f698905868c9140ed213ea542c44053fca7096. origin/main is now 9a1ce39c3,
and `git merge-tree --write-tree origin/main HEAD` returns rc=0.

## The blocking defect (the reviewer's own probe: ev/rev_probe.py, my instrument, not the finder's)

The added walk is `node.get(k, node.get("*", {}))` (store.py:178) and `node.get("")` (store.py:163).
`_tries()` stores a leaf's Domain under the key "" and a map key's Domain under "~", so for a
stored dict key of "" (or "~") the child node is a `Domain` (a NamedTuple), and the next
`.get` raises AttributeError out of `QuarantiningStore.async_load`. `load_mapping` turns that
into None, so the loader starts from nothing: every sample, lead record and promise in the
accuracy store, or the whole snapshot ring, is lost because of one malformed leaf. That breaks
the boundary's contract ("a poisoned leaf becomes that loader's own absent-data default").

    RESULT corrupt_empty_key_under_leaf_raises            base=0  head=1 (AttributeError: 'Domain' object has no attribute 'get')
    RESULT corrupt_empty_key_under_leaf_load_mapping_none base=0  head=1
    RESULT corrupt_empty_key_list_under_leaf_raises       base=0  head=1
    RESULT corrupt_tilde_key_instant_raises               base=1  head=1   (pre-existing, see below)

The documents were {"accuracy": {"samples": [{"t": {"": <iso>}}]}} and the same with a list value.
Fix shape: descend only into a dict child, e.g. `child = node.get(k, node.get("*", {}));
child if isinstance(child, dict) else {}`, applied in both arms, plus a finite_boundary row that
drives a "" key at an instant leaf through a real loader. The finder's store_fuzz does not
generate this shape (accuracy, N=100: load_exc=0 at both ends), so the regression is visible
only to my probe.

Not this PR's defect, owed elsewhere: at the BASE, a literal "~" key holding an instant string,
{"accuracy": {"lead_sigma": {"~": <iso>}}}, already raises the same AttributeError and drops the
store. The fixer may close it in the same guard (one line, same seam). If it stays out of scope,
the orchestrator files it.

## Everything else checked (it passes, and carries once the defect is fixed)

Finder harnesses at base 52f698905 and head (ev/finder_harnesses.txt; blobs 59047d6a0201,
ffd0633baec0, cf8f195ddb83 from b202335e2, 5fe6f3a067b6 from 532d8d09d, all matching the body):
- snapshot_bound.py: base snapshot_ahead_warnings=5, ring_instants_changed_vs_disk=5; head 0, 0.
  control_accuracy_* is 0 at both ends. `--perturb` reads 0 at both.
- future_clamp_seams.py: base instant_leaves=55 flagged_leaves=7 pairs=2; head 55/0/0. The head's
  zero is vacuous by construction (the enumerator reads the accuracy store at 0 h), and the body
  says so. I checked the companion directly (below).
- load_prelude.py: base raising_seams=1; head 0. `--perturb` reads 0 at the base, the fix's effect.
- store_report_equiv.py: head mismatches=0, `--perturb` 1764. It cannot run at the base
  (no store.quarantines), as the body says. Forward-carry (1) holds.
- store_fuzz.py 100 _accuracy: base log_gt3=100 (snapshot "ahead of the clock" WARNINGs); head ok=100, all zeros.

Lead semantics (rev_probe.py, probe A): at the head a due 10 h ahead is kept at 10.0 h, and a due
30 h ahead is bounded to 24.0 h, the same as the base. samples/#/t and evidence_since 1-2 h ahead now
load at 0.0 h (base: kept). This is the claimed tightening. I checked the writers: promises/*/start
is solve_time (accuracy.plan_promise), so no legitimately future instant loses its lead.

Mutation proof (reviewer-run, tests/finite_boundary.py, about 4 minutes each; ev/fb_*.txt):
- head: ALL 88 PASSED.
- m0 null (a comment on `import hashlib`): ALL 88 PASSED.
- m1 (`limit = bound`, the declaration ignored): 1 FAIL, lead_lost=['accuracy (writer round trip)', 'snapshots (writer round trip)'].
- m2 (my own: the digest is recorded in a `finally`, so a failed save is skipped as written): 1 FAIL, save counts [1, 3, 0] (want [1, 3, 1]).
I did not re-run M2-M5 or features.py. The bot's 19 killed_by pins record CI's mutation lane killing them.

Closing: the body has "Closes #2224." and "Part of" for #2232, #2236 and #2238. closingIssuesReferences
is [2224], as expected and as the roster's `fixes` requires.
VERSION, manifest.json, RELEASE_NOTES.md, tests/golden/ and both claim files are untouched (three-dot).
tests/structure_budgets.json: five rows move, and every one moves down (class_excess_loc 18468->18382,
coordinator_attrs 151->148, coordinator_multiassigned_attrs 118->115, max_class_loc 8635->8553,
seam_cut_total 752->720). There are no raises.
Not re-derived by me: archscore dS +1.3265, closure select counts, and ci_predict. These are cited from
the body and CI, never re-run here (fix-review.md 11).
Checks (ev/checkruns.txt): at 8508252635, `mutation` concluded failure, which is the unpinned-sites
trigger the body hands to mutation-autofix (answered by naming). At a5de7df1f, fast, coverage, mutation
and CodeQL analysis were still in progress when I read them, so I take no position on them.
Body staleness: `## Head` names 8508252635, and the head is now a5de7df1f (a bot carry). The body
re-take is owed with the fix.
Architecture (fixer.md 17): the shape matches the architect note. The store owns the load prelude, the
digest and the report rules, and the coordinator only calls them. No breach found apart from the defect above.
