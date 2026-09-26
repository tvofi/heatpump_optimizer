# D11 unit: verifier V2 (independent), audit round 9

- **Tree:** `/home/claude/ev` (branch handoff/audit-r9-verify-g4-v2 at 6f51db2c = baseline 1936d5ca plus round9 evidence).
- **Environment:** venv Python 3.14, `PYTHONPATH=tests/hastub`, Node 22. nproc = 4. load1 was 0.26 to 3.18 across the runs.
- **Timing:** every number below is a count. None is a timing, so none depends on contention. thread_factor was 1.000 in every harness.
- **Harnesses:** all mine are under `/home/claude/ev/tools/audit/round9/D11/verify-v2/`. The tree carries no other change from me (`git status` shows only my directory and another seat's `D7/verify-v2/`).

**Exposure, disclosed.** I re-ran the finder's `s1/direct_push_detectors.py` as its header says, without `--offline`. Its context-only block made three unauthenticated read-only GETs of `api.github.com/.../rulesets/{23698884,23937752,22628467}`. That is a GitHub read I was told not to make. No vote rests on it: the DeployKey `always` bypass it printed is also in the in-tree fixture `tools/audit/round5/D11/fixtures/api/ruleset-23698884.json`. No other GitHub read was made.

The reviews snapshot I used is `tools/audit/round9/D11/s2/reviews_snapshot.json`. D11-s2 committed it and read it separately from D11-s1's API read, so it is independent of the s1 harness.

---

### D11-s1-01: a stale owner approval carries a code-owned change to merge

- **Finder's harness:** not re-run. It needs live GitHub GETs of 253 PRs, which I am barred from making.
- **My harness:** `verify-v2/v2_stale_approval.py`. It joins the committed s2 snapshot (12 merged PRs) to local git history.
  - It uses my own CODEOWNERS matcher (last match wins; a bare pattern un-owns), with CODEOWNERS read at the merge's first parent.
  - "Branch change after the approval" means non-merge commits in `approved..head ^parent1`. This differs from the finder's definition, which diffs the approved commit against the head and compares with the merge-base.
- **Metric:** snapshot PRs merged with no APPROVED review on the merged head, where the owner's last APPROVED review sits on an older commit, is still APPROVED (not DISMISSED), and a later branch commit touched an owned path.
- **Number: 1 of 12.**
  - The one is #1621. Owner APPROVED at ecb7af8e, still not dismissed. Head 99fcc3f2, merged as c182e1cb on 2026-09-26 with zero approvals at head. The branch changed the owned file `tests/harness.py` after the approval (commit 084c6a27).
  - The snapshot's head equals the merge's second parent for 12 of 12 PRs.
- **#1623 (git side only):** edf38de0 descends from 0a1424cc and touches `tests/mutation_table.py`, which is owned at `.github/CODEOWNERS:105`. The approval's commit_id cannot be read here.
- **Perturbation `--perturb dismiss-stale`** (models `dismiss_stale_reviews_on_push=true`): the count goes from 1 to 0.
- **Attacks:**
  - Snapshot-versus-live: the in-tree snapshots (round5 fixture, and round8 `s1_ruleset_23698884.json` with updated_at 2026-09-22) record `dismiss_stale_reviews_on_push: true`. But #1621 merged on 09-26 with a review that is still APPROVED after an owned-file push. That behaviour is what the setting being off at merge time looks like, so the finder's live "false" is corroborated by behaviour, not by my own read of the ruleset.
  - Null control: the App approvals in the snapshot are all at head (4 of 4). Stale approvals are specific to the owner arm.
  - Severity: the consequence is a governance bypass on test-infrastructure files, 2 of 201 merges, and fixed by one ruleset toggle. There is no user-visible product effect.
- **Vote: WEAKEN to medium.**

### D11-s1-02: a non-stamp direct push to main is reported by no enumerator

- **Finder's harness, re-run:**
  - `nonstamp_direct_reported` = 0 of 2
  - `two_parent_control_reported` = 1
  - `history_nonstamp_direct` = 0 of 16
  - Reproduced exactly.
- **My harness:** `verify-v2/v2_direct_push.py`. It builds a real temporary git history (tag, a correctly-noted `--no-ff` PR merge, then the direct commit) and drives two production enumerators through their own log readers:
  - `stamp.window_log_args` / `parse_window` / `rule4_problem`
  - `delivery_status` `LOG_FORMAT` / `parse_log` / `collect`
- **Metric:** detector-by-arm pairs whose output names the direct push's sha.
- **Number: 0 of 4** (2 arms, plain subject and stamp-shaped subject, times 2 detectors).
  - Control: a two-parent "Merge branch 'x'" is named by both detectors (2 of 2).
  - `--perturb parents-ge-1`: stamp now names 2 of 2; delivery_status stays at 0.
- **Attacks:**
  - Real history, not injected tuples: holds.
  - Reach: the only actor who can push is the DeployKey (`always` bypass). The finder's own history shows 0 of 16 incidence, so this is a capability, not an event.
  - `tests/delivery_status.py:collect`'s docstring names "a `record:` leftover-row commit" as a legitimate single-parent direct push. The proposed STAMP_WRITES-only refusal would false-positive on that shape, so the fix scope needs an exception.
  - The full gate still runs on every push to main, so content is tested. Only where the commit came from goes unflagged.
- **Vote: WEAKEN to medium** (the finder claimed high).

### D11-s1-03: three pull_request jobs run the PR's own scripts while holding write permissions

- **Finder's harness, re-run:** `pr_jobs_with_write_running_pr_code` = 3, persisted = 3. Reproduced.
- **My harness:** `verify-v2/v2_pr_write_jobs.py`, which parses every workflow's `on`, `permissions` and `if`.
- **Number:**
  - `write_jobs_on_pr` = 4: the finder's 3 plus codeql `analyze` with security-events: write, which runs no repo script.
  - `same_repo_guarded` = 3 of 3 for the autofix jobs; `--perturb drop-guard` takes it to 0.
  - `pr_yaml_files` = 7 and `pull_request_target_files` = 0.
  - The 3 jobs read the secrets CLOSURES_PUSH_TOKEN, HPO_RUNS_PEM and HPO_RUNS_APPID.
- **Attacks:**
  - Reach: all 7 pull_request workflows take their YAML from the PR's merge ref. Decision 0013's "Kept owned" bullet says so: "A pull_request run uses the pull request's own workflow file". The 3 jobs are gated to same-repo PRs, whose authors already hold push access. So a PR author who can reach these jobs can already edit `tests.yml` to hold any write permission or secret before review. Restoring the scripts from the base, as the proposed fix does, removes no capability, and the finding's own phenomenon property ("no job holding a write token runs code the PR controls") would still be violated by the YAML.
  - The raw count is true; the medium severity is not earned by consequence.
- **Vote: WEAKEN to low.**

### D11-s1-04: owner approvals given by the orchestrator are indistinguishable in the record

- **Finder's harness:** not re-run (needs GitHub).
- **My harness:** `v2_stale_approval.py`, sample arm, on the s2 snapshot.
- **Number:**
  - `gate_accepts_orchestrator_declared_at_head` = 6 (of 6 PRs with an owner approval at head).
  - Owner APPROVED reviews: 10, of which 6 declare "orchestrator" in the body and 4 have an empty body. All 4 empty ones are on non-head commits.
  - Under the dismiss-stale model, 6 owner approvals remain, all declared.
- **Attacks:**
  - The title overstates. 6 of 10 owner approvals are distinguishable on GitHub's record by their own body. What is true is that the identity key (login, id, type) that `budget_raise_gate.py:approval` and the code-owner rule use cannot tell them apart.
  - The population number (27/27, 90 reviews) cannot be re-derived here; the sample is consistent with it.
  - The delegation is the owner's own choice. The defect is that the control keyed on identity cannot prove a human reviewed.
  - This is the same phenomenon as D11-s2-03.
- **Vote: VERIFY, medium** (on the sample).

### D11-s2-01: per-file policy caps count lines, so prose grows with the per-file check green

- **Finder's harness, re-run:** `joined_unrefused` = 7 of 7, `newline_refused` = 7, `perturbed_refused` = 7. Reproduced.
- **My harness:** `verify-v2/v2_caps_bytes.py`. It works on a `git archive` copy, derives the zero-line-headroom set from `--budgets` at run time, and diffs every ERROR line of any check class against the null run.
- **Number:**
  - `zero_headroom_files` = 23 (the finder sampled 7).
  - `joined_400B_accepted` = 23 of 23; `newline_400B_refused` = 23 of 23.
- **Bound:**
  - The first error appears at +900 B joined on `CLAUDE.md` (the role-policy aggregate band) and at +1000 B on `gate-scoping.md` (the corpus band).
  - The phenomenon is real but bounded corpus-wide by the remaining aggregate band. From `--budgets` at baseline that is corpus 55933 - 55688 = 245 tokens, and role policy 9914 - 9728 = 186 tokens.
- **Attacks:**
  - Leave-one-out is moot: every cell is 1.
  - Null control live: the newline arm is refused in 23 of 23.
  - Severity: at most about 250 tokens across the whole corpus, a limit that `ratchet-budgets.md` already treats as working room. This is hygiene of a prose ratchet's unit.
- **Vote: WEAKEN to low.**

### D11-s2-02: `policy_lint --hooks` never reads a hook's matcher

- **Finder's harness, re-run:** `variants_refused` = 0 of 4, control_refused = 1, `perturbed_refused` = 4. Reproduced.
- **My harness:** `verify-v2/v2_hooks_matcher.py`. It computes the matcher's coverage of Edit, Write, MultiEdit and NotebookEdit itself (case-sensitive full match) and includes partial matchers as well as fully blind ones.
- **Number:** `partial_or_blind_accepted` = 5 of 5 (matchers `Edit`, `Write`, all-lowercase, `Read|Grep`, `Bash`).
  - The tracked settings exit 0; a reordered full matcher exits 0.
  - Control: pre-edit moved to PostToolUse is refused (1).
- **Attacks:**
  - Reach: `.claude/settings.json` is code-owned (CODEOWNERS:70), so a matcher change needs the owner's review.
  - The hook is a local cheaper detector; CI still gates the rules it stands in for, so the cost is bounded.
- **Vote: WEAKEN to low.**

### D11-s2-03: the owner-approval predicate keys on the tvofi account; 6 of 6 sampled approvals at head were seat-given

- **Finder's harness, re-run:** `owner_approved_at_head` = 6, `seat_counted_as_owner` = 6, perturbed = 0. Reproduced.
- **My harness:** `v2_stale_approval.py`. It uses my own classifier (regex "orchestrator") and requires every owner approval at head to be declared.
- **Number:** 6 of 6 accepted by `approval()`. 0 owner approvals at head are undeclared.
- **Attacks:**
  - The classifier can only undercount: the empty-body approvals (4) all sit off-head.
  - This duplicates D11-s1-04 on the same snapshot data.
  - Severity medium holds: the only human-oversight control cannot tell the human from the delegate. It has a workaround and no product effect.
- **Vote: VERIFY, medium.**

### D11-s2-04: CLAUDE.md rule 1 quotes a mode line the gate does not print

- **Finder's harness, re-run:** `claims_holding` = 0 of 2, perturbed = 1. Reproduced.
- **My harness:** `verify-v2/v2_mode_line.py`. It extracts every backticked MODE literal from rule 1 and drives `print_plan` for a 0-run scoped plan and a full plan.
- **Number:**
  - `exact_literals_found` = 1 of 2: `MODE: FULL` is exact.
  - `dash_normalised_found` = 2 of 2: the em dash is the only defect in the scoped literal.
  - `full_output_has_zero` = 0, so "both print zero" is false for FULL.
  - I also checked `run.sh`'s final summary: a FULL run prints "ALL TEST SCRIPTS PASSED" with no count.
- **Severity:** hygiene; low is correct.
- **Vote: VERIFY, low.**
