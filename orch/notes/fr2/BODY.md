_Requested by **tvofi**_

R9-FR-2 (roster brief on `handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json`, the pre-study R9-FR-1's fold verdict): `prepr.sh` gains an **ancestry red-check arm** — the fix reviewer's root-cause trigger (`defect-root-cause.md`'s enforced second trigger), moved from review time to push time. Closes #1860.

The round-9 friction sweep measured the class this answers: `root-cause-unanswered` blocked 8 of W14's 14 merges, 6 of the 8 on reds standing at **earlier branch commits**, none at the reviewed head — exactly the share a branch check-run sweep sees and nothing push-time did (`pr-contract` lists the head's runs only; a red a later push cleared leaves no check-run record at the head at all).

**What the arm is** (step 7c in `tools/audit/prepr.sh`, after the body checks):

- **The range** is `merge-base(origin/main, HEAD)..` the branch's own remote head ref, derived through `pr_head_ref` — step 7b's rule, never `@{u}` — so the arm reads exactly the check-run history a reviewer of the pull request reads, and only commits the remote already has.
- **The red key** is `pr-contract.yml`'s own ("List the red checks at this head"), reused verbatim: status `completed`, conclusion `failure`, check-run name != `pr-contract`, `sort -u`.
- **The refusal** is the SAME body check `pr-contract` runs: each red name goes to `body_check` as one `--red` per name (CI's own form; a lone `--red` value is comma-split by `policy_lint`, so one flag per name is also the only form that carries a name containing a comma). One implementation — `policy_lint.mjs --pr-body` — decides whether the body answers a red, not two.
- **Skip, never refuse, at every boundary of what the arm can see** — `gh` absent, no credential, origin not a GitHub remote, no merge base, nothing pushed, no pushed commit carrying any check run, or a read that failed — each printing its own line. policy_lint's internal red-history derivation REFUSES a failed read because it runs in CI holding a granted token; this arm runs on a seat at push time, where a hung or rate-limited call must not block a push. No CI job that re-executes `prepr.sh` exports a credential to it, so in CI the arm prints its skip line and stays local-only-deterministic — the position `PREPR_SKIP_CLOSURES` holds for the closures step.
- **The measured-green/bare distinction**: zero reds over commits that carry check runs is an **ok** ("no red check run stands"); zero reds because no pushed commit ever ran CI is a **skip** (`.total_count` pass, paid only on the all-green branch).

**Self-test**: fourteen new rows in `prepr.sh --self-test`, driven through `reds_line` (the function the step calls), over offline check-runs fixtures under `.claude/workflows/fixtures/red-ancestry/` — one directory per ancestry shape (`red`: a failure an earlier push carried and the head cleared, beside a `pr-contract` failure the exclusion key must drop; `green`: runs but no failure; `bare`: no check run at all). The fixture commits are built with fixed dates, so their SHAs are deterministic and the fixtures are keyed by them: a later edit to the construction changes the SHAs, the stub finds no fixture, and the rows fail rather than pass vacuously. The stub replaces the `gh` binary word (`PREPR_GH`) with identical argv, so the URL and the jq key are built by the production code the step runs and real `jq` applies that key over the fixture JSON. The throwaway repository is reached through `GIT_DIR`, not `cd`, because `policy_lint.mjs`'s entry guard compares `process.argv[1]` with the realpath of its own module — a `.claude` symlinked into another directory silently runs nothing (rc 0, no output), which is recorded in the self-test comment.

Alternatives rejected:

- **Feeding `policy_lint`'s internal red-history arm (a07dd57d3, #1144) a token.** It reads `GITHUB_TOKEN`/`GH_TOKEN` from the environment only, and a seat's credential lives in `gh`'s store — which is exactly why the friction persisted after that arm landed. The brief's arm asks `gh` itself. It also derives its range from the local HEAD rather than the pushed ref.
- **Copying the nightly-status/delivery-status exemption into the arm.** It already lives in `policy_lint`'s `--pr-body` machinery, which the `--red` flags feed; a second copy would drift.
- **A second red predicate.** `pr-contract.yml`'s key verbatim; re-wording it would make "what is red" depend on which caller asked.
- **A `PREPR_SKIP_REDS`-style escape hatch.** The credential boundary already produces the skip line in CI; an env var a seat could set would weaken the arm everywhere to buy nothing the boundary does not.

## Head

6a10b7e26fdf20b958fd31068b46bcef0f09ee1c (measured 2026-10-04T10:22Z; `origin/main` cc442e3ef merged in at c013ea317, merge never rebase)

## Mutation proof

Five hand mutants, each `bash tools/audit/prepr.sh --self-test` with the mutant applied, failing rows pasted, restored (`git checkout -- tools/audit/prepr.sh`):

- **red names never reach the body check** (the `for n` loop appending `--red` deleted): `160 passed, 2 failed` — "a red an earlier pushed commit carried and the body does not name is refused" and its refusal-text row.
- **exclusion key dropped** (`select(.name != "pr-contract")` deleted from `REDS_JQ`): `158 passed, 4 failed` — the answered-body null control and the green/exclusion-key row refuse.
- **arm always skips after the credential gate**: `155 passed, 7 failed`.
- **measured-green/bare distinction deleted** (the `.total_count` pass replaced by an unconditional skip): `160 passed, 2 failed` — the exclusion-key ok row.
- **head-only derivation** (`git rev-list -n 1`), the exact defect this arm exists for: `159 passed, 3 failed` — the unanswered-red row passes, which is the failure #1860 records.

`tools/audit/prepr.sh` is INERT to the gate (`tests/closure.py`), so `mutation_table.py --scope changed` draws no site in it; the self-test rows above are the pinning instrument, and CI's mutation check owns what it can select.

## Null control

- **Failing first**: at 68b1c5f86 (fixtures and rows, arm absent) `bash tools/audit/prepr.sh --self-test` reads `148 passed, 14 failed` — all fourteen new rows fail, every pre-existing row green. At the final head: `162 passed, 0 failed`.
- **Answered passes**: the same red ancestry over `red-answered.md` (a body differing from `unnamed-red.md` only in its `## Red checks` section) exits 0 — a refusal firing on everything would pin nothing.
- **No-reds passes**: the `green` fixtures (runs exist, the only failure is a `pr-contract` run) exit 0 — this is also the exclusion key's null control, and mutant "exclusion key dropped" fails exactly this row.
- **Unpushed skips**: no remote branch, an empty range, an unresolvable ref and no credential each print their skip line, never a refusal.
- **Live boundaries, real data**: `ancestry_reds origin/fix/r9-eg-b1` — the one open pull request's branch, whose CI runs are held — prints `no pushed commit carries any check run...` (rc 3); `origin/handoff/r9-f10-13`, fully absorbed by main, prints `no commit of this branch is on ... yet` (rc 3). No branch with a live ancestry red existed at measure time (one open pull request, held CI), so the refusing arm's live proof is the offline fixtures above.
- **The stats instrument's own null**: the re-measurement below without a token prints its skip line ("the commit-to-PR map could not be fetched (GITHUB_TOKEN is not set)... UNCHECKED this run") and `STATS: 0 merged pull request(s)` over no data — the phantom-zero guard, demonstrated this run.

## Figures

- `bash tools/audit/prepr.sh --self-test`: `162 passed, 0 failed` at the head; `148 passed, 14 failed` at 68b1c5f86 (failing first).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head (also run before every push).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: SCOPED -- 0 script(s) run, 30 scoped out.` — keyed on the mode line; `closure.py affected` over the diff's file list derives `affected.case` = `skip` (the diff reaches no selectable script's closure; `tools/audit/` and `.claude/` are INERT prefixes).
- `GITHUB_TOKEN=$(gh auth token) node .claude/workflows/policy_lint.mjs --stats --since v6.7.16` at the head: `STATS: 1 merged pull request(s)` in the window, verdict class `root-cause-unanswered` `1 / 1`, `WOULD OPEN: 0` (threshold 3), `GAP: 0`. The null (no token) is in Null control. This is the issue's re-measurement command; the arm's effect appears in the windows this merge opens, not in this one.
- `bash tools/audit/prepr.sh /Users/timmalmstrom/hpo-seats/r9-fr-2/scratch/fr-2/BODY.md 1860` at the final head, after the push: step `ancestry reds` runs live (real `gh`, no stub) over this branch's own four pushed commits (which carry no check runs — no pull request yet) and prints its skip line `no pushed commit carries any check run, so there is no red to answer and none confirmed absent`; every step green, `PRE-PR: 6a10b7e26...` rc 0. The run's own output is the figure.

## Red checks

`nightly-status` (expected red): it grades `main`'s last scheduled run, and this diff touches none of its inputs (`tests/nightly_status.py`, `tests/delivery_status.py`, `.github/workflows/tests.yml`, `.github/workflows/governance.yml`, the plan, `docs/HANDOVER.md` — `REPORTER_INPUTS` in `policy_lint.mjs`) and no delivery row, so its red is the orchestrator's on `main` to clear (`defect-root-cause.md`'s standing exemption; the exemption itself lives in the `--pr-body` machinery this diff's arm feeds). This branch's own pushed commits carried no check runs when this body was written (no pull request yet); the arm this diff adds is what will name any future one at the next `prepr.sh` run.

## Forward-carry

none

## Friction

none
