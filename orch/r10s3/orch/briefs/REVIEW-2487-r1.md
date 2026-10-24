# Review — PR #2487, the aiohttp security bump (round 1)

Role: **fix reviewer**. Repository `tvofi/heatpump_optimizer`. **LOCAL seat only — no cloud dispatch.**
Read `dev/governance/roles/fix-review.md` before you start: you review adversarially, from a detached worktree at the
head SHA, with your own harness.

## What you review

- PR **#2487**, head **`1a9b90965c31c6fd0093f623ec623e319fd6d3be`** — *deps: aiohttp 3.14.4 in both locks (three GHSAs)
  (R10-DEPENDABOT-AIOHTTP)*. Currently a **draft**; that is expected and not a finding.
- Bus nonce for your verdict: **`591a7fc5da599b9806df0e7db9562ac7`** (minted by `bus.sh dispatch 2487 <head> rev-2487-r1`).
- Detached worktree: `git -C /Users/timmalmstrom/heatpump_optimizer fetch origin fix/r10-dependabot-aiohttp` then
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add --detach /Users/timmalmstrom/hpo-seats/r10s3/rev-2487 1a9b90965c31c6fd0093f623ec623e319fd6d3be`
- Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/rev-2487-ev` (create it).
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH` so seat python is the venv 3.14.
- Tools: `/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/` and `/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/pr/`.

## The claim

Three GHSAs against aiohttp are closed by moving it to 3.14.4 in **both** `tests/requirements-ci.txt` and
`tests/requirements-typing.txt`. Four files in the diff: the two requirements files, a regenerated-lock-sized change in
each, and one delivery row `dev/programme/delivery/2487.md`.

## What to establish (and only this — the owner has ruled that a full local gate is not owed for this bump)

1. **Read the body's own GHSA ids** and verify from an authoritative source that each is fixed in 3.14.4 and **not** in
   the version that was there before. State the previous version and cite where you read it (the diff, the lock).
2. **The two requirements files agree.** Diff them against each other: the same aiohttp version pinned in both, and no
   pin left behind at the old version anywhere in the tree (`grep -rn 'aiohttp' tests/ pyproject.toml` etc.). A partial
   bump is the failure mode that matters here.
3. **The rest of each diff is regeneration and nothing else.** Every changed line in both files must be explained by
   the resolver: aiohttp's own pin, and the transitives whose versions moved because of it. Name any line you cannot
   explain that way — that is a finding, not a note. Check specifically for a package that changed with no path to
   aiohttp, and for a constraint that disappeared (a removed pin is a silent loss of a security floor).
4. **The delivery row** `dev/programme/delivery/2487.md` is the PR's own row, names the roster group
   `R10-DEPENDABOT-AIOHTTP`, and states a disposition rather than a placeholder.
5. **PR contract sections** in the body are present and answer the template's headings; a `nightly-status` red at the
   head that is main's own scheduled failure is not this PR's and is not a blocker (state it and move on).
6. **CI at the head.** Read check runs through `/repos/tvofi/heatpump_optimizer/commits/<sha>/check-runs` (never
   `gh pr checks`, which hides red-then-green). Do not wait indefinitely: report the state you saw with the time read.
   The suite is CI's job on this PR — **do not run the full gate locally**; if you run anything, run the narrow thing
   that answers a specific question.

## What a verdict is here

Push your verdict through the bus, exactly as `fix-review.md` and `bus.sh` require:

```
bash /Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/bus.sh push-verdict 2487 <your VERDICT.md> <your evidence dir>
```

Then report back to me: the verdict line (`Fix review: merge <40-hex head>` or `Fix review: blocked <40-hex head> <class>: <reason>`),
the review ref SHA, and each finding with what you ran to establish it.

If a load-bearing claim in the body is wrong, say so plainly — a bump that only half lands, or that carries an
unexplained pin change, is `blocked`, however small the diff looks.
