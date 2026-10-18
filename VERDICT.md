Fix review: blocked 63d4d2b2a16d8c04b982767a4c2c995f964ad7ed ci-red: instrument-self-tests is red at this head because of this PR — tests/throwaway_git.py --check refuses the raw `git init` the new self-test adds at tools/policy/agreement.mjs:441 (passes at base 89e33859); `## Red checks` does not name it and pr-contract refuses

bus-nonce: 7f7e6c9dcf3072191cb6d839b07c1494

Round 1 (the PR has no earlier `Fix review:` comments). Measured head: 63d4d2b2a16d8c04b982767a4c2c995f964ad7ed (still the branch tip when written). Contract current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## Blocking

1. **instrument-self-tests is red, and the PR causes it.** On both heads, 931fa7b7b (job 117819749235) and 63d4d2b2a (job 117820624145), the step `python3 -I tests/throwaway_git.py --check` prints
   `REFUSE tools/policy/agreement.mjs:441: rg(['init', '-q'])` / `throwaway_git: 1 raw git init or clone site(s) refused`, exit 1.
   Reproduced locally: the head exits 1 and base 89e33859 exits 0 (`ev/throwaway_git-{head,base}.txt`). Main is green, so this red belongs to this PR. The new real-repository self-test opens a repo with a raw `git init`. The repo's throwaway-git rule refuses that unless the site goes through the throwaway_git helper or has an `ALLOW` entry with a reason in `tests/throwaway_git.py`. There is no JS twin of the helper, so the fix is probably an ALLOW entry, which edits a tests/ instrument. Whether that is policy- or code-owned is the fixer's to check.
2. **The red is unanswered.** pr-contract (jobs 117820624071 and 117820701869) refuses with `check instrument-self-tests is red and ## Red checks does not name it`. The body's `## Red checks` names only `wave-script`, which was never red on CI. The fixer should have caught this: prepr / the instrument-self-tests lane would have refused before the push.

## Non-blocking (verified)

- (a) A recarried branch passes. I built a real recarry: 07a09406, plus a commit, plus `git merge --no-ff origin/main` (git's default subject). Main's #2423 guard: `REFUSED merge-subject-pr 644f10e96 "Merge remote-tracking branch 'origin/main' into HEAD"`, `refused=1`. This head's agreement.mjs on the same tree: `1 first-parent commit(s) past 07a09406a`, `refused=0`. See `ev/recarry-lane-{base,head}.txt`.
- (b) A custom subject on main is still refused. My probes, spliced into the self-test's scratch repo (`ev/reviewer-probes-head.txt`):
  - GitHub-shaped test merge `Merge <sha> into <sha>` over a main carrying `Merge pull request #2 (custom)`: refused=1, naming that commit;
  - test merge over a clean main with a recarried head: refused=0;
  - main's push run (HEAD = origin/main = custom merge): refused=1, which is the PR's own probe.
- (c) The fallback refuses rather than passes. With refs/remotes/origin/main deleted:
  - recarried head: refused=1, naming the branch's own `Merge origin/main into fix/x`;
  - dirty main: refused=1;
  - clean main: refused=0.
  **The self-test does not cover this arm.** Mutant 2 (`catch { return SUBJECT_CUTOFF }`, which makes the fallback walk an empty range and pass everything) leaves `SELF-TEST 26 of 26 probes held` (`ev/mutant2-fallback-pass.txt`). The behaviour is correct today but unpinned. Worth a probe on the re-cut.
- (d) Nothing weakened. The diff changes only the walk's end point; both refusal arms are intact. The commits between a stale origin/main and the PR base go unjudged on a PR run, but main's own push run judges them, and that already held before.
- Mutation proof re-run: restoring `${cutoff}..HEAD` gives `FAIL` on both recarry probes and `SELF-TEST 24 of 26 probes held` (`ev/mutant1-walk-HEAD.txt`), as the body states.
- Figures: `26 of 26` at head is confirmed. `23` at the merge base is confirmed (`SELF-TEST 23 of 23`). Lane at head: `refused=0` confirmed. `815 items`: I measure 816 at head (`ev/lane-head.txt`). The count likely depends on the local refs and tags; I cannot re-derive 815.
- Merge: `git merge-tree --write-tree origin/main 63d4d2b2a` exits 0 with no conflict.
- VERSION, the manifest version and the notes heading are untouched.
- Forward-carry: none claimed, and none needed.
- delivery-status red (OVERDUE on #2413, #2412, #2407) is not this PR's: the diff only adds its own row.
- CI at this head: the rest is green or still running (fast, coverage, browser, typing, env-matrix, CodeQL in progress when read; `ev/check-runs-head.tsv`).
