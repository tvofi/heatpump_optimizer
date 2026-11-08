Fix review: merge e509b39efdf731960cfb0e8b6338ad3610689efe

bus-nonce: c3b906384208c4b75d067d28e536fe43

Round 1 (first-round fix review). Head measured: e509b39efdf731960cfb0e8b6338ad3610689efe. A root-cause record only: no production line, test or check changes, so there is no mutation proof to run (fix-review step 1 is n/a).

## Findings

none

## Evidence

- Handoff content: handoff/r10-rca-stamp-flush-cost (1b8e1600a) is an ancestor of the head. handoff-body/r10-rca-stamp-flush-cost exists. The head adds a main merge (409e85a9e) and the delivery row; the RCA, bugclasses.json and row differ from the handoff only by the row. Three-dot diff is exactly: the RCA section 7, one bugclasses.json string, dev/programme/delivery/3335.md.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exit 0, no conflict (ev/mergetree.txt).
- VERSION, manifest and RELEASE_NOTES.md untouched (not in the diff). No new tracked file needs a closure: the row is under dev/programme/delivery/; `closure.py select` prints `MODE: SCOPED -- 0 script(s) run`.
- Figures re-derived with the committed harness r10_rca_flush_dispatch.py: `runs 42382408131` gives runs=1 runner_min=1007 (ev/run639.txt). `since 2026-10-26T02:31:17Z` now gives runs=30 runner_min=16919; the 3 extra runs are post-fix lanes=beat runs of 1 min each (`since 2026-11-08T04:48:27Z` gives runs=3 runner_min=3, each total=1 and record-autofix only, ev/since-fix.txt), so 30-3 = 27 runs and 16916-min reproduce exactly. The body's "runs=0 since fix" was true when taken; the 3 later runs confirm the fix's lanes=beat payload works in production, with no claim stronger than measured. 4564 for 11-07 = 3557 + 1007 is arithmetic on the cited figures. P(recurrence) 0.1 per cycle: the verdicts are unchanged as the RCA says.
- Class search re-run: `git grep` for dispatch forms finds merge-main.yml, three tests.yml jobs, ci_probe.py, stamp.py, plus nightly.yml's header hand recipe; the same set as the RCA, nothing new. stamp.py names `-f lanes=beat` as its hand form.
- bugclasses.json is consistent with the RCA (27 dispatches, 16916 min). `fold_ledger.py check` rc 0; `structure.py` passes (ev/).
- Process state (c), cause, cost test and the refusal-to-build are section 2-6 of the existing RCA and are unchanged; section 7 claims only re-measurement.
- CI at this head: the first `gate` run failed with "run(s) [42490477382] at this head are still being judged"; I waited, the closures run concluded success, and the re-run `gate` (id 128767145014) is success. The packet re-rendered at the end shows Refusals: none, and all required contexts success. `merge_train.py classify` still prints `RED ... red: gate` because it counts the superseded first gate run; it read the same "still being judged" red, not a finding in the diff. I judge the head GREEN on the re-run gate.
- A local prepr `closures` refusal in the body (entities.py 3 checks failing in the cloud container) is identical at base and not this diff's; CI `tests / closures` is success.
