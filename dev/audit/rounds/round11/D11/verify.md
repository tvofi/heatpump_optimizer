# D11 verification, audit round 11

Verifier: the one D11 verifier, all three lenses (V1 reproduce, V2 independent, V3 reach and class).
Tree: every D11 finding's scope (D11-s1, D11-s2, D11-s3) is outside the planted-scope list, so all were
measured in the git worktree `audit-r11-verify-D11` at `handoff/audit-r11-register` =
`28b864af6d909e3114d07546e22af79ce8dc85ef` (the finders measured `92d38ecb64`). No plant export was used.
Box: macOS arm64, python 3.14.7, node v24.22.1; `$HOME/venv-ci` absent, so `python3` on PATH was used.
`NODE=$(which node)` was exported for the s3 harnesses, whose default `/opt/node22/bin/node` does not exist here.
Every headline number below is a count, so contention does not move it; load1 was high throughout
(between 90 and 384, other seats running) and thread_factor was 1.000 to 1.009 on every run. Any timing is provisional.

The register's verdict columns, GitHub and other verifiers' reports were not read. One exception, by the harness's own
design: `s2/provenance.py`, re-run exactly as its header says, queries the public attestations API. My V2 for that
finding is static and makes no GitHub call. The other s2 harnesses read the committed `api/` snapshots.

## Per finding

### D11-s1-01: the Stop hook lets a turn end red on 2 corpus files. Vote: verify (low)
- V1: `stop_hook_reach.py` gives `MISSED AGENTS.md`, `MISSED dev/audit/README.md`, `RESULT missed=2`, with corpus=67 here
  (65 at the finder's baseline). Under `--perturb`, missed=0 (to_zero, as stated). Null control: a production-only change
  exits 0 and a CLAUDE.md change exits 2.
- V2: I wrote my own driver. For each of the 67 `--corpus-filter` files, a one-file scratch repo is built with the file
  changed, a red `policy_lint` stub and the production hook run end to end. 2 of 67 exit 0 (AGENTS.md,
  dev/audit/README.md). The seam_rule grep agrees: 2.
- V3: this is a Claude Code harness hook, not a Home Assistant path. It is reachable in every seat session. Severity is
  low: CI's policy-docs job still runs the linter. The seam_rule enumerates every corpus file against the prefix list,
  so it covers all seams. Class: N-move-stale-path fits dev/audit/README.md (the old `tools/audit/` prefix kept).
  AGENTS.md was never listed, which is I4: two definitions of the policy set, the hook's prefix list and the linter's
  corpus, disagree. Proposed class: I4, with N-move-stale-path for one of the two instances.

### D11-s1-02: the ruleset drift detector reads 1 of 3 rulesets. Vote: verify (medium)
- V1: `ruleset_reach.mjs` reports unmonitored=2 (22628467 and 23937752 give delta 0, while 23698884 gives delta 6).
  `--perturb` gives unmonitored=1 (down, as stated). The null arm has 0 findings.
- V2: my own read of the snapshot in `s1/api/`. The branch rules carry (deletion, 22628467), (non_fast_forward,
  22628467), (pull_request, 23698884) and (required_status_checks, 23698884). counts.mjs:297-299 adds ids only from
  `required_status_checks`, so it reads {23698884}. Active rulesets: 3. Unread: {22628467, 23937752} = 2.
  The fixture's `_comment` scopes the class to required contexts by design. No other tracked script reads either id.
- V3: GitHub repository rulesets are a real path and reachable (decision 0009 records an earlier `PUT` on 22628467's
  bypass_actors). Medium severity is earned: the deletion and force-push protection on main and the release-tag
  protection can change unseen. The seam_rule needs the live API; I ran its equivalent over the snapshot, and it
  enumerates every active ruleset. Class I3 is confirmed. **Duplicate of D11-s3-01** (same reader, same line).

### D11-s1-03: rules_sync `--check` has no control, and `--self-test` rewrites. Vote: weaken (low)
- V1: `rules_sync_control.py` gives control_red_on_drift=0, check_refuses_drift=1 and selftest_rewrote=1.
  `--perturb` gives control_red_on_drift=1 (up).
- V2 (test-gap mutation): the single production line is `tools/policy/rules_sync.mjs:110`,
  `process.exit(drift ? 1 : 0)` changed to `process.exit(0)`. In a temp copy with one drifted `.mdc`, the mutant
  `--check` exits 0 (rc 1 unmutated, rc 0 in sync). `git grep` finds no test, self-test or mutant arm that drives
  rules_sync over a drifted tree. Its users are governance.yml:170 and prepr.sh:4578, both running `--check` on the
  live tree. field_coverage records it as `none`. So 0 controls exist.
- V3: reachable in CI (policy-docs, required). The refusal works today, so the consequence needs a second, later
  edit to neuter it. The `--self-test` write only regenerates generated files into their correct form. For these
  reasons I weaken to low. The seam_rule (`inventory.py` + awk) lists 12 ci-required instruments with no self-test or
  acceptance control, rules_sync among them, so it enumerates the seams. Class I1 is confirmed.

### D11-s1-04: claim-merge mutation control is dead. Vote: weaken (low)
- V1: `claim_control.py` gives baseline_pass=0 and mutants_reached=0 of 16. `--perturb` gives baseline_pass=1,
  killed 16 and survived 0 (up). `claim_merge_mutants.py`, run directly, also gives `baseline rc=1 FAIL`.
- V2: I built my own partial copy (tests/ plus .gitattributes). `import harness` raises FileNotFoundError on
  `custom_components/heatpump_optimizer/translations` (tests/harness.py:41). Adding only that translations directory
  makes the import succeed. Nothing wires the harness: no workflow or self-test step runs it, and its only appearance
  in selftest_closures is a `beatd/probes` closure listing.
- V3: this is an audit instrument, not production. The driver itself stays tested by `tests/entities.py`'s section in
  the suite, so the consequence is a lost re-runnable mutation proof, not an untested driver. Severity: low.
  The seam_rule (`copytree(ROOT / "tests"`) matches only this one harness. It is a literal of the demonstrated seam
  and does not enumerate other partial-tree copies. Class I1 is acceptable. The cause is an import-time dependency
  added later, so it is close to N-move-stale-path but not a move.

### D11-s1-05: tests/structure.py is unowned and unpinned in required jobs. Vote: verify (medium)
- V1: `meter_boundary.py` gives `EXPOSED tests/structure.py via tests / arch-instrument, tests / fast (3.14)` and
  pr_copy_unowned=1. `--perturb` gives 0 (to_zero). The null control (coverage_ratchet) is pinned, giving exposed=0.
- V2: own check. CODEOWNERS has no pattern matching `tests/structure.py`. Its tests/ lines are per-file and none is
  `structure.py`. `tests/run.sh:568` runs `"$PYTHON" tests/structure.py`. `tests.yml` has no restore of structure.py:
  its PINNED restores are coverage_ratchet (l.1021), nightly_status and a pinned.list without it. `gate.REQUIRED["pr"]`
  includes `tests / fast (3.14)` and `tests / arch-instrument`. For comparison, coverage_ratchet is pinned (l.1023)
  and machinery_ratchet is pinned in governance.yml (l.150). Exposed: 1.
- V3: reachable, since every PR runs it. The consequence is a PR that can redefine a ratchet metric without the owner
  review that a budget raise needs. Medium holds. The seam_rule's EXPOSED lines cover all 8 budget meters, so it
  enumerates the seams. Class: new is acceptable. I3 (a bypassable boundary of a required check) is the nearest
  existing class, and I propose I3.

### D11-s1-06: wt_sync.sh `--self-test` force-pushes. Vote: weaken (low)
- V1, first as written: `seat_selftest_sweep.py --only wt_sync.sh pr_cap.py heartbeat.sh` gives
  real_repo_writes_on_selftest=0 on this box. The harness's git shim is `#!/bin/bash`, and macOS bash 3.2.57 fails to
  parse its `$(case ... )` with a syntax error, so every git call failed. That is a host-portability defect of the
  harness (N-host-platform-unrun shape), not a refute.
  I re-ran a scratchpad copy with only the shim's shebang changed to `/opt/homebrew/bin/bash`. It gives
  `REAL-REPO-WRITE wt_sync.sh` and real_repo_writes_on_selftest=1 (wt_sync timed out at 240 s under load1 131 after
  logging a push). `--perturb --only wt_sync.sh` gives 0 (to_zero). Null control: pr_cap.py logs no shim call.
  Before running, I confirmed safety: under the harness's insteadOf, `git remote get-url --push origin` resolves to
  `file:///nonexistent-d11s1/...`, and a dry-run push fails. No push left the box, and no wt_sync process remained.
  I did not run the full 113-script sweep on this shared, non-isolated box, so the finder's no_selftest=18 is not
  re-taken.
- V2: static reading of `tools/audit/seat/wt_sync.sh`. Line 14 looks only for `--scratch`, and any other argument
  falls through to the fetch/snap/`push -q --no-verify -f origin` loop over every dirty worktree. My own text count:
  14 of the 117 tools/audit/seat scripts carry no `self-test` string at all.
- V3: reachable on a real seat box whenever a seat follows the README's "each carries --self-test" with this script.
  The effect is the tool's normal production action: a ref_privacy-guarded snapshot push to `wip-sync/<slug>`, which it
  is designed to run every 15 minutes. It does not destroy data. For that reason I weaken to low. The seam_rule
  (NO-SELFTEST and REAL-REPO-WRITE over every seat script) enumerates the seams. Class: new is acceptable.

### D11-s2-01: a red-gate merge (#3618). Vote: weaken (medium)
- V1: `gate_at_merge.py` gives #3618 red and #3644 wait, platform_gate_red=1 and merged_not_green=2. `--perturb` gives
  red 0 and merged_not_green 1 (down). Null control: 50 of 52 are green.
- V2: my own reader over `api/gate_runs.json` with two definitions. (A) The latest gate run per check suite by
  started_at, completed at or before merged_at. (B) The globally most recent completed gate run. Both read exactly
  {3618} red, and the in-progress count is exactly {3644}. Leave-one-out: dropping #3618 gives red 0, so the finding
  rests on one merge. For #3618, the latest gate before 19:51:14Z is the failure at 19:18:44Z (suite 118403819214).
  It is the most recent gate run overall, so GitHub's "latest run wins" reading is red too.
- V3: reachable on real GitHub. However, the snapshot's ruleset 23698884 shows `current_user_can_bypass: never` and no
  owner bypass actor. A merge with a red latest required run therefore means either different GitHub semantics or the
  ruleset not enforcing at that moment, for example an enforcement toggle during the 2026-11-15 closure.
  The snapshot cannot separate these, and the finding's mechanism ("the required gate check does not enforce what
  the train assumes") is unproven. The number stands. Severity: medium rather than high. It is one text-PR merge,
  and the mechanism is unproven.
  The seam_rule lists every window merge, so it enumerates the seams. Class: I3 (a required check's boundary
  bypassed) instead of new.

### D11-s2-02: no owner-own approval at head is recorded. Vote: weaken (low)
- V1: `oversight.py` gives owner_account_approval_at_head=31, owner_own_at_head=0,
  agent_declared_under_owner_account=31 and merged_by_owner_account=49. `--perturb` gives owner_own 31 (up).
- V2: my own regex (`mandate|orchestrator|on behalf|agent approval`) over `window.json`'s reviews at `head_sha`
  gives 31 owner-account approvals at head, 31 declared, 0 undeclared, and merged_by tvofi 49. These are identical.
- V3: real GitHub. The 0 is the designed outcome of decision 0013's mandate (agent approval as the owner, declared in
  the body). The residual defect is that the agent/human split is keyed on review-body text alone, which the
  perturbation shows. That is a record-keeping weakness, not a wrong merge: low. The seam_rule's
  `grep -rn AGENT_DECLARED tools/` enumerates the readers. Class: new (nearest I3).

### D11-s2-03: the HACS zip asset is not attested. Vote: weaken (low)
- V1: `provenance.py` (live attestations API) gives zip_attested=0 and tar_attested=5 over v10.0.3, v10.0.2,
  v10.0.1, v10.0.0 and v7.1.17. I did not run the `--perturb` arm, which is also live.
- V2 (static, no network): release.yml has one `actions/attest-build-provenance` step (l.286). Its subject is
  `git archive --format=tar <tag> | sha256sum` (l.279/292). The uploaded `heatpump_optimizer.zip` (l.195, named
  by hacs.json `filename`) is never a subject. 0 of 1 attest steps cover the installed asset.
- V3: real release path. However, HACS does not verify attestations, and the zip is a deterministic `git archive`
  subtree of the attested tag. A user can re-derive it, and nothing an install does today changes. The release.yml
  comment records the choice. Low. The seam_rule (`--n 30`, one line per release) enumerates the releases.
  Class: new.

### D11-s2-04: policy units restated across files. Vote: verify (low)
- V1: `policy_health.py --list` gives dup_units=16 and rulings_overlap=1, over corpus_files=86 here. `--perturb` gives
  0 and 0. That perturbation is tautological: it deletes the duplicates it counts, in memory. It moves as stated, but
  it tests the counter, not a production seam.
- V2: my own sentence-level count over 76 policy files (the corpus filter plus dev/governance/**.md, RULINGS.md and
  the steward SKILL.md, with generated copies dropped), counting sentences of 8 or more words verbatim in 2 or more
  files. It finds 30 duplicates. 15 of them are only among decisions (history). Of the other 15, live cross-file
  mandates include steward SKILL/claim-files (2), root-cause/defect-root-cause, D11/RULINGS, D4/D5/D9/D10 with
  their criteria, D5/D6, and standing-dispatch/standing-merge. The definitions differ (sentence vs text_ledger unit),
  but both confirm the direction. Leave-one-out: dropping the 0001/0006 decision pair removes 7 of the finder's 16.
  Its "6 live" figure already excludes those.
- V3: policy text, not product. Consequence: a future one-sided edit forks a mandate, which is low. The seam_rule
  lists every DUP pair, so it enumerates the seams. Class: new (nearest I5).

### D11-s3-01: counts.mjs reads 1 of 3 rulesets. Vote: verify (medium). Duplicate of D11-s1-02
- V1: `ruleset_arms.py` (NODE overridden) gives rulesets_read=1, gap_arms_unmoved=4 of 4, controls_fired=3 (7, 1 and
  4 errors) and null 0. `--perturb` gives rulesets_read=2 (up, as stated) and gap_arms_unmoved=2.
  Attack: under `--perturb`, the null arm also rises to 1 error (22628467 is not in the fixture). So the moved
  `gap_22628467_bypass_added=1` equals the null arm, and its delta over null is 0. The headline metric
  (rulesets_read) still moves. D11-s1-02's perturbation, which records 22628467 in the temp fixture, gives a true
  delta of 4.
- V2 and V3: the same as D11-s1-02 (my snapshot read: 1 read of 3 active). Class I3 is confirmed. The judge should
  merge the two.

### D11-s3-02: brief_lint's CI run skips dev/programme/rosters. Vote: verify (medium)
- V1: `brief_arms.py` (NODE overridden, about 70 min under load1 60 to 220) printed null TOTAL=0, then control_3l_path 1, control_3l_count 1 and control_playbook_path 1 (3 of 3 controls fired), and gap_r10_path TOTAL=0 (unmoved). Each arm's `rosters_linted` was only `.claude/workflows/wave-3l-groups.json`. The run ended after the gap_r10 arm with no RESULT block, so the gap_r9 arm and `--perturb` were not re-taken; on the arms taken, the finding reproduces.
- V2: my own runs. The no-argument `node tools/policy/brief_lint.mjs` prints one roster header,
  `== .claude/workflows/wave-3l-groups.json ==`, and none for dev/programme/rosters. A named
  `brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` gives `TOTAL: 3 error(s)`, all R10-RELAY-NOBODY-STALL
  path:line anchors moved. Source: `main()` (l.1673-1676) takes `workflowFiles(ROSTER_FILE_RE)` only, while
  `rosterIssues()` (l.879-883) was already widened to ROSTERS_DIR by #2896 A1: the same class, fixed in one reader of
  two. tests.yml:662 (`briefs`, required) runs the no-argument form. Unlinted live rosters: 2 (wave-r10, wave-r9).
- V3: reachable in CI on every PR. Consequence: rotted brief citations reach seats unrefused. Medium holds.
  The seam_rule (`git ls-files '*wave-*-groups.json'`) also lists 5 dev/archive rosters, which are retired. It
  over-enumerates but does cover every roster. Class I3 is confirmed. I4 also fits, since two readers disagree on
  the roster set.

### D11-s3-03: policy_lint --hooks accepts an `exit 0` hook. Vote: weaken (low)
- V1: `hooks_arms.py` gives null_ok=4, control_refused=3 of 3 and gap_noop_accepted=4 of 4. `--perturb` gives
  gap_noop_accepted=0 (to_zero) with null and controls unchanged. Load1 was 217 / 178.
- V2: my own worktree. For each of pre-bash, pre-edit, session-start and stop-selfcheck, I inserted `exit 0` as
  line 2 and ran `node tools/policy/policy_lint.mjs --hooks`. Each printed `ok ... <hook>.sh` and
  `HOOKS ok: 4 wired hook(s) exist and pass their own --self-test`: 4 of 4. The source (policy_lint.mjs:7616-7624)
  sets `verdict: code === 0 ? 'ok'` and uses the tail only as `why`.
- V3: reachable in CI (policy-docs, prepr hooks step). However, `/.claude/hooks/` is code-owned
  (CODEOWNERS `@tvofi`), so neutering a hook already needs a code-owner review. The check is a second line, and the
  consequence is low. The seam_rule covers the 4 wired hooks only. The same exit-status-only reading of a self-test
  may exist in other self-test readers, and it does not enumerate those. Class I1 is confirmed.

### D11-s3-04: prepr step 5's wiring is never driven. Vote: weaken (low)
- V1: `prepr_arms.py` here: null arm 515 passed, 55 failed. The self-test is not green on this macOS seat under load, so the null control fails on this host (the same host-platform shape as N-host-platform-unrun). step5_wiring_gutted gave 515 passed, 55 failed, identical to null case for case. version_edit_gutted gave 525/45; its tally is noisy, but at case level it adds `FAIL a pull request editing VERSION is refused`, which no other arm shows. So by case the control fires and the step-5 mutant survives, which is the finding's claim. The tally-level kill (`mutants_killed=0`) is a host artefact. thread_factor 1.267, load1 50. The finder's 553/0 must be re-taken on Linux by the judge.
- V2: static. The only self-test calls that reach prepr.sh's main flow (l.2787, 2789) run with
  `PREPR_BODY_PATH_ONLY=1`, which refuses or accepts the body path. The version cases (l.2758-2767) go through
  `veco` and the `--version-edit` entry point. No case runs the main flow over a VERSION-moving head to step 5
  (l.4755-4756). So 0 cases drive the step. The single production mutation is `tools/pr/prepr.sh:4756`,
  `step "no version edit" $? "$STAMPED"` changed to `step "no version edit" 0 "$STAMPED"`.
- V3: reachable on seats. The refusal survives downstream (pr-contract's `--version-edit`, which is required, the
  pre-edit hook and the stamp), as the finding itself states, so the consequence is only slower detection: low.
  The seam_rule lists 26 `step ... $?` sites here (24 at the finder's baseline), so it enumerates the seams.
  Class I1 is confirmed.

## Cross-finding notes for the judge
- D11-s1-02 and D11-s3-01 are one defect.
- The s3 harnesses hard-code `/opt/node22/bin/node`, and s1's sweep shim needs bash 4 or later. Both fail on the
  macOS seat as written. This is a harness portability defect (N-host-platform-unrun), recorded here and not filed.
