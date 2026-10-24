# Fixer — ci-ratchet dies on a swallowed API refusal, on every push to main

Role: **fixer**, one fix. Repository `tvofi/heatpump_optimizer`. Read `dev/governance/roles/fixer.md` first:
failing test first, mutation proof, a null control for every quantified claim, `GATE_SCOPE=auto`,
`tests/structure.py` before the push, and the handoff freezes the branch.
**LOCAL seat only — no cloud.**

## The red (name it in `## Red checks`)

`ci-ratchet` in `.github/workflows/tests.yml` has failed on **every push to main since `4e5801eb`**
(14:17Z) through `e4d47457` (19:51Z) — twelve consecutive runs, job ids `118802572907`,
`118878630676` and the rest. The last success was `2dadcdc8` at 14:11Z. Step 4, "Gather this run's and
the recent window's metrics", dies in ~17 s.

It is **not** required for a merge (main reads green at 42 contexts), so it has been dying quietly.

## The cause, diagnosed and reproduced

The step fetches the artifacts list as

    gh api "repos/${{ github.repository }}/actions/artifacts?per_page=100" \
      --jq '[.artifacts[] | …]' > "$RUNNER_TEMP/window.json" || true

and the next line, in the heredoc python, does `json.load(open(window))`. The `|| true` swallows a failed
or truncated `gh` call, so the file is empty and the failure surfaces ten seconds later as

    unexpected end of JSON input
    json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)

Re-measure this rather than trusting it: run

    for i in 1 2 3 4 5; do gh api "repos/tvofi/heatpump_optimizer/actions/artifacts?per_page=100" \
        >/tmp/a.json; echo "$i rc=$? bytes=$(wc -c </tmp/a.json)"; done

On 2026-10-20 the orchestrator measured **rc 1, 0 bytes, `unexpected end of JSON input` on one attempt
in three**, and clean 70 KB responses on the others. The repository has ~17 600 artifacts (3 524 pages at
five per page), so the list call is the heaviest read the workflow makes.

The same class sits one block down: the `.tsv` loop runs
`subprocess.run(["gh", "api", f".../artifacts/{id}/zip"], …, check=True)` over up to 45 artifacts, so a
single 404 on an expired artifact kills the step with a `CalledProcessError` and no naming.

This is a **recurrence**: `R10-CI-RATCHET-RED` was folded into R10-CI-LAYOUT PR 0 (#2464, `71f0bb69f`),
which merged on 2026-10-19 and did not cover this path.

## The fix

- **Never read an empty or partial response as a legitimate window.** A failed fetch is a refusal with a
  message, not a zero.
- **Retry the list call** with a bounded backoff, and name what failed and why when the retries are spent
  — the step must not fail with a traceback and no error line.
- **Tolerate an expired artifact** in the `.tsv` download (skip it and say so) rather than aborting the
  whole window on one 404.
- **Make it testable offline.** Decision 0013: an instrument the programme runs is a tracked file with a
  `--self-test`. The parsing and the retry belong in a real module (`tests/ci_ratchet.py` already owns
  this lane, or a new `tools/ci/` helper if that is cleaner), driven to green from the workflow, with the
  self-test wired into a workflow `run:` line in the same pull request — `selftest_wiring.py` refuses an
  unwired one. Do not leave the decision inside a heredoc where nothing can test it.

## Controls

- **Failing test first**: an arm that feeds the parser an empty file must redden with a message naming
  the fetch, at the base and at the head it passes. Show both.
- **Null control**: a good response must still produce the same window the step produced before — feed a
  recorded real response through and show the same artifact count and the same `unique_by` result.
- **Mutation**: remove the empty-guard and the retry, one at a time, and show each arm redden on its own
  named check. A mutant that crashes instead of reddening is not a proof.
- **The expired-artifact arm**: a 404 on one zip must leave the rest of the window intact, not abort.

## Environment and handoff

Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/ci-ratchet-red` (absolute). Worktree:
`git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/ci-ratchet-red/wt -B handoff/r10-ci-ratchet-red origin/main`.
`export PATH=/Users/timmalmstrom/.local/state/hpo/bin:$PATH` (the seat venv; never an ambient python3).
The box is saturated (8 cores, load 70+, several preprs): put anything long behind
`tools/audit/seat/daemonize.py --log`, state load1 beside every wall-clock figure, prefer counts.
`.github/workflows/tests.yml` is **code-owned** — say so in the body; I approve it under mandate 6175172275.
Roster group: **R10-CI-RATCHET-RED** (I reopen it). Push code to `handoff/r10-ci-ratchet-red` and body to
`handoff-body/r10-ci-ratchet-red`; no host path (#2310).
Report under 200 words: the cause you reproduced, what you changed, each control's rc, what you could not
establish.
