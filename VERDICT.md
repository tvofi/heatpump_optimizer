Fix review: blocked 1c42ca3fda183b63a6c3579071bef9a8e354acef ci-red: required gate red at this head on a cancelled codeql / Analyze (python); the code itself passes review

bus-nonce: 5175f81ab13194d5507c6b1eccb38446

Round 2 of the fix review for #3217 (R10-HOTFIX-RECORD-ATTRIB round 2). It is a delta review after verdict/3217 blocked f190c717 mutation-vacuous. Everything was measured at head 1c42ca3fda183b63a6c3579071bef9a8e354acef, from a detached worktree at that SHA. That SHA was still the PR head when the check runs were last read (~03:46Z).

## Block

`merge_train.py classify 1c42ca3fda183b63a6c3579071bef9a8e354acef --pr 3217` exited 1 and printed `RED 1c42ca3fda183b63a6c3579071bef9a8e354acef pending: none red: gate`. A red CI never carries (fix-review.md step 12), so this head cannot take a merge verdict.

Both `gate` runs at this head concluded red:
- Run 41953777322 printed `FAIL codeql / Analyze (python): cancelled (run 41953331353)`. That job ran from 02:21:26 to 03:06:36 and then ended cancelled.
- Run 41953331353 printed `FAIL run(s) [41953777322] at this head are still being judged; their gate decides`. That run defers to the first one.

The diff touches no Python (it changes tools/policy/policy_lint.mjs and dev/programme/delivery/3217.md), so the cancelled CodeQL leg is not something this change produced. Nothing in the code review below stands against the head.

To clear the block:
1. Re-run the cancelled `codeql / Analyze (python)` job and let the gate re-judge. This is the `hpo-runs` / orchestrator lane. This seat posts and re-runs nothing.
2. Answer `## Red checks` for whatever still concludes red at that point. The body currently says "none concluded" because it was written before CI ran. The last pr-contract run (03:42:43) started before the last red gate concluded (03:44:16), so no green pr-contract run has yet checked the body against these reds (step 11).

With a green gate and that answer in place, a re-review needs only the CI re-read. The code evidence below carries, because the patch is unchanged.

## Findings

- Refusal wording: the `why` string names both causes as two distinct alternatives: "that pull request's merge commit differs from it, or /pulls/<n> could not be read (HTTP error or rate limit)". It does not say which of the two happened. `confirmGapMerge` still returns a single boolean, so a red run reads "one of two". The round-1 ask, that both causes be named, is met. Mutant M8 shows the pin holds that wording. Saying which cause occurred would be a diagnostic refinement, not a correctness one, because both causes refuse identically, and record_row.py's Refuse does not distinguish them either. Carry: dismissed: both causes refuse identically; naming both as alternatives meets the round-1 ask
- Unused stub arm: the enumeration pins never drive the unreadable-/pulls branch through `fetchPullsBySha`. `gapEnumGet`'s `merge === null` arm (HTTP 404) is defined but never called. That branch is covered at the helper level: the pin "could not be read was confirmed" kills M1. The guard treats both false causes the same, so no mutant separates them at the enumeration level. Carry: dismissed: covered by the helper pin; the enumeration guard has a single false path

## Evidence

- RESULT M0 null control (unmutated, head 1c42ca3f): `FIXTURE ok: 93 error(s) hold 266 pins across 12 check classes`, rc 0. The body's figure of 266 is re-derived. The round-1 verdict measured 263 at f190c717, so +3 matches the three added pins.
- RESULT M3 (the round-1 reviewer's mutant; the guard block in `fetchPullsBySha` deleted): `FIXTURE VACUOUS ... "an enumeration gap whose pull request merged at a different commit was trusted, or its refusal does not name both causes"`, rc 1. KILLED at the enumeration level. M0 is the null control.
- RESULT M1 (`confirmGapMerge` returns true): rc 1, three pins fail, including the enumeration-differs pin. Killed.
- RESULT M2 (returns false): rc 1, the helper-equal pin and the enumeration-recovered pin fail. Killed.
- RESULT M4 (sha equality dropped): rc 1. Killed.
- RESULT M5 (the guard calls `ghGet` instead of the injected `get`): rc 1, "enumeration gap ... not recovered and listed in gapShas". Killed. The injection is load-bearing.
- RESULT M6 (`gapShas.push` deleted): rc 1. Killed.
- RESULT M7 (the guard also applied to API rows): rc 1, "an enumeration API row was not taken as the number". Killed.
- RESULT M8 (the "could not be read" clause dropped from `why`): rc 1. Killed.
- All mutant output is in ev/mutants.txt. The worktree was restored clean (`git status --short` empty).
- The three enumeration-level pins the brief asks for are present and each is reached:
  - API row: taken as '42', absent from gapShas.
  - Gap where `/pulls/900` merge_commit_sha equals the sha: recovered as '900' and listed in gapShas.
  - Gap whose merge commit differs: `ok:false`, with a `why` matching /could not be read/.
- Python half: the three-dot diff against merge base 499162c89d0f4f8369e16e6e41fb3a620bc1ecb0 touches only dev/programme/delivery/3217.md and tools/policy/policy_lint.mjs. record_row.py is unchanged.
- merge-tree with origin/main (`git merge-tree --write-tree origin/main 1c42ca3f`): rc 0, no conflicts (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched by the three-dot diff.
- Roles drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so fix-review.md is current.
- Check runs (ev/ci-reds.txt) were read from the PR's check-runs API: 56 runs, one page of 100, plus the jobs of run 41953777322.
  - Concluded non-green:
    - gate ×2: failure (see Block).
    - codeql / Analyze (python): cancelled.
    - governance / delivery-status: failure. It lists overdue rows #3089 (2a9cd34) and #3192 (d4e584e), both other pull requests, and says it is not a required context. The diff adds dev/programme/delivery/3217.md, which delivery-status reads, but #3217 is not among the rows it flags.
    - tests / nightly-status: failure. The diff reaches nothing nightly-status reads. Its log tail carries only cleanup lines; I did not read the full log.
  - Green: tests / fast (3.14), coverage, closures, mutation, browser, typing, instrument-self-tests, policy-docs, arch-score, budget-raise-gate, and pr-contract (twice).
- Finder's harness: the packet names none. The brief's live-API case (616868bd answering [] for #3179) was not re-queried, so it is not re-derived.
- The fix-review.md steps 2–4 measurements (finder's harness at both ends, env_drift) do not apply here: no harness is named, and no fixture or claim moved.

## Friction

- The frugal-routing hook (`guard`, inline search budget 5) refused a plain `cat` of my own mutant output and a Monitor wait partway through the review. I cleared it through the hook's own route (one scout delegation to relay the file) rather than overriding it. Carry: dismissed: session tooling, not a repository process
