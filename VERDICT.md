Fix review: blocked 43883893cd3d5a03f9d0b19b464388547b69e61c carry-missing: roster carry (dead inert_reads guard in tests/closure.py) unaddressed; guard layout:old exemption matches prose; class-open: audit-find.js finder wall misses dev/programme/register; red on merge into main 09ba95d0
bus-nonce: 52ef3f5f11b52b2ee7cf9dd36837fe78

Reviewer seat r9c-rev-2027, round 1. I measured head 43883893cd3d at merge base e0f0b6fb397b, working from a detached worktree. The head was unchanged at posting. Main moved to 09ba95d0 (#2015 merged) during the review, and the last block item was measured against that main. Evidence is in /Users/timmalmstrom/hpo-seats/r9c-rev-2027-ev.

## Blocking

1. **Carry not addressed (carry-missing).** The R9-RO-10 roster entry on handoff/audit-r9-fixplan carries one owed item, added in 8cefe802. It asks for three things:
   - extend tests/closure.py's dead-path refusal (the PHANTOM check) to `inert_reads`;
   - a perturbation that plants a dead `inert_reads` path and turns the check red;
   - removal of any dead `inert_reads` entries on main.

   The diff does not touch tests/closure.py, and the body does not disposition the carry. The new guard cannot cover it, because `tests/closures.json` is under `historical` and the guard skips it. The carry landed about two minutes before the fixer's last authored commit, so the fixer may not have seen it. It is still owed.

2. **The guard's escape hatch is wider than the body says.**
   - `FALLBACK` exempts every retired path on a line when the substring `layout:old`, `locate(` or `canon(` appears anywhere on that line. The marker is not tied to any path, and it does not have to be a deliberate marker.
   - The PR's own carry-1922 brief line passes only because its prose mentions the marker name ("mark a fixture line layout:old"). With that word changed, the line cites two landed paths without their new homes: `tools/audit/README.md` and `tools/audit/briefs/fixer.md`. See RESULT lines in `marker-hole.txt`.
   - An executed stale command passes too: `bash tools/audit/app_push.sh ... # layout:old` gives refused=False, and so does a `locate(x); ... tools/audit/app_push.sh` line.
   - The body's "a reviewer sees each use in the diff" is therefore false for an incidental mention.
   - Wanted: key the marker to the path, for example `layout:old=<path>`, or require a comment-form marker. Then re-word the carry line so it names the new paths.

3. **Class-open seam in the wave scripts.** The live findings register moved from `docs/audit-2026-09.md` to `dev/programme/register/audit-2026-09.md`.
   - `.claude/workflows/audit-find.js:198` (the Prepare prompt) and `:301` (the leads prompt, which this PR edited) still build the finder wall as "delete docs/audit-*.md, dev/archive/audits/audit-*.md, dev/archive/backlog.md".
   - `prepare_baseline.sh --strip` runs only `strip_earlier_rounds`, not `finder_wall`. So the next round's finder export keeps the live register: RESULT register_survives_audit_find_wall=yes (`wall-sim.txt`).
   - prepare_baseline.sh's own comment describes exactly this breach.
   - The guard cannot see glob citations, and neither #2014 nor #2015 touches audit-find.js.

4. **Red on the stated merge order, which has now happened.** #2015 merged as 09ba95d0. Merging this head into that main makes the PR's own guard return 5 new-reference refusals (`guard-on-live-main-09ba95d0.txt`):
   - `audit-verify.js`: three lines citing `tools/audit/bugclasses.json`, one of them also citing `tools/audit/rotation.json`;
   - `check-wave-script.mjs`: one line citing `tools/audit/scopes.json`.

   The fixer owes a re-point at the main merge. The body's merge-order section did not predict it.

## Non-blocking, to fix in the same round

5. **Rule globs narrowed without saying so.** `tools/audit/briefs/**` was re-pointed to `dev/governance/roles/**` in brief-citations, finding-propagation and writing-for-agents. Before the lift, that directory held 8 role contracts and 15 dimension briefs. The 15 dimension briefs now under `dev/governance/dimensions/` drop out of all three rules, and the body does not say so. Either add `dev/governance/dimensions/**` or state why they are dropped.

6. **The 14th dead glob has no owner who fixes it.** The body attributes the `tools/audit/briefs/**` glob in defect-root-cause.md to #2014. #2014 (head 064c5aae) edits that file, but only its prose at line 121: its diff changes no `paths:` line. No carry exists either. After both PRs merge, the glob stays dead. Carry it to #2014's group, or re-point it here.

7. **Surviving mutants of my own.**
   - Ml: drop the HEAD^1 fallback in `guard_base`. It survives, but it is equivalent in CI, because on a push GOLDEN_REF is HEAD^1.
   - Mk: the multi-category placement case (`!=1` changed to `==0`). It survives, untested.
   - Mj: the emptied-directory dedupe. It survives; it affects only the count.

## Verified

**Guard plants on the real index** (`perturb.txt`). Each plant was removed afterwards.

| plant | result |
|---|---|
| stale citation of `.claude/workflows/rules_sync.mjs` in docs/setup.md | 1 new-reference, rc=1 |
| `git mv` of `tools/audit/rotation.json`, citations left | 21 unswept, rc=1 |
| `misc/planted.txt` | 1 placement, rc=1 |
| all removed | 0 refusals, rc=0 |

**Mutants killed by `--self-test`** (`mutants.txt`): 9 of my 12 mutants were killed, namely fallback, new-path exemption, base multiset, lookbehind, re-add hit, planned exemption, fresh, skip, and emptied directories.

**Replay** (`--replay 25`, `replay25.txt`): 28 refusals in 4 non-move merges, matching the body. My judgement of them:
- #2005's 15 nudge.md refusals are true positives.
- RO-7's 3 placement refusals are a map gap.
- 10 are narrative. Re-pointing them, or naming the new path beside the old, is cheap.

**Sweep:**
- The dead-glob loop prints 14 lines at the base and 2 at the head.
- Rule-binding is live for new-path globs: I planted `dev/governance/rolesXX/**` and got an ERROR.
- fix-review vacuity: `tools/audit/briefs/` has 0 tracked files at the base, and the diff is 0 against 135 for `dev/governance/roles/`.
- `tools/audit/prepr.sh` is absent and `tools/pr/prepr.sh` exists.
- stop-selfcheck self-test: 26 passed. app_approve self-test: 145 checks, 0 failed.
- check-wave-script: 170 passed. rules_sync: ok.
- No code parses the approval text that app_approve.sh posts.

**#2005 (nudge.md):** fixed. Every script it now cites exists, apart from a deliberate "There is no tools/audit/merge_train.py".

**Budgets:**
- No cap moved; `policy_lint --budgets` output was diffed base against head.
- The added `opens` entry keeps the role measurement honest. Without it, the policy role falls from 9993 to 6938, which would be a gamed drop.
- The sentence trimmed from delivery-status-tracking ("Never touch VERSION…") is CLAUDE.md rule 4, so no obligation is lost.
- policy_lint: TOTAL 0, FIXTURE ok. structure.py: PASSED.

**Carry-1922 override of R9-RO-5:** sound. R9-RO-5 assumed that rule-binding reads only the canon list, and that no longer holds. The exceptions are measured and carried.

**Ownership census:** with `--no-renames` file lists, I count #2015 1700, #2014 19 and both 94, against the body's 1694, 19 and 93. That is my own rule, so the body's figures are close but not re-derived exactly.

**Merge order:** if this PR had landed first, its guard would refuse #2014 (2 new-reference) and #2015 (8 new-reference and 134 unswept).

**Other:** VERSION, the manifest, RELEASE_NOTES and the claim files are untouched. merge-tree against 09ba95d0 exits 0. The head in the PR body matches the head I measured.

## CI at the head (check-runs API)

- fast (3.14), closures and mutation: success.
- coverage was still in progress when I posted.
- budget-raise-gate has one cancelled run and a successful twin. The cancelled run still needs a re-run, because a cancelled run blocks the merge.
- delivery-status (main's unread rows) and nightly-status are red. Neither is this PR's, and the body answers both.
- The gate is MODE: FULL, from comment-only changes to tests.yml.

## RESULT

```
RESULT guard_plants stale=1 unswept=21 placement=1 clean=0
RESULT reviewer_mutants killed=9 survived=3 (Mj count-only, Mk untested, Ml CI-equivalent)
RESULT replay25 nonmove_refusals=28
RESULT dead_globs base=14 head=2
RESULT marker_hole carry1922_line hidden=2 executed_line_with_marker refused=False
RESULT finder_wall register_survives=yes
RESULT guard_on_merge_into_09ba95d0 new_reference=5
RESULT role_policy with_opens_add=9993 without=6938
```
