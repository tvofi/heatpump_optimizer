Fix review: merge ef3e4e145460dd3a3b95adb69d26c4a866b21945

bus-nonce: 52c65c48bf446147a84170e221518aa3
pending-ci: gate / tests (classify prints WAIT: pending, gate red: none)

## Evidence

- Head reviewed: ef3e4e145460dd3a3b95adb69d26c4a866b21945 (ev/HEAD.txt). Delta 16c628e4..ef3e4e145460dd3a3b95adb69d26c4a866b21945 touches one file, dev/programme/rosters/wave-r10-groups.json (ev/delta-files.txt). Three-dot diff against origin/main merge base: every path is under dev/programme/rosters/, triage/ or delivery/; non-record paths = 0 (ev/non-record-paths.txt).
- `node tools/policy/brief_lint.mjs` at head: exit 0, all control lines ok.
- Roster JSON parses at head; groups 504 at head vs 342 on origin/main; groups on main missing at head: 0. Carries/top-level keys on main missing at head: none.
- R11-INTAKE-R10-RESIDUE, R10-SELFTEST-SCOPE-UNION-GUARD, R10-HOTFIX-SELFTEST-SCOPE-RERECORD: present at head, absent on origin/main.
- `git merge-tree --write-tree origin/main HEAD`: clean, tree d1744547127d41b38a71bc2eb89ea18732902770.
- tests/entities.py: could not run here (ModuleNotFoundError: homeassistant in tests/harness.py under venv-ci python, with BASH_ENV unset); not verified by this seat. The diff touches record paths only.
- tests / nightly-status answer in the body: states the check grades main's last nightly dispatch (run 43204237855), names the cause as outside the branch and the owner, and says no cheaper detector exists. Judged on its text: adequate. Not re-verified against the run.
- CI: merge_train classify polled twice (about 90 s apart): WAIT pending, gate red: none. Not settled; no red seen.
- The body's figures (22 files, 951 commits, 342 to 437 groups) were measured at 7696a3ba and are not re-measured at this head. The head now holds 504 groups, which includes groups main has since gained. I did not re-derive them.
