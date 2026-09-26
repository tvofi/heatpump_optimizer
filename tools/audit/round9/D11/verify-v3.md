# D11 round 9: verifier V3 (reach and class)

Tree: /home/claude/wt at 6f51db2c. That is baseline 1936d5ca plus the round-9 evidence commits. `git diff --stat 1936d5ca 6f51db2c -- ':!tools/audit/round9'` is empty, so the production code measured is the baseline's. Machine: 4-CPU cloud container, CPython 3.14 (/home/claude/venv314), node 22. Every number below is a count, so contention does not affect it. Each harness printed load1 between 0.26 and 3.74 and thread_factor 1.000.

**Constraint on step 1.** Two finder harnesses read the GitHub API: `s1/approvals_at_head.py` and the ruleset arm of `s1/direct_push_detectors.py`. This seat's brief forbids reading GitHub, so neither was re-run against the API. I ran `direct_push_detectors.py --offline`. For D11-s1-01, -s1-04 and -s2-03 the votes rest on the committed `s2/reviews_snapshot.json` and local git.

**Reach in real Home Assistant.** None of the 8 findings touches an HA code path or a `tests/hastub` symbol, so `tests/ha_contract.py` does not apply. I assessed reach on the real counterpart instead: GitHub rulesets and Actions, Claude Code hooks, and the gate's logs.

My harnesses are in `tools/audit/round9/D11/verify-v3/`: `v3_owner_approvals.py`, `v3_direct_push.py`, `v3_pr_privilege.py`, `v3_caps_bound.py`, `v3_hooks_matcher.py` and `v3_mode_line.py`. Each runs as `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python <path>`.

## D11-s1-01: stale owner approval merges a code-owned change. Vote: weaken to medium
- **Metric:** of snapshot PRs whose tvofi last APPROVED review is not on the merged head, count those where:
  - the branch-own commits after that review (`git rev-list <approved>..<head> --not <merge^1>`) touch a CODEOWNERS @tvofi path; and
  - no APPROVED review from anyone sits at the head.
- **Result:**
  - Snapshot: `stale_owner_with_owned_change_no_head_approval=1` (PR 1621). Under `--perturb commit-clause` it is 0.
  - `snapshot_head_ne_merge_parent2=0`, so the snapshot's heads match git.
  - #1623 is not in the snapshot. Using the finder's approval commit 0a1424cc, the single branch-own commit after it (edf38de0) touches code-owned `tests/mutation_table.py`.
  - Total 2, which matches the finder.
- **Reach (real GitHub):**
  - PR 1621's only review is tvofi APPROVED at ecb7af8e. Its state is still APPROVED, not DISMISSED.
  - The PR merged at 99fcc3f2 after three branch commits (084c6a27, 0d679a28, 8f7abb96) changed code-owned `tests/harness.py` (62 lines).
  - Under a ruleset requiring one approval plus code-owner review, that only happens if stale approvals are kept. This confirms dismiss_stale=false indirectly, with no API read.
  - Decision 0008 step 3(d) specifies `dismiss_stale_reviews_on_push: true`. Decision 0009's landed note lists only the approval count and code-owner review, so the "recorded as enforced" half of the claim rests on 0008 alone.
- **Severity:** both instances changed test-harness files, not production or policy, and no wrong value shipped. The cost is bounded, so high is inflated; medium.
- **Seam rule: partial.** It enumerates the 201 API-readable merges of the 253 first-parent merges since the rule landed (`window_first_parent_merges_since_rule=253`). The 52 merges that answer 404 are not enumerated.
- **Class:** I3 confirmed.

## D11-s1-02: a non-stamp direct push passes every enumerator. Vote: weaken to medium
- **Finder harness (`--offline`):**
  - `nonstamp_direct_reported=0` of 2; two-parent control 1; history: 16 of 16 single-parent commits since v6.5.0 lie within STAMP_WRITES.
  - Under `--perturb parents-ge-1`: 2.
- **Own measurement (`v3_direct_push.py`):** real window v6.7.0..v6.7.1^ (8 rows) with the real v6.7.1 notes.
  - Null: rule4 returns None and `collect` leaves nothing unattributed.
  - Real branch commit 084c6a27 injected with 1 parent: named by 0 of 2 enumerators (`rule4_problem` and `delivery_status.collect`).
  - Same commit with 2 parents: named by 2 of 2. Under the perturbation, 1 parent: 2 of 2.
- **Reach:** real GitHub. The DeployKey bypass is taken from decision 0009's landed note, because the ruleset read is forbidden to this seat.
- **Severity:** incidence is 0 of 16. The push needs the deploy key, which only the stamp seat holds, and a push to main forces the FULL gate. A functional break would go red; only provenance escapes. Capability-only and key-gated, so medium.
- **Seam rule: partial.** It drives only `rule4_problem`. My harness adds `collect`, which is also blind. policy_lint's `enumerateMerges` is not exported, and its own comment says it skips any first-parent commit with no PR.
- **Class:** I3 confirmed.

## D11-s1-03: autofix jobs run PR scripts with a write token. Vote: weaken to low
- **Finder harness:** 3, with the token persisted on disk in all 3. Under `--perturb restore`: 0.
- **Own measurement (`v3_pr_privilege.py`):**
  - 5 jobs a PR can start hold a write permission or a secret. 3 of them read CLOSURES_PUSH_TOKEN, HPO_RUNS_APPID and HPO_RUNS_PEM.
  - After the finder's restore fix: 0 of 3 run PR-controlled code (null).
  - After the fix plus one PR-side edit of `tests.yml` (a step running a file the PR adds): 3 of 3 again.
- **Reach:** a same-repo `pull_request` run executes the PR's own workflow file; `budget-raise-gate.yml`'s header says so. A branch pusher who can edit `tests/closure.py` can equally edit these jobs' `run:` lines. The three scripts add 0 jobs of privilege beyond what the branch pusher already has, and the proposed fix does not close the property.
- **Severity:** low.
- **Seam rule: partial.** It enumerates jobs in the current YAML, not the seam where the PR supplies the workflow file itself.
- **Class:** I3 confirmed.

## D11-s1-04: delegated owner approvals look like the owner's. Vote: verify, medium
- **Own measurement:** the production `approval()` accepts 6 snapshot PRs. All 6 (`gate_accepts_delegate_declared=6`) have an owner review at head whose body names the orchestrator or the mandate; 0 are undeclared.
- **Finder's number:** 27/27 over 90 approvals. It needs the API and was not re-run.
- **Reach:** real GitHub. The reviews are under id 70032254, type User. `git grep` for 70032254 or OWNER_LOGIN finds one code consumer, `budget_raise_gate.py`, and it cannot separate them.
- **Duplicate:** this is the same phenomenon as D11-s2-03 (same predicate, same bodies). The judge should keep one.
- **Seam rule: partial.** It counts PRs over the readable window (52 of 253 unreadable), not the identity consumers.
- **Class:** corrected from "new" to I3. The code-owner review is a required governance check, and anyone holding the owner's credential crosses its human boundary.

## D11-s2-01: per-file caps count lines, not prose. Vote: weaken to low
- **Finder harness:** `joined_unrefused=7`, `newline_refused=7`, `perturbed_refused=7`.
- **Own measurement (`v3_caps_bound.py`):**
  - 41 of 41 per-file caps report 0 per-file errors on +600 B appended to an existing line. 40 of those files are measured by POLICY_GLOBS; `fixtures/policy-rot/budgets.md` is measured by none.
  - Bisected on CLAUDE.md, the largest joined append with no budgets error at all is 736 B (~184 tokens). The first refusal above it comes from the role-policy aggregate cap.
  - Under `--perturb bytes`: 1 of 41 blind (the unmeasured fixture), and CLAUDE.md's silent growth is 0 B.
- **Severity:** the seam is every per-file cap, not only the 7 with zero headroom. The growth is bounded by the aggregate bands (184 tokens here), so this is hygiene: low.
- **Seam rule: enumerates.**
- **Class:** I3 confirmed.

## D11-s2-02: `--hooks` ignores the matcher. Vote: verify, medium
- **Finder harness:** 0 of 4 variants refused; control 1; under the perturbation 4.
- **Own measurement (`v3_hooks_matcher.py`):**
  - On the tree: 0 of 5 variants refused. The five are PreToolUse `Edit`, `Write|Edit`, `edit|write` and `Read`, and SessionStart `compact`.
  - Under the finder's own perturbation: 2 of 5 refused. `Edit`, `Write|Edit` and SessionStart `compact` still pass.
- **Reach:** real Claude Code honours PreToolUse and SessionStart matchers.
- **Severity:** `pre-edit.sh` fails open by design and CI re-checks its rules, so a missed refusal costs one CI round. The misconfiguration needs a code-owned `settings.json` edit. Bounded, so medium is kept.
- **Seam rule: partial.** It prints every (event, matcher) pair, but the property, the perturbation and the proposed fix test only PreToolUse against `Edit`.
- **Class:** I3 confirmed.

## D11-s2-03: owner approvals at head are seat-given. Vote: verify, medium
- **Finder harness:** 6 of 6; perturbed 0.
- **Own measurement:** 6 of 6 with a different body regex (`orchestrator|mandate`).
- **Sample:** drawn by rule (`git log --merges --first-parent -12`), not hand-picked.
- **Mandate:** `git grep -i mandate` finds it in no decision record; 0009's step-6 note cites a different mandate.
- **Duplicate:** of D11-s1-04.
- **Seam rule: enumerates** the in-tree identity consumers. `budget_raise_gate.py` is the only code consumer; the ruleset is outside the tree.
- **Class:** corrected from "new" to I3.

## D11-s2-04: CLAUDE.md quotes a mode line the gate does not print. Vote: weaken, low
- **Finder harness:** 0 of 2 claims hold; perturbed 1.
- **Own measurement (`v3_mode_line.py`):** it drives the real `closure.py select --diff HEAD`, which printed `MODE: SCOPED -- 0 script(s) run, 26 scoped out.` The em-dash literal CLAUDE.md quotes is absent from that output (0); with the perturbation it is present (1).
- **Claim (b), "both print zero":** under an exit-status reading, a 0-run scoped gate and a passing full gate both exit 0, so (b) is not shown false. The defect is claim (a) alone: 1 of 2 claims hold, not 0 of 2.
- **Seam rule: partial.** Across the policy corpus there are 9 quoted output literals; only CLAUDE.md's is absent from every code file. The seam rule scans 3 of them and misses `tools/audit/briefs/` and `tests/README.md`.
- **Class:** I5 confirmed.
