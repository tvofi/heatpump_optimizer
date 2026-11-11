# D13-s1 report (round 10), baseline 17f1c55fad1b

Cells: D13.M1 (first-pass yield, rounds per merge), D13.M2 (verdict coverage by class), all files.
Window: first-parent merges in `1913f0dd7` (v6.7.16 stamp) `..origin/main` (= baseline).

Harness: `dev/audit/rounds/round10/D13/s1/yield.mjs` (header carries metric, command, perturbations).
Run: `GITHUB_TOKEN=$(gh auth token) node dev/audit/rounds/round10/D13/s1/yield.mjs --since 1913f0dd7`
Output at baseline: `yield.baseline.out`.

## M1
- Window 185 merges, api_failures 0; set diff against production `mergedPRsFromWindow` = 0.
- 163 merges carry a parsable verdict; 434 verdicts (434 issue comments, 0 reviews); 0 outside grammar.
- First-verdict yield 100/163 = 0.613. Rounds per merge: mean 2.663 (434/163), max 14 (#2066).
  Histogram 1:60 2:41 3:22 4:16 5:8 6:5 7:4 8:4 9:2 14:1.
- Production `policy_lint.mjs --stats --since 1913f0dd7` printed the same 163/185, 100/163.
- `fetchWindow` reads one page of 100 comments/reviews; against a fully paginated read it dropped 0
  verdicts and truncated 0 PRs in this window (non-finding; a latent cap, no PR exceeded it).

## M2 — finding D13-s1-01
22 of 185 merges carry no parsable verdict: 17 record/chore (`record`, `docs`) of 47, 2 fix of 88
(#2203, #2173), 3 other (#2196 closure, #2179 test, #2005 policy). All authored by hpo-author[bot].
No rule under dev/governance or CLAUDE.md exempts record PRs (grep for "exempt" finds only
defect-root-cause.md, unrelated). Production `--stats` prints the 22 as one capped list of 10
numbers with no class split, so it cannot compute M2's per-class row itself.
Perturbation: `--reshape-one` re-shapes #2191's single verdict out of grammar: coverage 163 -> 162,
no_verdict 22 -> 23 (executed).

## Exposure
Read GitHub API for the window: /commits/<sha>/pulls, /pulls/<n>, /issues/<n>/comments,
/pulls/<n>/reviews for 185 PRs (753 requests, cached under $TMPDIR/d13s1-cache-1913f0dd7);
verdict content used as population only.

## Unfinished
None for M1/M2. load1 was 15.18 (shared box); all numbers are counts.
