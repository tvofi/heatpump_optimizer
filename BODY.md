# docs(R9-RO): the merge-path wall-clock pre-study — prepr, the PR gate, main CI

Round-9 pre-study seat `r9-mergepath-prestudy`, on tvofi's request: a measured
wall-clock budget of the whole critical merge path — local `prepr`, one pull
request's full CI gate, and main's post-merge CI — with a duplication audit of
the heavy scripts across the three gates, reuse opportunities with safety
verdicts, scoping and parallelisation findings, and an ordered recommendation
that resolves against the two sibling pre-studies' planned pull requests.
Study only: no production file changed, no budgets file touched, no PR opened
by this seat.

## Head

a82604ae5

## Mutation proof

n/a: a measured study document, no code or check changes; nothing the
mutation ledger could pin. Every load-bearing figure cites its run id, job id
or command in §10 of the document.

## Null control

The unmodified tree's merge path IS the control: the document's §1 budget is
taken from one representative merge (#2071) exactly as the tree ran it, with
no instrument inserted — CI timings read from the Actions API, local `prepr`
timed unmodified (34 m 24 s full; 4 m 08 s with `PREPR_SKIP_CLOSURES=1`),
`tests/derive_closures.sh` never run in full locally.

## Figures

- one line per stage wall in §1's table, each with its run/job id — `gh api repos/tvofi/heatpump_optimizer/actions/runs/38031625988/jobs`
- the scoped closures arm's serial re-record (24 scripts, 51 m 18 s; boost_drift_replay.py 27 m 13 s) — `gh api repos/tvofi/heatpump_optimizer/actions/jobs/114030702792/logs`
- boost_drift_replay.py runs 7x per merge, 10 268 s = 2 h 51 m of CI lane time — sums of the per-job figures in §2's table, each cited there
- local prepr walls — `time bash tools/pr/prepr.sh` (full: 34 m 23.7 s; `PREPR_SKIP_CLOSURES=1`: 4 m 07.7 s), seat venv first on PATH
- local single-script recording — `time GOLDEN_REF=origin/main ./tests/derive_closures.sh --single tests/boost_drift_replay.py --record-only --out-dir <scratch>` (figure in §1 of the document)

## Red checks

none

## Forward-carry

none — the two planned pull requests' specifications sit on unmerged handoff refs (closures at 177bb01c3, coverage/fast at 69e374393), so no tree path can carry to them yet; section 6 of the document is the resolution, and the orchestrator hands it to those seats' briefs before they land.

## Friction

none
