Fix review: merge 96b8dd7bf471fd979f8f8d3800941c1b1fe7f2e0

bus-nonce: 60371e12bf7ec97419e9c1087a3af987

## Round

2. Round 1 blocked b5cf12dfe83705acaf5726b8e018e84174ac8883 with record-contradicts-diff. I measured head 96b8dd7bf471fd979f8f8d3800941c1b1fe7f2e0, and it was still the PR head when I wrote this. The contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty against origin/main 9586fce08.

## Findings

- The RCA's section 2 says U0c's `run-name` "landed 2 minutes earlier in the assembly" than U9a's reader. That figure does not re-derive. By author date, U9a 9262e6f43 (23:16:49Z, 10-22) is about 2 min *earlier* than U0c 85d13b859 (23:18:40Z), and section 1 says so correctly. By committer date in the assembly, U0c 05:25:52Z precedes U9a 05:26:44Z by 52 s. So the claim's direction holds in the assembly, but its "2 minutes" is the author-date gap with the order reversed. It changes neither process state (d) nor the cost test. Carry: dismissed: a wording slip in a measurement record, with no effect on the cause, the state or the cost test's verdict; it does not justify a third round
- `gate` on the code run 40096300046 at this head is red (job 120885360941, 13:31:19Z): `FAIL run(s) [40096300815] at this head are still being judged; their gate decides`. The body's `## Red checks` does not name it. This is gate.py's designed deferral to the body-edit run, and that run's `gate` (40096300815) concluded success at 13:38:20Z. The `pr-contract` run that started after it (job 120886322355, done 13:35:54Z) passed. Carry: dismissed: a by-design deferral whose deciding gate is green, not this PR's red; no cheaper detector applies

## Evidence

- RESULT mutation (rca index): I deleted `_rca.R10-RCA-CI-RATCHET-RUN-NAME`, and `fold_ledger.py check` printed `UNKNOWN-RCA: N-p2b-assembly-reader cites R10-RCA-CI-RATCHET-RUN-NAME, which _rca does not index`, 1 violation. Restored. (ev/mutants.txt)
- RESULT mutation (schema enum): I dropped `N-p2b-assembly-reader` from finding.schema.json's class_guess, and `agreement_py.py --run` printed `RESULT divergent=3 ...` and `AGREEMENT REFUSED`. Restored.
- RESULT mutation (class row): I deleted the `N-p2b-assembly-reader` row. `fold_ledger check` and `agreement` both stayed ok, but `tools/policy/check-wave-script.mjs` failed `class_guess is exactly the ... bugclasses.json ids plus "new"` (208 passed, 1 failed, with the deliberate probe aside). So the row is pinned. Restored.
- RESULT head: `fold_ledger: 46 classes, 746 instances, 121 in-tree judge survivors (rounds [8, 10]), 121 rca entries`, 0 violations. `agreement_py.py --run` gives `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`. `tests/structure.py` gives STRUCTURE RATCHET PASSED. The scoped gate gives `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` with 5 changed files. All match the body. (ev/checks.txt)
- Round-1 block answered: `grep -n "not registered"` on the RCA returns nothing at the head and returns line 141 at b5cf12dfe. Sections 1, 4 and 5 now state the row as registered, listed and not counted, with total 0, 4 non_round_instances, barrier null and triage P52's rejection, which matches the row (`0 None 4 ['R10-RCA-CI-RATCHET-RUN-NAME']`). The delta b5cf12dfe..b7564b26d touches only the RCA file (12+/4-).
- Head and merges: the body names the authored code head b7564b26d and the head 96b8dd7bf. b638f354d (b5cf12dfe + b7564b26d) and 96b8dd7bf (+ origin/main ac5788f26) show an empty `--cc`, so neither merge has a manual resolution. (ev/merges.txt)
- Merge: `git merge-tree --write-tree origin/main 96b8dd7bf` exits 0 against origin/main 9586fce08 (tree 412ce425f), with no conflict and no claim file touched. (ev/merge-final.txt)
- VERSION, the manifest version and RELEASE_NOTES.md are untouched (the three-dot diff stat is empty).
- Figures re-derived from the Actions API: 5 failed main push runs (d5dc3e26a, 94bec976b, 15f0b5924, 88744e573, 50af6174f); 4 successes before them and 3 from 9fd5eb107; the red ended at 10:19:58Z (about 7.7 h, the doc's 6.0 h being a stated floor at 08:35Z); 113 ci.yml runs in the 24 h to 06:00Z. All match. (ev/figures.txt) I did not re-derive the 1.14 s per call or the 129 runner-s/day; they come from job 120752118657's step timestamps, which I did not open.
- Cause claims checked: d5dc3e26a's `tests/ci_ratchet.py` keys on `r.get("name") not in ("CI", "Tests")` and `== "CI"`. 77f97545c's ci.yml has 0 `run-name` lines, and 85d13b859 adds one. At the head, ci_ratchet.py keys on `.path` (`PUSH_RUNS = ("ci.yml", "tests.yml")`). `tests/ci_ratchet.py` first landed in e3511b221 on 10-11, which matches the doc's 13 days. (ev/claims.txt)
- Class rule: the RCA's class search is a hand `git grep`, which it discloses as such, not a committed harness. A docs-and-register RCA owes none. Round 1's independent grep agreed that there is one affected reader, and I did not build another.
- No mutation table is owed, because the diff writes no production code line. No null control is owed, because no check is proposed.
- The register row's file lacks a trailing newline at the head. That is fold_ledger.py's own writer (`json.dumps` with no newline), not a hand edit.
- CI at this head (check-runs API, 53 runs, ev/checkruns.tsv): every check concluded success, skipped or neutral except the code run's deferring `gate` (see Findings). The edit run's `gate` and both `pr-contract` runs are success. mergeable_state is `blocked`, which waits on the PR being a draft and on review, not on a check.
- Forward-carry: the body says none. The RCA's plan-review suggestion is explicitly a proposal left to the owner, and the triage P52 reopen condition is recorded in the row's non_round_note.
