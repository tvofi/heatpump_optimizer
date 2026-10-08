head 8b4ce3732544ca9348d8d22dc4f667dbf430cdd6 (closures-autofix bot commit on 9b47134658b0e2b51a371c7f3eb55f58d62ed8c5); merge base 0b89f781f = origin/main at review time. Round 3 of review (rounds: aa88452d, e8701d2e, this).
Delta 9b471346->8b4ce373: tests/closures.json only; non-timing change is one line, + "tests/ha_contract.py" in tests/entities.py's closure (228->229 entries, custom_components entries 80 -> 80, same as origin/main). No custom_components path in the delta.
Merges 87bccd61 and 9b471346: tree == git merge-tree --write-tree of their parents (bf893db3, 20cde6e1), clean automatic merges. git merge-tree origin/main head rc=0.
Three-dot diff: tests.yml, delivery/2058.md, entities.py, nightly_ha.py (+closures.json at 8b4ce373, bot). No VERSION/manifest/RELEASE_NOTES/claim/budget file.
Reviewer mutants at 9b471346 (entities.py, venv-ci, PYTHONPATH=tests/hastub:custom_components:tests):
 RESULT N2 (every PR runs): 2 of 2214 FAILED: reach ('pull_request','false',True),('pull_request','',True) + reporter-watches. rc=1  (m2.log)
 RESULT N3 (drop tests/ha_contract.py pathspec): 1 of 2214 FAILED: coverage, uncovered=['tests/ha_contract.py']. rc=1 (m3.log)
 RESULT N5 (_stage copies tests/layout.py): 1 of 2214 FAILED: coverage, uncovered=['tests/layout.py']. rc=1 (m5.log)
 RESULT NULL (main's tests.yml): 2 of 2214 FAILED: reach ('pull_request','true',False) + coverage pathspecs=[]. rc=1 (null.log)
Fires (pull_request run, head 9b471346): closure-scope 113377927763 success; nightly-ha (2025.2.0) 113378056184 success; nightly-ha (stable) 113378056503 success. Does not fire: body cites aa88452d run 37777137892 (verified round 1).
At 8b4ce373 (checks-final.tsv, 70 runs): fast (3.14) 113400916942/113400965852 success; closures 113400841275/113401090329 success; nightly-ha both arms success twice; pr-contract 113400965841/113405040438 success; only non-green: nightly-status 113400965473 failure (main's scheduled run, answered in body Red checks, diff does not touch what it reads).
Closures red at 9b471346 (113378056663) UNDER-SCOPED tests/ha_contract.py -> autofix 8b4ce373; named and answered in body.
Body at 8b4ce373 (body-8b4ce37.md): Head names 8b4ce3732544ca9348d8d22dc4f667dbf430cdd6; Fires cites the job ids above (match my check-runs); 2212/2214 explained (4a7c846f vs 3b9b6fc6); Red checks names all reds incl. both closures reds, fast, nightly-ha, nightly-status, delivery-status.
Not re-executed by me: N1, N4 (body); the gate itself (CI fast lane cited).
