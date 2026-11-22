Fix review: merge f93e28bb6267d66f3cec852f9502843ea52b7fca

bus-nonce: 7b5b03c52b5bee5f649905111e70bd4b

Round 1 (first review, scope full). Reviewed from a detached worktree at f93e28bb6267d66f3cec852f9502843ea52b7fca; merge base baa9a467ac518bc3f8733d2603ea8ae406b235af; `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.

## Evidence

- CI: `merge_train.py classify f93e28bb6267d66f3cec852f9502843ea52b7fca --pr 3865` printed `GREEN f93e28bb6267d66f3cec852f9502843ea52b7fca pending: none red: none` (ev/classify.log). Owed-reds set: `tests / mutation`, `tests / typing`, `validate / validate-hacs`; none is red at this head. Earlier heads of the range (b25ced9bdd, 264bea5f15) were not checked for red history; the body states `## Red checks: none`.
- Merge with main: `git merge-tree --write-tree origin/main f93e28bb62` exits 0 (tree 03dc29b1b9); no conflict.
- Step 1, mutation proof, reviewer's own mutants (ev/reviewer-mutants.txt), each run as `python3 tools/audit/seat/corpus_mirror.py --self-test --no-mutants` at the head:
  - M1, `archive_refusal` `target == base` site back to `info.is_dir()`: killed, `FAIL archives: a member with an empty name ... got ('RAISED IndexError', None)`.
  - M2, the `parents`/`files` site back to `info.is_dir()`: killed by the same case.
  - M4, helper body `name[-1] == "/"` (the 3.11.5 shape): killed by the empty-name case and the 1429-archive one-byte fuzz case.
  - M3, the `safe_extract` loop site back to `info.is_dir()`: survives. This is an equivalent mutant, not a gap: `safe_extract` reaches that loop only after `archive_refusal` returns "", and `archive_refusal` refuses any empty name ("a member's path is the archive's directory"). For a non-empty name, `is_dir()` and `name.endswith("/")` agree on every interpreter. The site's predicate is still pinned by the in-tree `dir entry not written` mutant (replace it with False), which is killed.
- In-tree MUTANTS at the head, `--self-test` (with mutants): `corpus_mirror self-test: ok (with mutants)`. The new `dir-ness from the name`, `dir entry is a parent` and `dir entry not written` mutants and the renamed `directory itself` mutant are each `mutant killed` (ev/selftest-head.txt).
- Step 2, the finder's harness (3.11.5's `ZipInfo.is_dir` body patched in, `--self-test --no-mutants`): at base baa9a467ac, rc 1 with `FAIL archives: each of 1429 archives one byte away from a well-formed one extracts or is refused by a rule, and none raises; raised ['IndexError']`. At the head, rc 0 with `ok (without mutants)` (ev/finder-base.txt, ev/finder-head.txt). The body's figure was taken at base 8ef4509; this re-take at the PR's own base reproduces it. 1429 is this run's fuzz count, which the check generates itself.
- Step 3, null control: unpatched `--self-test --no-mutants` at the base gives `ok (without mutants)` (ev/null-base.txt), so the defect is invisible without the 3.11.5 body, as the body says.
- Step 6, other configurations: at the head, /usr/bin/python3.11 (3.11.18), python3.12 (3.12.3), python3.13 (3.13.18) and python3 (3.14.7) each give `ok (without mutants)` (ev/interpreters-head.txt). 3.11.5 itself is not on this seat either; the patched body stands in for it, as in the body.
- Step 6, class: I re-ran the body's enumeration rule at the base and at the head (ev/class-rule.txt). At the base it returns `corpus_mirror.py` lines 151, 155 and 210 (the three seams the diff closes), two `pathlib` calls in `tests/entities.py` (22159, 42129), the self-test's pathlib call (1004), and line 1179. Line 1179 is the `directory itself` MUTANTS needle, a string literal holding `info.is_dir()` that the diff rewrites. At the head the rule returns only the pathlib calls and the new mutant's replacement string. So no zip-member seam is open. I widened the rule to `is_dir`, `.filename[`, `infolist` and `namelist` in every zipfile importer: the other importers (`platinum_rules.py`, `ci_ratchet.py`, `entities.py`, `codeql_scope.py`) read names through `namelist()` with no dir-ness predicate.
- Step 5: the three-dot diff touches only `dev/programme/delivery/3865.md` and `tools/audit/seat/corpus_mirror.py`. `VERSION`, the manifest and the `RELEASE_NOTES.md` heading are untouched.
- Cheap checks at the head (ev/cheap-checks.txt): `tests/structure.py` gives `STRUCTURE RATCHET PASSED`; `tests/closure.py select` gives `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, which matches the body. Architecture score is cited from CI (`arch-score` success), not re-run.
- Step 7: the body names f93e28bb6267d66f3cec852f9502843ea52b7fca as head, which is the head I measured.
- Step 4, claims: `tests/env_drift.py --all` did not finish inside my 200 s timeout (ev/cheap-checks.txt: `Terminated`), so it was not re-derived. The three-dot diff touches no golden fixture and neither claim file, so no claim or drift can move; CI's required checks are green.
- Step 14: no budget, closure, golden or claim file moves in the diff.
- Step 16: no actuator path; `custom_components/` is untouched.
- Steps 9 and 10: the finder's harness is an inline `python3 -c` script, not a committed harness. The new self-test case `a member with an empty name ...` commits its effect into the tree, so it reads the defect on every interpreter. The body states `Forward-carry: none`.

## Findings

- Note: figure: the body's class census at the base ("three seams ... `tests/entities.py`, two; this file's self-test, one") omits a seventh line the rule prints, `corpus_mirror.py:1179`. That line is the `directory itself` MUTANTS needle, a string literal and not a call, and this diff rewrites it. No seam is open. Carry: dismissed: a string-literal hit the diff itself rewrites; paperwork, settled at this head.
