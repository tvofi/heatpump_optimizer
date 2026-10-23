Fix review: merge c40335889dd453c206c0d6a77b6301fe7dc1a8e1
bus-nonce: 3214d3ff4dc47f2c223b90df163a11c1

Round 1, group R10-CI-LAYOUT-P2. Measured at c40335889dd453c206c0d6a77b6301fe7dc1a8e1 from a detached worktree; head re-read before posting, unchanged. Merge base 25816d5eb; `git merge-tree --write-tree origin/main HEAD` (origin/main f046076ad) rc 0. The head's delta over the code head ca1bc2b0e is a clean merge of origin/main (`git show --cc d8011956b` empty) plus `dev/programme/delivery/2673.md` alone. Roles at the merge base are current (`git diff MB...origin/main -- dev/governance/roles/` empty).

## RESULT lines

- `ruleset_cutover.py --self-test` 94 checks, 0 failed; `budget_raise_gate.py --self-test` 237/0; `gate.py --self-test` 28/0; `selftest_wiring.py --check` 91 wired, 0 unwired; `rules_sync.mjs --check` ok; `brief_lint.mjs` ok; `tests/structure.py` PASSED; head `policy_lint.mjs` rc 0, TOTAL 0, PRE-CUT-OVER note.
- Reviewer mutants: reds_at_head without `not unproven` (2 fail), main_ratchet_green always true (2 fail), gate.py taking an action_required run as a source (1 fail), gate.py source order oldest-first (1 fail) -- killed. One survivor, below.
- VERSION, manifest version, notes heading, both claim files and every `*budgets*.json`: untouched (three-dot).

## Red checks, read from the job logs, not the body

- Code-run `gate` (job 120677977400) FAILs on exactly `governance / policy-docs`, `wave-script`, `env-matrix` (this run). policy-docs (120667596076): base 25816d5eb restored, 37 errors, every one `[required-contexts]`. env-matrix (120667595648): 9 of 16 held, misses are the same refusal. wave-script (120667595745): base `agreement_py` `FileNotFoundError: .github/workflows/budget-raise-gate-rerun.yml`. Body's answer verified.
- `governance / delivery-status` (120667595774): main's ledger, now 8 overdue (#2659, #2645 added since the body's read; the body's six still listed), none #2673. Not a `gate` input. Body's answer holds in substance.
- Code-run `pr-contract / pr-contract` (120677623711): success. Edit-run `pr-contract` (120668058175): failure -- see note 2.

## Cut-over: no required context left unreported

Post-PUT the ruleset requires `[gate @ 15368]` (`NEW_CHECKS`, literal-pinned in the self-test); every `gate` check run at this head is app 15368. `ci.yml` is the only workflow with `pull_request`/`pull_request_review`/`merge_group` triggers (every other former workflow is `workflow_call`-only), it has no path filter, and `gate`'s `if: ${{ !cancelled() }}` runs on every event it takes. A GITHUB_TOKEN push's held `action_required` run leaves `gate` absent (fail-closed), and `merge-main.yml` plus the tests autofix jobs approve such runs as hpo-runs, fail-soft without secrets. An edit or review run created after a code run waits in `prelude.wait_earlier`, so its body units read a finished CodeQL; one created before is older, and `gate`'s newest-source rule does not take it (reviewer probe `edit_after_code.py`, which is the reviewer's own and not the finder's: a newer red edit-run pr-contract does redden the code run's gate, but `wait_earlier` makes that case unreachable, so the finding is withdrawn).

## Non-blocking notes

1. **`reds-at-head` refuses at this head, so step 2 (`--disable`) cannot open the window here as the body's order reads.** Live read: `(False, "reds besides the base-pinned: ['governance / delivery-status', 'pr-contract / pr-contract']")`. It counts every red in every suite. That includes `delivery-status`, which `gate` does not require, and the older edit run's fail-closed `pr-contract`, which `gate` does not source. This is stricter than `gate` and safe. To clear it before step 2: drain main's 8 overdue rows, then re-run `delivery-status` at H. Then `gh run rerun 40027562213 --failed`, which re-runs that pr-contract against the code run's finished CodeQL. Finally re-run `--dry-run --window` at H: the body's staging read is at 2efb2cc2f (#2662) and was never re-taken at this head. Carry: R10-CI-LAYOUT-P2
2. **Surviving mutant in `reds_at_head`**: inverting the per-(name, suite) newest selection (`r["id"] > newest[key]["id"]` -> `<`) fails 0 of 94 checks. Production is correct today. But a regression there would read a green first attempt over a red re-run in the same suite, and gate re-runs (sweep, refresh) are this design's routine. Owed: a fixture with attempt 1 success and attempt 2 failure in one suite, which must refuse. Carry: R10-CI-LAYOUT-P2
3. **Body figure false**: `git log origin/main..HEAD --format=%B | grep -ciE 'co-authored|claude-session'` reads 9, not 0. All 9 are `Co-authored-by: Cursor <cursoragent@cursor.com>` (e55be5744, 011a15ea3, 3aca3f7b6, 8f2790ef5, 13098f8ae, c398efe2b, ff1a0afaa, 2efb2cc2f, ca1bc2b0e). #2662's item 4 (Claude trailers) is answered: `ref_privacy.py guard --over origin/main` rc 0, and its grammar and the owner's ruling name Claude attribution only. The body's sentence is owed a correction. Carry: R10-CI-LAYOUT-P2
4. Whether the attribution ban extends to the Cursor co-author trailer is outside this PR, and no live group owns it (R10-FLY-NO-FOOTERS* all `done`). Carry: dismissed: an owner policy call, not a defect of this diff; the orchestrator raises it on #201
5. Roster carry 15 (window precondition keyed on push runs at or after #2665's merge, not the newest run's colour) is neither implemented nor dispositioned in the body. It is moot as measured: every completed push run newer than e6dd46277's merge is at or after it, and `main_ratchet_green` reads run 40026916610 at f046076ad. Carry: R10-CI-LAYOUT-P2

Forward-carries checked on `origin/handoff/audit-r10-roster` a29c7ebfb: the body's five sit at R10-CI-LAYOUT-P2 carry indices 10-14, and so do #2662's.
Evidence: RESULTS.txt and the job logs under evidence/.
