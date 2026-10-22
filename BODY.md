Root-cause record for the recurring "API rate limit exceeded for installation" reds on required checks (arch-score, pr-contract, env-matrix, validate-hacs; 2026-10-22 about 06:27Z, 08:40Z, 09:44Z). It records only; no workflow is changed. The analysis is `dev/audit/rca/install-ratelimit.md`, with an offline harness, `dev/audit/harnesses/record_api_calls.sh`, that counts the REST calls Governance's `record` job makes per push to main.

- **Cause.** Every job that went red reads with `GITHUB_TOKEN`, whose bucket is 1,000 requests an hour per repository, shared by every workflow. The brief's 5,000/hr and HANDOVER item 44's "App quota" are other buckets. The consumer that empties it is `governance.yml` `record`. It runs on every push to main and walks `<last tag>..origin/main` three times (`--record`, `--stats`, `--sunset`), so each push costs `3W + 6P` calls. The harness measured 834 calls at `04c1dd779`, and the live job at `c409c9b18` read 91 PRs over 93 commits (825 calls). So one push to main uses 83 % of the hourly bucket. Each of the day's three reds followed a burst of 4 to 6 main merges, which asked for 3.2 to 4.6 times the bucket. The follower, pr-contract, arch-score and validate-hacs make tens of calls per head; they are where the bucket was found empty, not what emptied it.
- **Process state: (c).** HANDOVER 44 and R10-FOLLOWER-DEBOUNCE diagnosed this class and were carried out as written, but they counted runs, not calls ("435 of the first 1000 listed runs"). That made the follower look like the cause and hid a job that runs 4 times an hour at 834 calls a run.
- **Cost test: passes.** Measured 3 instances a day, each costing at least 1 h of merge train. Against that, M0 to M2 cost nothing or save time on every run, and M3 adds about 2 s per push.
- **Countermeasure.** M0: print `gh api rate_limit` in the record job, so the unit is calls. M1: walk the window once and share it across the three modes (834 → 370). M2: a concurrency group on `record` so a burst runs it at most twice. M3, the owner's call: give the O(window) job an App installation token, or take `--stats` and `--sunset` off the push arm. Without M3 the class returns as the window grows. Retry with backoff does not help: an empty hourly bucket is not transient.
- **Owner.** No live group owns the record job. This proposes a new group, `R10-RECORD-API-BUDGET` (lane IN, instrument, S, high), for M0 to M2, plus a separate owner decision on M3. Until the orchestrator registers it, R10-CI-LAYOUT-P2 holds the carry, because it is the live group that already lists `governance.yml`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01XayfiVpWu23h9aUKRv2LLm

## Head

`0a8c4523a76a1154bb634ce24c9dc110f1b170a8` on base origin/main `04c1dd77990b97ae144e48cd29655853783532f2`; every count is measured at that base.

## Mutation proof

n/a: this records a cause and proposes a countermeasure; it adds no check. The harness is the instrument the fixer's mutation proof uses: it reads 834 at this base, M1 must bring it to 370 or below, and putting back the per-mode fetch must bring it back to 834.

## Null control

`bash dev/audit/harnesses/record_api_calls.sh origin/main` (an empty window) reads `TOTAL 0`. The unmodified tree at the default window reads `TOTAL 834`.

## Figures

- 834 calls per push (94 + 370 + 370): `bash dev/audit/harnesses/record_api_calls.sh`
- 1,065 calls per push over the wider `v7.0.1` window: `bash dev/audit/harnesses/record_api_calls.sh v7.0.1`
- 0 calls on an empty window: `bash dev/audit/harnesses/record_api_calls.sh origin/main`
- 94 first-parent commits and 92 merges in the window: `git rev-list --first-parent --count v7.0.2..origin/main`

## Red checks

none

## Forward-carry

- Countermeasure M0 to M2 (`governance.yml` `record`, `tools/policy/policy_lint.mjs`), the owner decision on M3, and correcting HANDOVER item 44's "shared App quota" to the `GITHUB_TOKEN` bucket at that merge. R10-CI-LAYOUT-P2 is the only live group that already lists `governance.yml`, so it holds these until the orchestrator registers the proposed `R10-RECORD-API-BUDGET` (`dev/audit/rca/install-ratelimit.md` section 5). Carry: R10-CI-LAYOUT-P2
- An exhausted hourly bucket returns a 403 that is not transient. A retry must wait until the reset time the 403 names, and must never loop. Carry: R10-FLY-GH-READ-RETRY

## Friction

none
