fix(ci): the ci-ratchet window fetch refuses instead of dying

`ci-ratchet` has failed on every push to main because its gather step fetched
the artifacts list inline as `gh api … --jq … > window.json || true`. The job
log shows the mechanism whole (job `118878630676`): gh's jq engine printed
`unexpected end of JSON input`, `|| true` swallowed the exit code, and ten
seconds later the next line died on `json.load` of a 0-byte file. What the log
names is a JSON traceback; the fetch that failed is never named, and the failed
fetch is indistinguishable from a window that is legitimately small.

The fetch, the selection and the zip download move into `tests/ci_ratchet.py`,
where `--self-test` drives every refusal offline. An empty, truncated or
wrong-shaped body is a refusal naming the fetch and the run it was for; the list
call retries with a bounded backoff, and when the attempts are spent the
refusal carries gh's exit code, byte count and stderr; an artifact that expired
between the listing and its zip download is skipped rather than aborting the
window. The selection keeps the jq query's semantics exactly — the null control
below compares the two.

`.github/workflows/tests.yml` is code-owned: tvofi approves it under mandate
6175172275.

## Head

`8457652c` — measured on that head, `origin/main` at `e4d47457`. Prepr ran as
`env PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh ~/hpo-seats/r10s3/ci-ratchet-red/body.md`
(the owner's ruling for this wave); the closures re-derivation is CI's.

## Mutation proof

One decision removed per run, `python3 -I tests/ci_ratchet.py --self-test`
after each, the file restored between runs. Every mutant printed its named
`FAIL` lines and none crashed; a crash is not a proof.

- **M0**, no mutation: rc 0, 0 red — the proof base.
- **M1**, the 0-byte guard deleted: `FAIL an empty response refuses, naming the
  0-byte fetch and its run`, rc 1. The JSON catch alone still refuses, but it
  names the byte count without the run; the guard is what makes the diagnosis
  "nothing arrived", not "the body stopped short".
- **M2**, the retry cut to one attempt: `FAIL a failed list call is retried and
  the retry's window is used`, `FAIL an rc 0 with 0 bytes is retried too`, and
  the backoff-timing arm `FAIL spent attempts refuse by name`, rc 1.
- **M3**, the expired-artifact skip deleted: `FAIL an expired artifact is
  skipped and the rest of the window survives`, rc 1.
- **M4**, the created_at ordering reverted to the null-first key this branch
  first wrote: `FAIL an artifact with no created_at does not outrank a dated
  copy` and four neighbours, rc 1. This mutant is the one the fix itself
  introduced and the self-test then caught; the commit says so.

## Null control

The base's behaviour, driven on the same 0-byte input the job produced
(`~/hpo-seats/r10s3/ci-ratchet-red/arm/arm_probe.py base`): rc 1 and
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`,
naming no fetch. The same arm at the head (`… arm_probe.py head`) is rc 1 with
`ci-ratchet: the artifacts fetch failed after 4 attempt(s): gh exited 0 and
returned 0 bytes. This is a refusal, not an empty window`.

A good response selects exactly the window the job's jq query selected: the
live response through `window_entries` and the same response through the job's
own jq expression compare `identical=True` (the command is in `## Figures`; the
count moves with each push, so only the equality is stated).

The probe can see a failure it reports absent: with `GH_TOKEN=not-a-token` the
same list call is rc 1 and its body is `{"message": "Bad credentials", …}`,
which `window_entries` refuses as having no artifacts list — a non-empty body
is not a good body.

## Figures

- `gh api "repos/tvofi/heatpump_optimizer/actions/artifacts?per_page=100"` — 28
  attempts on this seat: 28 rc 0, 70 473 bytes each. The 1-in-3 failure the
  orchestrator measured did **not** reproduce here, so the rate is not carried;
  the failing instance is the CI log's, and the class is pinned by the self-test
  arms rather than by a local rate.
- `gh api "repos/tvofi/heatpump_optimizer/actions/jobs/118878630676/logs" --allow-escape-sequences`
  — the red: `unexpected end of JSON input` then
  `json.decoder.JSONDecodeError … (char 0)`.
- `gh run list --workflow=tests.yml --branch=main --event=push --limit=16 --json databaseId,headSha`
  then each run's `…/jobs`: of the 15 runs carrying a ci-ratchet job, 14 failed
  and one passed (`2dadcdc8`); the streak from `4e5801eb` to `e4d47457` is 11
  consecutive failures in that window. My window does not reproduce the brief's
  twelve — the sixteenth run carried no ci-ratchet job.
- `gh api "repos/tvofi/heatpump_optimizer/actions/artifacts?per_page=100" --jq '[.artifacts[] | select(.name|startswith("ci-metrics-")) | select(.expired==false) | select((.workflow_run.id // .run_id // 0) != 0) | {id, run:(.workflow_run.id // .run_id), name, at:.created_at}] | sort_by(.at) | reverse | unique_by(.run,.name)' > /tmp/jqwin.json && gh api "repos/tvofi/heatpump_optimizer/actions/artifacts?per_page=100" > /tmp/rawwin.json && PYTHONPATH=tests python3 -c "import json, ci_ratchet as c; jq=json.load(open('/tmp/jqwin.json')); py=c.window_entries(open('/tmp/rawwin.json').read(), 0); print(f'identical={py == jq}')"`
  — `identical=True`, the jq-to-Python null control.
- `python3 -I tests/ci_ratchet.py --self-test` — 15 checks, 0 failed.
- `python3 tests/structure.py` — `STRUCTURE RATCHET PASSED` (load 1-minute
  interval 165 on 8 cores during the run; the verdict is a count, not a time).
- `grep -rnE '^[[:space:]]*[^#[:space:]].*\|\|[[:space:]]*(true|echo)' --include='*.yml' .github/workflows/`
  — the class's seam rule: 25 non-comment swallow sites. Every one is
  dispositioned below; the ci-ratchet list fetch was the only one that could
  read a failure as a *permissive* result.

The seam rule returns these, each already guarded or closed here. **Closed in
this diff:** the ci-ratchet list fetch and its heredoc (was `tests.yml` around
the gather step). **Already guarded, no data consumer** (a report, a mask or a
diagnostic that is printed, not read): `governance.yml:195`, `governance.yml:1122`,
`tests.yml:1345`, `tests.yml:1350`, `tests.yml:1424`, `tests.yml:3176`,
`tests.yml:3438`, `tests.yml:3727`, `tests.yml:4185`, `tests.yml:4248`.
**Already guarded, the empty is the loop's own meaning:** `merge-main.yml:169`,
`merge-main.yml:171`. **Already guarded, an absent value handled at its
consumer:** `governance.yml:1029` and `tests.yml:3856` (an empty `--since` the
linter and `record_row.py --enumerate` both refuse or accept explicitly),
`tests.yml:2570` (empty id takes the explicit re-record-fresh branch),
`tests.yml:2908` (a missing lane artifact is named in the log and the lane is
graded from the window), `tests.yml:4005` (absent and unreadable both leave the
expectation empty, which fails closed). **Already guarded, fails closed to the
conservative direction:** `governance.yml:1072` (the run summary reads
`HISTOGRAM_OUTCOME`, #1473), `tests.yml:874` and `tests.yml:876` (no
`coverage.json` reddens the job), `tests.yml:2345` and `tests.yml:2513` (an
empty diff answers `full`), `tests.yml:3049`, `tests.yml:3322` and
`tests.yml:3611` (the unswallowed push refuses a stale base). No seam is left
un-dispositioned and none is a new finding.

## Red checks

`ci-ratchet` on main — the check this PR fixes, red on the last 14 of the 15
push runs that carried it. Root-cause trigger (a check red on a commit): the
cheaper detector is the `--self-test` this PR adds, and before it none existed
— the decision lived in a heredoc no test could reach, and the job runs only on
push to main, so the first place the failure could appear was main itself. Its
standing cost is 15 offline checks: sub-second in `tests/entities.py` (which
the `fast` lane runs on every pull request) and one step in the ci-ratchet job.
Every input is synthesised, so it needs no network and no token.

## Forward-carry

`none` — the fix closes the class's only permissive seam in place; the other 24 are listed under `## Figures` with their guards, so no later stage's brief is constrained.

## Friction

`none`
