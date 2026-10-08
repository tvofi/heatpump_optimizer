Fix review: blocked aa88452dfef01782eddc5d31c9ea3a350926504e root-cause-unanswered: delivery-status and nightly-status went red on a diff touching tests.yml and the body's Red checks says none; fires half unproven
bus-nonce: 242743ad42c73bc7a6078d071037f5bf

Checked at aa88452dfef01782eddc5d31c9ea3a350926504e.
1. Does not fire here: closure-scope success, nightly-ha skipped. Correct for the pathspecs, since this diff touches none. Design note (non-blocking): the job's own definition in tests.yml is not a trigger, so a change to the job's if: is covered only by the entities.py reach check, not by a run.
2. Unrequired: ruleset 22628467 lists no nightly context and the diff has no ruleset change. nightly-ha is not required, so a skipped context cannot block (#1514 shape not reachable); needs closure-scope plus !cancelled() keeps schedule and dispatch running.
3. Pins: reach, output and staged-read coverage checks added in tests/entities.py; mutation N1-N5 and null control are in the body but not re-executed by me (the fast lane passed at this head in CI).
4. BLOCKING: pr-contract red (jobs 113310735049, 113311725784): delivery-status and nightly-status are red, the diff touches tests.yml that they read, and ## Red checks says none. Each must be named and answered (nightly-status: scheduled run 37595831734 mutation-ledger/mutation-nightly/record-autofix, unrelated lanes; delivery-status: overdue batch). Fixer owns the body.
5. BLOCKING: the fires half is unproven. The body says the next head adds a docstring line to tests/nightly_ha.py; this head has none, and run 37764931838 was a dispatch, not a pull_request event. No real pull_request run shows nightly-ha firing. Add the trigger-touching commit (or state a cheaper proof) and cite the run.
6. Body staleness: it says ALL 2214 checks while the mutation section says 2212; re-take figures.
