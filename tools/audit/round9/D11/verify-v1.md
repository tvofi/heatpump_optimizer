# D11 round 9: verifier V1 (reproduce)

Box G4-V1, unit D11 (D11-s1-01..04, D11-s2-01..04). Worktree `handoff/audit-r9-evidence` at 6f51db2, run with `PYTHONPATH=tests/hastub` and `/home/claude/venv/bin/python` (3.14.0rc2) standing in for venv314. load1 was 1.95–3.71 and thread_factor 1.000. Every number is a count, so contention does not affect it.

## Exposure
- `GH_TOKEN` was present in the container, so the s1 harnesses ran as their headers state: read-only GETs from the harness only, with the response cache outside the tree.
- No review or comment bodies were printed from the API. The s1-04 classifier was re-counted numerically.
- The first ~110 characters of the review bodies in the committed `s2/reviews_snapshot.json` were read to check its classifier.
- No GitHub discussion, no register verdict column and no other verifier's work was read.

## Logs and harness
- Logs, under `tools/audit/round9/D11/verify-v1/`:
  - `rerun-s1-approvals{,-perturb-commit,-perturb-reattr}.log`
  - `rerun-s1-direct{,-perturb}.log`
  - `rerun-s1-priv{,-perturb}.log`
  - `rerun-s2-{caps_unit,hooks_matcher,mode_line,owner_review}.log`
  - `caps_bound.log`
- Harness written: `caps_bound.py`. It runs policy_lint in a private git worktree and removes it afterwards.

## D11-s1-01: stale owner approval merges a code-owned change (weaken, high → medium)
**Re-run** (`approvals_at_head.py`): `owned_change_after_owner_approval` = 2, the same two seams the finder named:
- `#1621 tests/harness.py @ecb7af8e->99fcc3f2`
- `#1623 tests/mutation_table.py @0a1424cc->edf38de0`

Window: 201 merges readable, 52 returned 404. `owner_approval_not_at_merged_head` = 6.

**Perturbation** (commit-clause): 0. **Null control** (app approvals not at merged head): 0/128. **Leave-one-out**: 1.

**Offline checks**:
- 4 branch commits touch `tests/harness.py` after the approval, and `edf38de0` touches `mutation_table.py`. CODEOWNERS lines 104–105 own both files.
- Live ruleset 23698884 has `dismiss_stale_reviews_on_push=false`, `require_last_push_approval=false` and `require_code_owner_review=true`.
- Decision 0008 step 3(d) specifies `true` and calls it "enforced by GitHub". Decision 0009 step 6 adopts 0008's parameter shape.

**Attacks**:
- The 404s make 2 a lower bound.
- There is no end-user consequence. Incidence is 2/201, both seams are seat commits to test and check files inside reviewed PRs, and one ruleset setting fixes it.
- That consequence is bounded, so the finding earns medium.

## D11-s1-02: a non-stamp direct push is reported by no enumerator (weaken, high → medium)
**Re-run**: 0 of 2 reported. **Perturbation** (parents-ge-1): 2. **Two-parent control**: 1. **History**: 0 of 16 non-stamp direct pushes.

**Live bypass**: DeployKey/always on 23698884 and 23937752.

**Why it misses them**: `blind_merges` reads parents>=2 only. `enumeration_went_blind` fires only when the window holds no PR, although its docstring intends that direct pushes get a human look.

**Attacks**: incidence is zero, and a push needs the deploy key, which only the stamp path holds. This is a capability, not an incident.

## D11-s1-03: write-token jobs run the PR's own scripts (weaken, medium → low)
**Re-run**: 3 jobs (closures-, claims- and mutation-autofix), each with its token persisted. **Perturbation** (restore): 0.

**My count**: 7 of the 9 workflows trigger on `pull_request`.

**Method attack**:
- On `pull_request`, GitHub runs the PR's own workflow YAML. A same-repo PR can grant itself write permissions, or reference the secret, in any job it edits.
- Fork PRs get a read-only token and no secrets.
- So the three jobs add no privilege beyond what the PR author already controls.
- The proposed restore-from-base fix zeroes the metric but leaves the stated property violated.

## D11-s1-04: orchestrator-given owner approvals (weaken, medium → low)
**Re-run**: `owner_agent_declared` = 29/90, `empty_body` = 46/90, and the gate accepts 27/27. **Perturbation** (reattribute): 2/27.

**My re-count**:
- A stricter regex gives 25/90.
- Bodies containing "orchestrator": 27/90.
- The direction holds.

**Attacks**:
- The reviews self-declare in their bodies, so GitHub's record distinguishes at least 25–29 of the 90. "Indistinguishable" holds only for the 46 empty bodies.
- The delegation is the owner's. What remains is that no in-tree decision records the mandate.
- **This duplicates D11-s2-03.**

## D11-s2-01: per-file policy caps count lines (weaken, medium → low)
**Re-run** (`caps_unit.py`): 7 of 7 cells accept the joined append. The newline arm is refused 7/7, the perturbed arm refused 7/7, and the null gives 0. **Leave-one-out**: 1 per cell.

**Own measurement** (`caps_bound.py`, 200 B steps):

| file | joined append accepted up to | first refusal (joined arm) |
|---|---|---|
| CLAUDE.md | 600 B | +800 B, role-policy aggregate (9928 > 9914) |
| delivery-status-tracking.md | 800 B | +1000 B, whole corpus (55938 > 55933) |
| gate-scoping.md | 800 B | +1000 B, whole corpus |

For all three files the newline arm is refused at +200 B.

**Attacks**:
- The per-file cap is a line cap by design.
- The prose growth it misses is bounded by the aggregate headroom, about 150–200 tokens across the corpus.
- The rule text overclaims what the per-file comparison prevents.

## D11-s2-02: `--hooks` ignores the matcher (weaken, medium → low)
**Re-run**: 0 of 4 variants refused. **Control** (script renamed): refused. **Perturbation**: 4. **Null**: rc=0.

**My extra variants**:

| settings.json variant | `policy_lint --hooks` rc |
|---|---|
| matcher `Read` | 0 |
| matcher `Edit` (partial) | 0 |
| matcher `Bash\|Read` | 0 |
| PreToolUse deleted | 1 |

No other file reads `matcher`.

**Attacks**: `pre-edit.sh`'s header says it fails open and that CI re-runs every check it stands in for. A wrong matcher therefore loses an early detector, not enforcement.

## D11-s2-03: owner predicate keys on the tvofi account (weaken, medium → low)
**Re-run** on the committed snapshot: 6/6 seat-given, 0 human. **Perturbation**: 0/0. The live superset (s1-04's re-run) gives 27/27.

**Attacks**:
- The perturbation relabels exactly the counted reviews, so it moves by construction. It does show that `approval()` keys on the login alone.
- **This duplicates D11-s1-04**, and the same severity argument applies.

## D11-s2-04: CLAUDE.md rule 1 misquotes the mode line (verify, low)
**Re-run**: 0 of 2 claims hold.
- CLAUDE.md quotes the mode line with an em-dash, but `print_plan` prints `MODE: SCOPED -- 0 script(s) run, 1 scoped out.`
- The FULL line prints no zero.

**Perturbation**: 1. **Null**: the `MODE: FULL` substring is present.

**Extra check**: `tests/run.sh:578-616` prints no zero in FULL mode (it ends "ALL TEST SCRIPTS PASSED"), and no workflow echoes a mode count.
