Fix review: merge 6156d54c96eddb07dc40ec2ce02f96e899986c84

bus-nonce: 80c1a566049576d36f91b53bee4ce88f

## Evidence

Head measured: 6156d54c96eddb07dc40ec2ce02f96e899986c84 (ev/HEAD.txt). Roster-only batch; round not stated by the body, treated as first review. origin/main = merge base = a6620c30adcdf0d9529ee66977694bfa2a06d5c3.

- RESULT diff: three-dot `git diff $(merge-base origin/main HEAD)...HEAD` is 2 files: dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/2661.md. Nothing else. VERSION, manifest and RELEASE_NOTES untouched (empty diff).
- RESULT groups: 169 before, 169 after, same order and same group/lane ids, top-level keys identical, none removed or added. Exactly 5 entries differ (ev/changed.txt): R10-SCORES (resume), R10-LEARNER-DEFAULT (brief), R10-FLOW-TOOLKIT-MEASURE (resume), R10-FLY-SUITE-ENV-FLAKES (carry), R10-FLY-NO-FOOTERS-EMITTERS (resume). Within each only the named key changed.
- RESULT set-stage: R10-SCORES done at 14405df59 = merge of #2647, ancestor of origin/main; R10-FLOW-TOOLKIT-MEASURE done at a6620c30a = merge of #2645, origin/main tip; R10-FLY-NO-FOOTERS-EMITTERS done at c6ef06684 = merge of #2652, ancestor of origin/main. All three PRs are merged on main.
- RESULT append-carry: R10-FLY-SUITE-ENV-FLAKES gains one carry, the #2632 round 3 correction (coverage-ratchet red caused by features.py leaving worker children, coverage_tree.sh seam). Existing carries unchanged; it appends only.
- RESULT re-cite: R10-LEARNER-DEFAULT brief changes only coordinator.py:6385-6388 to 6552-6559. At origin/main those lines hold the comment and predicate saying an unconfigured slot (no reading.entity_id) must not freeze learning, which is what the brief claims. The rest of the brief text is identical.
- RESULT null control: main's roster equals the merge base (main == merge base), so nothing main wrote is lost; 169 groups both sides.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs` on the head roster prints TOTAL: 0 error(s) (ev/brief_lint.txt).
- RESULT merge-tree: `git merge-tree --write-tree origin/main HEAD` exit 0, tree ff7807c7 (ev/mergetree.txt). Clean.
- RESULT commits: no Co-Authored-By, Claude or session trailer in any commit message in origin/main..HEAD.
- Scoped gate: local run printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` Two scripts (tests/doc_claims.py, tests/harness_headers.py) failed locally only because this seat lacks the voluptuous and homeassistant modules (ModuleNotFoundError); that is an environment gap, not a PR result, so I cite CI for them (ev/gate.txt).
- CI (check-runs API for the head, 36 runs, read once): no failed run. Success: pr-contract, briefs, closure-scope, mutation, nightly-status, delivery-status, policy-docs, wave-script, hassfest, validate-hacs, budget-raise-gate, arch-score, scope, graders-head-copy, CodeQL analyses. Skipped: coverage, coverage-ratchet, typing, browser and the mutation lanes. Still in_progress when read: fast (3.14), closures, env-matrix, instrument-self-tests. The merge holds only if those four conclude green. No red check, so no root-cause answer is owed; the body's "Red checks: none" matches.
- Body figures: 169/169, 5 changed, 5 commits and the merged-head description all re-derived. I did not re-derive the stage counts (done 92 then 95); the three set-stage ops account for the +3 done and -3 in-progress.

## Findings

None that this PR leaves unsettled. The Forward-carry is "none" and the roster carry added here is the #2632 text already present on the roster.
