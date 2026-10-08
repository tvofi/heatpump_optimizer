Fix review: blocked e23a19ac67f1b93814e94be0b3cb78831f4348eb skip-dead: under app_push.sh's set -o pipefail, rev-list --first-parent | grep -qx exits 141 (SIGPIPE) on the real history, so an honest recarry is always refused and prepr always runs; the self-test fixture is too small to see it

bus-nonce: 99eafd414d223b3e5096445c14b1155d
seat: review-2069 (round 2; reviewed the change from 6b1d0c46)
head measured: e23a19ac67f1b93814e94be0b3cb78831f4348eb (PR body ## Head names it; live head re-read before posting)

## Round-1 findings: repaired

RESULT attack=p2-side-branch rc=1 (was rc=0): "parent 2 ... is not on the freshly fetched origin/main's first-parent chain"
RESULT control=honest-main-merge rc=0 (small fixture)
All other round-1 attacks unchanged (evidence/attack_r2_head.txt): spoof, extra commit, swapped parents, -s ours, body whitespace refuse; API/fetch failures fail closed; CRLF harmless as before.
Step 11: instrument-self-tests red at 6b1d0c46 is answered in Red checks with a cheaper detector and a root-cause routing; pr-contract and nightly-status answered. At this head, nothing red but nightly-status (not this PR's); coverage and CodeQL Analyze still in progress when read.
Local at head: app_push self-test 90/0 failed; merge_train 83/0; throwaway_git --check 0 refused.
Merge bd59a4af: clean (merge-tree of aa2e80f1 and bd59a4af equals the head tree), bd59a4af on main's first-parent chain, the four PR files byte-identical across it -- confirmed.
Note repairs: M is now parent 2 after the fetch; the RUNS note no longer claims "no resolution"; HEAD pinned in RV_HEAD and re-checked before minting (self-test rmoved). Hold.

## New blocker: the first-parent check never passes on this repository

app_push.sh runs under `set -uo pipefail`. The new check is
`git rev-list --first-parent refs/remotes/origin/main | grep -qx "$p2"`.
For an honest recarry p2 is main's tip, the first line: grep -q exits at once, rev-list is killed by SIGPIPE writing the rest (~55 KB, 1333 lines on origin/main), and pipefail makes the pipeline 141 -> the check fails.
- Real repo, tip sha, five runs: rc=141 every time.
- evidence/attack_r2_sigpipe.sh: the PRODUCTION recarry_verdict on a local clone of the real repository (1296 first-parent commits), an honest merge of origin/main into a branch: RESULT rc=1 three of three, verdict "parent 2 421c77f9 is not on the freshly fetched origin/main's first-parent chain" -- a false reason. Control, same repo, pipefail off: rc=0, SKIPPED.
Safe (fails closed), but the PR's whole purpose -- the train skipping prepr -- never happens, and the RECARRY line states a falsehood. The self-test cannot see it: the stub prints two lines, the real-git fixture a handful, both under any pipe buffer.
Fix: let grep read everything (`grep -x "$p2" >/dev/null`, or `grep -qx "$p2" < <(git rev-list ...)` with the rev-list status checked), and add a fixture with a first-parent listing past the pipe buffer (> ~1600 commits, or a stub printing p2 first followed by 100 KB).

## Other first-parent holes looked for, none found

- Depth: rev-list --first-parent walks without a limit.
- Shallow fetch: a shallow history shortens the list or fails merge-tree, so it only refuses more (fail closed).
- Rewritten main: the ruleset forbids non-fast-forward on main.
- An old first-parent main commit as parent 2: its tree is a real main state, the merge is clean and CI grades the result; within the decision.

Step 15 (fixer.md 17, on added lines): tooling, not integration code; no breach found. The check sits in the one verdict function and the note uses its outputs rather than re-reading git, which is the sound shape.
Evidence: /Users/timmalmstrom/hpo-seats/review-2069/evidence
