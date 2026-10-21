fix(ci): the ci-ratchet window fetch refuses instead of dying

`ci-ratchet` fails on main's push runs in two distinct ways. This PR fixes one of
them. Its gather step fetched the artifacts list inline as
`gh api … --jq … > window.json || true`. When gh's jq engine printed
`unexpected end of JSON input`, `|| true` swallowed the exit code, and the next
line died on `json.load` of a 0-byte file. The traceback named no fetch, and a
failed fetch could not be told apart from a window that really was small (CI job
`118878630676`).

The fetch, the selection and the zip download move into `tests/ci_ratchet.py`,
and `--self-test` drives every refusal offline. An empty, truncated or
wrong-shaped body is refused, and the refusal names the fetch and the run it was
for. The list call retries with a bounded backoff; when the attempts are spent,
the refusal carries gh's exit code, byte count and stderr. An artifact that
expired between the listing and its zip download is skipped rather than
aborting the window. The selection keeps the jq query's semantics exactly; the
null control below compares the two.

The other way, `GREW critical_path_minutes`, is the job graph's wall time. This
diff does not move it, and R10-CI-LAYOUT owns it (`## Red checks`).

`.github/workflows/tests.yml` is code-owned: tvofi approves it under mandate
6175172275.

## Head

`a5dede8e009ffb9088286a3d68a92e9451494c04`: this seat's merge of origin/main
`03b49e1521a2490335922093c9177aec8f6119d9` into the previous head
`fddca8122bf61800022c7ee848188a6c235b2047`. The merge was clean, with no
conflict and no resolution. The three-dot diff (`git diff $(git merge-base
origin/main HEAD)...HEAD --stat`) is unchanged: `.github/workflows/tests.yml`,
`tests/ci_ratchet.py` and `tests/entities.py`. Main's delta since the old base
touched `tests.yml` and `tests/entities.py` outside this diff's hunks, so steps
2–8 were re-executed on this head. Every figure below was taken at this head,
with `origin/main` at `03b49e15`, on 2026-10-21 between 11:30Z and 12:00Z
(`date -u`). Prepr ran as `env PATH=<3.13 venv>/bin:$PATH PREPR_SKIP_CLOSURES=1
bash tools/pr/prepr.sh ~/hpo-seats/r10-ci-ratchet-red/body.md` and printed `clean
no refusal` (`PREPR_SKIP_CLOSURES` is the owner's ruling for this wave; the
closures re-derivation is CI's). The venv is named because
`tools/audit/seat/seat_venv.sh` failed here: `No download found for request:
cpython-3.14.7-linux-x86_64-gnu`. The PATH `python3` is 3.11, which cannot parse
the tree, and the first prepr run refused `no-copies` and self-test 6b for that
reason alone. The 3.13 venv is `tests/requirements-ci.txt` installed without
`--require-hashes`.

## Mutation proof

Each run removed one decision from a pristine copy of `tests/ci_ratchet.py` and
then ran `python3 -I tests/ci_ratchet.py --self-test`. The file was restored
between runs, and `git status` was clean after the last. Every mutant printed
its named `FAIL` lines and none crashed.

- **M0**, no mutation: rc 0, `15 checks, 0 failed`. This is the proof base.
- **M1**, the 0-byte guard in `window_entries` deleted: rc 1, `FAIL an empty
  response refuses, naming the 0-byte fetch and its run (not an empty window)`.
  The JSON catch still refuses, but it reports "0 bytes of incomplete JSON"
  without the run. The guard is what makes the diagnosis "nothing arrived".
- **M2**, `FETCH_ATTEMPTS` cut to 1: rc 1, `FAIL a failed list call is retried
  and the retry's window is used` and `FAIL an rc 0 with 0 bytes is retried
  too, not read as a window`. The spent-attempts arm passes its own `attempts=3`
  and stays green, as it should.
- **M3**, the expired-artifact `skipped.append(art); continue` replaced by a
  fall-through to the refusal: rc 1, `FAIL an expired artifact is skipped and
  the rest of the window survives`.
- **M4**, the `created_at` ordering reverted to the null-first key
  `(r["at"] is None, r["at"] or "")`: rc 1, five `FAIL`s, led by `a good
  response still yields the window (the null control)`, `a duplicate (run,
  name) keeps the newest copy` and `an artifact with no created_at does not
  outrank a dated copy`.

## Null control

The base's own code on the job's input: I extracted the merge-base gather
heredoc from `tests.yml` verbatim and ran it on a 0-byte `window.json`. It exits
rc 1 with `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char
0)` and names no fetch. Run on the same 0-byte file, the head's
`ci_ratchet.window_entries(…, 39548715713)` exits rc 1 with `ci-ratchet: the
artifacts fetch returned 0 bytes for run 39548715713; refusing to read that as
an empty window`.

A good response selects exactly the window the job's jq query selected. I
fetched one raw artifacts response, then ran it through the job's jq expression
(standalone `jq`, the same input) and through `window_entries`. The two compare
`identical=True`. With the first entry dropped from jq's answer, the same
comparison prints `identical=False`, so the comparison can see a difference.
The window's size moves with every push, so only the equality is stated.

The previous body's bad-token arm is not re-taken. On this seat the egress proxy
supplies its own credentials, so `GH_TOKEN=not-a-token` returned rc 0 and a full
list. The wrong-shape refusal is pinned offline by the self-test arm `a no
artifacts list artifacts response refuses (not an empty window)` instead.

## Figures

- `python3 -I tests/ci_ratchet.py --self-test`: `15 checks, 0 failed`. M1–M4
  were run against this command (`## Mutation proof`).
- `for i in $(seq 1 12); do gh api "repos/tvofi/heatpump_optimizer/actions/artifacts?per_page=100" > a$i.json 2> e$i.txt; echo "$? $(wc -c < a$i.json) $(head -c 80 e$i.txt)"; done | sort | uniq -c`:
  of 12 attempts, 11 were rc 0 with a full body, and 1 was rc 1 with 0 bytes
  and `unexpected end of JSON input`. This is the CI failure reproducing on this
  seat without `--jq`, so it belongs to the fetch itself and not to gh's jq
  engine. A rate from 12 draws is not carried; the class is pinned by the
  self-test arms. The first jq-shaped fetch this seat made failed the same way.
- `gh api "repos/tvofi/heatpump_optimizer/actions/artifacts?per_page=100" > raw.json && jq '[.artifacts[] | select(.name|startswith("ci-metrics-")) | select(.expired==false) | select((.workflow_run.id // .run_id // 0) != 0) | {id, run:(.workflow_run.id // .run_id), name, at:.created_at}] | sort_by(.at) | reverse | unique_by(.run,.name)' raw.json > jq.json && PYTHONPATH=tests python3 -c "import json, sys, ci_ratchet as c; print(f'identical={c.window_entries(open(sys.argv[2]).read(), 0) == json.load(open(sys.argv[1]))}')" jq.json raw.json`:
  `identical=True`. The same command with `json.load(...)[1:]` prints
  `identical=False`.
- `gh run list --workflow=tests.yml --branch=main --event=push --limit=16 --json databaseId,headSha`,
  then for each run `gh api repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs`.
  For the `ci-ratchet` job I read its conclusion and the steps whose conclusion
  is `failure`. The 16 runs end at `03b49e15`, whose run carried no ci-ratchet
  job yet. Of the 15 that carried one, 2 passed (`9e2f6ed9`, `0cc148b2`). 8
  failed in `Gather this run's and the recent window's metrics`, the step this
  PR replaces. 5 failed in `Grade the ratchet` (`265d3bf1`, `8fbc60dd`,
  `c77f89dc`, `739c8369`, `70b6c88a`). Each of those five logs' only non-`ok`
  graded line is `GREW critical_path_minutes`, at 57.28, 57.28, 54.88, 56.5 and
  55.98 against the budget 54.825.
- `env PYTHONPATH=tests/hastub python3.13 tests/entities.py`: `ALL 2381 ENTITY
  CHECKS PASSED`, rc 0. The seat's PATH `python3` is 3.11, which cannot parse
  `tests/entities.py` (a PEP 701 f-string), so these ran in a 3.13 venv built
  from `tests/requirements-ci.txt`.
- `env PYTHONPATH=tests/hastub python3.13 tests/harness_headers.py`: `ALL 109
  HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/env_drift.py --claims-only 03b49e1521a2490335922093c9177aec8f6119d9`:
  `claims hygiene: … ok`. Neither claim file is in the diff.
- `python3 tests/closure.py selftest`: `ALL 124 closure shrink pins PASSED`.
  `python3 tests/layout.py`: `layout self-test: ok`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`:
  `MODE: FULL`, because `.github/workflows/tests.yml changes the gate itself`.
  The full suite is CI's (fixer.md step 5).
- `grep -rnE '^[[:space:]]*[^#[:space:]].*\|\|[[:space:]]*(true|echo)' --include='*.yml' .github/workflows/`
  is the class's seam rule. It returns 25 sites at this head and 26 at the merge
  base `03b49e15`. Compared on file plus text (line numbers removed), the only
  difference is the ci-ratchet list fetch this diff closes. Main's 53 new
  `tests.yml` lines added no seam.

Every site the seam rule returns at this head is dispositioned; line numbers are
at `a5dede8e`. **Closed in this diff:** the ci-ratchet list fetch and its
heredoc (the gather step of the `ci-ratchet` job). **Already guarded, no data
consumer** (a report, mask or diagnostic that is printed, not read):
`governance.yml:195`, `governance.yml:1122`, `tests.yml:1345`, `tests.yml:1350`,
`tests.yml:1424`, `tests.yml:3176`, `tests.yml:3438`, `tests.yml:3727`,
`tests.yml:4185`, `tests.yml:4301` (the merge job's `cat merge-resp.json` after
its own `::warning::`). **Already guarded, the empty is the loop's own
meaning:** `merge-main.yml:169`, `merge-main.yml:171`. **Already guarded, an
absent value handled at its consumer:** `governance.yml:1029` and
`tests.yml:3856` (an empty `--since` that the linter and `record_row.py
--enumerate` each refuse or accept explicitly), `tests.yml:2570` (an empty id
takes the explicit re-record-fresh branch), `tests.yml:2908` (a missing lane
artifact is named in the log and the lane is graded from the window),
`tests.yml:4005` (absent and unreadable both leave the expectation empty, which
fails closed). **Already guarded, fails closed in the conservative direction:**
`governance.yml:1072` (the run summary reads `HISTOGRAM_OUTCOME`, #1473),
`tests.yml:874` and `tests.yml:876` (no `coverage.json` reddens the job),
`tests.yml:2345` and `tests.yml:2513` (an empty diff answers `full`),
`tests.yml:3049`, `tests.yml:3322` and `tests.yml:3611` (the unswallowed push
refuses a stale base). No returned seam is left without a disposition, and none
is a new finding.

## Red checks

- `pr-contract`, red twice at `fddca812` (jobs `118951336129` and
  `118973391411`): both failed only at `carry_audit.py check`, with `UNROUTED
  body item 3521abe2 (## Forward-carry)`. The previous body put prose after
  `none` under `## Forward-carry`, and the audit reads that as a finding with no
  destination. This body's `## Forward-carry` is a bare `none`. The cheaper
  detector already exists: `prepr.sh` runs the same `carry_audit.py check`
  before the push, and it passes on this body.
- `nightly-status`, red at `fddca812`: the last concluded scheduled run
  `39387919507` (head `0c298f6`) failed `slow` on `FAIL synthetic-dhw-only.json:
  cycle_cost [1 offender(s): loop_cpu_ratio 0.1114 over its budget 0.111]`.
  This diff touches no replay code or budget. The roster already owns the red:
  R10-REPLAY-CAP names run `39387919507` and this budget, and R10-REPLAY-LANE
  carries the same measurement. The check is unrequired.
- `ci-ratchet` on main, run `39548715713`, job `119065361551`: `GREW
  critical_path_minutes: 56.5 (budget 54.825)`. This red is not this PR's. The
  grade step reads the job graph's wall time on the recent push runs, which this
  diff does not change. The five Grade-step failures in `## Figures` all grew
  this metric alone. R10-CI-LAYOUT owns it in the roster
  (`origin/handoff/audit-r10-roster`, `dev/programme/rosters/wave-r10-groups.json`),
  which already records this run, the `56.5` against `54.825`, and the job graph
  as PR 1/PR 2's. So no new route is written here. One consequence for review:
  once this PR merges, `ci-ratchet` on main stays red until R10-CI-LAYOUT pays
  the critical path. The gather step will then pass, and the job will fail at
  the grade, naming the metric.
- `ci-ratchet` on main, Gather step (8 of the 15 runs in `## Figures`): this is
  the check this PR fixes. Root-cause trigger: the cheaper detector is the
  `--self-test` this PR adds, and none existed before it. The decision lived in
  a heredoc no test could reach, and the job runs only on push to main, so the
  first place the failure could appear was main itself. Its standing cost is 15
  offline checks: sub-second in `tests/entities.py`, which the `fast` lane runs
  on every pull request, plus one step in the ci-ratchet job. Every input is
  synthesised, so the self-test needs no network and no token.

## Forward-carry

`none`

## Friction

`none`

🤖 Generated with [Claude Code](https://claude.com/claude-code) · https://claude.ai/code/session_01Hfabwv39uWj3PHP4XMZXiu
