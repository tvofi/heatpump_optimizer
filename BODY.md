Root-cause record for the recurring "API rate limit exceeded for installation" reds on required checks (arch-score, pr-contract, env-matrix, validate-hacs; 2026-10-22 about 06:27Z, 08:40Z, 09:44:27Z). It records only; no workflow is changed. The analysis is `dev/audit/rca/install-ratelimit.md`, with an offline harness, `dev/audit/harnesses/record_api_calls.sh`, that counts the REST calls Governance's `record` job makes per push to main. Round 2: rewritten after the fix review's claim-refuted block.

- **Cause.** Every job that went red reads with `GITHUB_TOKEN`, one installation bucket shared by every workflow in the repository; HANDOVER item 44's "App quota" is another bucket. **The bucket's size is unmeasured.** GitHub documents 1,000 an hour, and round 1 took that as the limit, but Governance run `39745228063`'s record job (job `119711895503`) completed full walks (84 PRs, `RECORD_ENUM: api`, no 403) after two earlier push runs in the same minutes. The four push runs from 08:03:46Z to 08:07:08Z all succeeded and demanded 3,030 calls by the formula below, so at least about 3,030 calls were served from 08:03:46Z. That is a lower bound, not the limit. The 83 % and the 3.2 to 4.6 times the bucket are withdrawn.
- **The heaviest consumer is `governance.yml` `record`.** It runs on every push to main and walks `<last tag>..origin/main` three times (`--record`, `--stats`, `--sunset`), costing `3W + 6P` calls: 834 at `04c1dd779` by the harness, 825 by the live job at `c409c9b18` (91 PRs over 93 commits). That is hundreds of calls per push to main, against tens per PR head for the follower, pr-contract, arch-score and validate-hacs. The 08:38 record job (run `39749268769`) degraded after the 08Z burst: histograms step 15 s instead of about 112 s, friction filer failed after 0 s.
- **Bursts.** Each red fell in an hour of five or more pushes to main: 06Z, 6 pushes including the direct push `b787c7d45` (06:35Z), demand 4,305; 08Z, 6 pushes, 4,599; 09Z, 5 pushes including `04c1dd779` (#2604, 09:42Z, about 90 s before the 09:44:27Z red), 4,080.
- **Process state: (c).** HANDOVER 44 and R10-FOLLOWER-DEBOUNCE diagnosed this class and were carried out as written, but counted runs, not calls ("435 of the first 1000 listed runs"). That made the follower look like the cause and hid a job making hundreds of calls a run.
- **Cost test: passes.** Measured 3 instances a day, each at least 1 h of merge train, against a standing cost of zero for M0 to M2 and about 2 s per push for M3. The test does not depend on the bucket's size.
- **Countermeasure, in order.** M0 first: print `gh api rate_limit` in the record job, so the unit is calls and the limit is measured. Then M1 (walk the window once across the three modes, 834 to 370) and M2 (a concurrency group on `record`). M1 and M2 interact: the fix review's replay of the 08Z pushes with a 155 s job runs it about 5 times, about 1,850 calls, so the count after both is for the countermeasure group to measure. **The M3 call (an App token, or `--stats` and `--sunset` off the push arm) waits for M0's measured limit.** Retry with backoff does not help: an empty hourly bucket is not transient.
- **Owner.** `R10-RECORD-API-BUDGET` (lane IN, instrument, S, high), registered on `handoff/audit-r10-roster` for roster PR 12, carries M0 to M2, decision O-1 on M3 after M0, the HANDOVER 44 correction, and the two harness defects below.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01Wgz2w3vSn5gRBkUNkgQRm8

## Head

`4237ca684e89ff2be14054f41e790b4b671ec106` merges the authored code head `e96f64a5ad78053eb240056f135a10b08026c86d` and then merges origin/main `cd4aaed44` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`e96f64a5a` (round-1 code `0a8c4523a` with origin/main `cd4aaed44`, v7.0.3, merged in). Every count is measured with origin/main at `04c1dd77990b97ae144e48cd29655853783532f2`, the base the record and the review measured at; `tools/policy/policy_lint.mjs` and `.github/workflows/governance.yml` are unchanged between it and `cd4aaed44`. Run logs are taken from the fix review's evidence (`review/2606` `3f3e5bda1`, `evidence/record_job_runs_0803_0912.txt`, `evidence/record_job_08z_extract.txt`), not re-fetched.

## Mutation proof

n/a: this records a cause and proposes a countermeasure; it adds no check. The harness is the instrument the countermeasure's proof uses: it reads 834 at this base, M1 must bring it to 370 or below, and putting back the per-mode fetch must bring it back to 834. Its two known defects (below) are carried to the group that uses it.

## Null control

`bash dev/audit/harnesses/record_api_calls.sh origin/main` (an empty window, github remote set) reads `TOTAL 0`. The unmodified tree at the default window reads `TOTAL 834`.

## Figures

Harness lines with origin/main at `04c1dd779`; at a later main the default window is the later tag's.
- 834 calls per push (94 + 370 + 370): `bash dev/audit/harnesses/record_api_calls.sh`
- 1,065 calls per push over the wider `v7.0.1` window: `bash dev/audit/harnesses/record_api_calls.sh v7.0.1`
- 0 calls on an empty window: `bash dev/audit/harnesses/record_api_calls.sh origin/main`
- 94 first-parent commits in the window: `git rev-list --first-parent --count v7.0.2..04c1dd779`
- 825 calls by the live job at `c409c9b18` (W = 93, P = 91; its log prints 91 PRs): `git rev-list --first-parent --count v7.0.2..c409c9b18` and `git rev-list --first-parent --merges --count v7.0.2..c409c9b18`
- 92 merges in the window: `git rev-list --first-parent --merges --count v7.0.2..04c1dd779`
- per-push demand 3W+6P at each 2026-10-22 push (696 to 834; hour sums 4,305 / 4,599 / 4,080): `git rev-list --first-parent --count v7.0.2..<sha>` and `git rev-list --first-parent --merges --count v7.0.2..<sha>` per push
- 1,626 calls at the 188-commit window (177 merges): `git rev-list --first-parent --merges --count v7.0.0..v7.0.1`
- at least about 3,030 calls served from 08:03:46Z (744 + 753 + 762 + 771, lower bound): the four push runs' per-push demand above

## Red checks

- `pr-contract`, jobs `119783138386` (10:54:07Z) and `119800875823` (11:36:45Z), both at head `4237ca684`. Each log ends `BAD-DEST body item 5afde258: R10-RECORD-API-BUDGET: R10-RECORD-API-BUDGET is not a group of the roster` (the same line for items `b5f92218` and `6635e3d7`), then `CARRY-AUDIT: 4 finding item(s): 1 routed, 0 unrouted, 3 bad destination(s)`. Cause: pr-contract reads the roster from the PR tree, and `R10-RECORD-API-BUDGET` reached main only with #2608 (`543c8087c`, 11:33:58Z), after the first run and about 3 minutes before the second. Cheaper detector: `python3 -I tools/audit/carry_audit.py check --body <file>` run against the head tree before the push, about 0.1 s per push. Resolution: the base merge of origin/main that the orchestrator applies with this body. Carry: dismissed: resolved by #2608 plus this base merge; no remaining work
- No other red at this head. `nightly-status` is graded on main and is not required.

## Forward-carry

- Countermeasure M0 to M2 (`governance.yml` `record`, `tools/policy/policy_lint.mjs`); decision O-1 on M3 taken only after M0's measured limit; the M1 + M2 run count (about 5 runs, about 1,850 calls on the 08Z replay) measured by the fixer; HANDOVER item 44's "shared App quota" corrected to the `GITHUB_TOKEN` bucket at that merge (`dev/audit/rca/install-ratelimit.md` sections 4 and 5). Carry: R10-RECORD-API-BUDGET
- `dev/audit/harnesses/record_api_calls.sh` prints `TOTAL 0` with exit 0 when origin is not a github remote (the `subject` enumerator runs, no `curl`), which meets M1's "370 or less"; it should refuse a zero on a non-empty window. Carry: R10-RECORD-API-BUDGET
- `dev/audit/harnesses/record_api_calls.sh` counts a partial abort: it exits only on `curl failed`, so an `HTTP 403 from ...` or `unparseable JSON ...` fetch error ends a mode early and prints the early count as the total (review mutant: 96 instead of 278 per mode, exit 0). Carry: R10-RECORD-API-BUDGET
- An exhausted hourly bucket returns a 403 that is not transient. A retry must wait until the reset time the 403 names, and must never loop. Carry: R10-FLY-GH-READ-RETRY

## Friction

none
