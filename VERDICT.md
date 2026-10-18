Fix review: merge faf04b0ef3d83d21e2388e000e442da78c97637a
bus-nonce: ee06b851937191bedb242f2868532a2f

Evidence: ~/hpo-seats/r10s3/review-2384/ev (check-runs-faf04b0.tsv, this file). Round 1. Head faf04b0ef measured and still the PR head at post time.

RESULT roster_lib: dev/programme/rosters/wave-r10-groups.json loads (load_roster_file, 63 groups, round 10, 38 open); no group removed, six appended, top-level keys unchanged.
RESULT brief_lint (tools/policy/brief_lint.mjs, byte-identical to origin/main 55dc8d9c2): TOTAL 0 error(s), 1 warning.
RESULT ref_privacy --check at head: 0 refused. grep of the roster for /Users/, the account name, /private/tmp, /var/folders: nothing.
RESULT merge-tree origin/main..head: clean, no conflict, no MERGE-CLAIM line.
RESULT stage changes, old main vs head, each backed:
  R10-STORE done = #2375 merged 932f5d601; R10-LEAF-IMPORTS done = #2371 merged 234087a51; R10-PUMP-MODEL done = #2365 merged (413944b67);
  R10-REF-PRIVACY done = #2366 merged a73f3320c; R10-DEEPLINK-CENSUS done = #2345 merged f4955e15f. Commit pins in the roster resolve and are on main.
  Issue re-wiring: #2253 and #2317 stay open and are still named by a not-done group (R10-ADVISOR, R10-UX-HEALTH, R10-DEEPLINK-HANDLERS); #2255 and #2259 are wired to not-done groups so Closes lines resolve; #2228, #2310 and #2224 are closed. The six appended groups are not-started with issues #2378 #2395 #2381 #2331/#2353 #2235 and no resume claim.
  The only brief change to an existing group is R10-SCORES coordinator.py:10403 -> 10281; line 10281 holds ctx._thermal_params.heat_loss_coefficient at head. Carry rows appended to NIGHT-FOLDS, INPUT-STALENESS, CURRENCY, REPLAY-LANE, UX-HEALTH and BRIEFS-FOLD are forward-carries from merged PRs and the sweep, each naming its source.
RESULT scrubbed briefs: R10-RCA-FRICTION and R10-RCA-STRUCTURE-BLIND now say ~/hpo-seats/r10s3/... for their seat dirs; the rest of each brief, its files, issues and after list keep their meaning.
RESULT Red checks: the only real reds in the range are pr-contract and instrument-self-tests at 0942893c2, both answered in the body's ## Red checks (ref_privacy --check as the cheaper detector, standing cost named; pr-contract = the section saying none). The other non-green runs in the range (19 at 0ae19a514, Analyze (python) at 0d11a7bd) are conclusion cancelled by supersession, none failure.
RESULT CI at head faf04b0ef (check-runs API, ev/check-runs-faf04b0.tsv): 45 runs, 30 success, 15 skipped, 0 failure, 0 cancelled; instrument-self-tests success 14:49:58Z, pr-contract success twice (14:47:07Z, 14:47:45Z), briefs success, delivery-status success. Heavy runs cited, not re-run.
RESULT no production code, so mutation proof, null control, claim files, VERSION and class-open steps are N/A; the diff touches the roster and delivery/2384.md only (not in POLICY_GLOBS, no ## Approval owed).

Non-blocking notes for the orchestrator:
1. ## Figures quotes 349 insertions and 23 deletions at 94929f74a and "one path". At the head the roster alone is 352/24 (the +3/-1 is 47313f3a9, R10-SAV-BASELINE fixes [2255], a hand edit the body does not describe) and the PR diff now has two paths (delivery row). Re-take the figures if the body is touched again.
2. origin/handoff/audit-r10-roster is now at 97344315a, ahead of this head; stage rows landed there after this PR's head need a follow-up roster PR.
3. New carry rows contain literal backslash-apostrophe pairs (for example fold\'s); harmless to readers, matches existing BRIEFS-FOLD rows.
