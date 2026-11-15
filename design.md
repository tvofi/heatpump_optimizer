# Design note: R11-PRE-TOOLCHAIN-PIN

Base `26dbf7c43ec3742101398b098dbdcc61bbee8f19` (= `origin/main`; no predecessor handoff head: the payload says
"After: none"). Evidence: owner ruling 2026-11-13 on card P1; audit row a1 at `d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7`,
`dev/audit/rounds/round10/process-convergence-audit.md:375`. No finder harness: owner ruling on a process audit
(`findings` is empty); the row's enumerator is `gh run list --branch main --event push --workflow ci.yml --limit 40`.

## 1. Owning seams (one owner per concern, two concerns)

| concern | owner | callers only |
|---|---|---|
| which jobs of a main push run are product, which machinery, and each verdict | `tools/ci/gate.py` (it already owns `REQUIRED`, `PUSH_REPORT_ONLY`, `machinery_line`) | `tools/release/stamp.py` rule 2, the new share reader, the promotion step |
| the stable tools ref: its name, the paths compared, "behind", promotion | a new seat instrument named toolchain (Python, beside `tools/audit/seat/open_driver.py`) | `tools/audit/seat/pr_args.sh` `pr_tools_fresh`, `tools/audit/seat/beatd.py` `fresh`, `tools/audit/seat/cloud_relay.sh` `tools_level`, `tools/audit/seat/open_pr.sh`, `tools/audit/seat/update_pr.sh` |

`tests/seam_map.json` maps coordinator methods only and has no entry for either; ownership above is by `fixer.md` step 17
("the existing mechanism, never a parallel one"). Promotion reads the machinery verdict; nothing else crosses.

## 2. Shape

**Before.** Three sites each compare a checkout with `origin/main`: `PR_FRESH_PATHS` (`tools/audit/seat/pr_args.sh:189`),
its mirror `SEAT_PATHS` (`tools/audit/seat/beatd.py:113`), and the relay's whole-tree checkout of `origin/main`. The beat
hard-moves its own checkout to `origin/main` after each pass, so machinery is live on merge. On a push, the `gate` job
requires `CODE_UNITS` whole: product lanes and machinery lanes (`tests / arch-instrument`, `tests / briefs`,
`tests / closures`, all of `governance`) in one verdict, which rule 2 of `tools/release/stamp.py` reads through `GATE_JOB`.

**After, status.** `tools/ci/gate.py` splits the push class into two named tuples built by `_names`: product (`tests / fast`,
`browser`, `typing`, `mutation`, the `PUSH_ONLY` coverage pair, `codeql`, `hassfest`, `validate`) and machinery (the rest of
today's push set, plus every job `machinery_line` lists today). One pure function takes a run's jobs dict and returns both
verdicts, each `green | red | unknown` (unknown: a member unfinished or cancelled; missing input never reads green).
On push the `gate` job's conclusion becomes the product verdict; the summary prints one `PRODUCT:` and one `MACHINERY:`
line, the second replacing the report-only line. `gate_verdict` is unchanged, so rule 2 becomes "no stamp on a red product
status" with no second reader; its refusal text names product, and machinery red is printed, never refused.
A new seat instrument named main-status (reader only; imports the function, fetches through `tools/audit/seat/gh_read.py`
as `gather_runs` does, takes an offline runs file for its self-test) prints for the last N=20 `ci.yml` main push runs:
`product-green k/20 (red r, unknown u); machinery-green m/20`, one line per run, and `at <sha>` prints one run's pair.

**After, toolchain.** Branch `toolchain/stable` always points at a commit of main (a branch, so the default refspec
fetches it; `ci.yml` triggers on main only). The toolchain instrument has three verbs. *behind* `<dir>`: prints
`rev-list --count HEAD..origin/toolchain/stable` over the seat paths; the three sites call it and delete their own
constants; the relay worktree checks out the stable ref. *promote* `[<sha>]`: default the newest main commit whose machinery
verdict is green; refuses a sha not on `origin/main`, a non-fast-forward of the ref, a verdict other than green; pushes;
prints `PROMOTE <utc> <old> -> <new> run=<id>`; `--init` only while the ref is absent; `--force --why` is the
orchestrator's hotfix path and prints `PROMOTE-FORCED`. *self-test*. A beat row in `tools/audit/seat/beatd.jobs.json` runs
promote; `fresh` moves the beat's checkout to the stable ref, and only forward.

```
merge -> main push run -> gate.py: PRODUCT / MACHINERY verdicts
   stamp.py rule 2 <- PRODUCT          beat row "promote" <- MACHINERY green -> push toolchain/stable
   beatd fresh(), relay worktree, pr_tools_fresh <- toolchain "behind" <- origin/toolchain/stable
```

**Invariants.** (i) The ref only fast-forwards along main. (ii) No caller moves a checkout backwards: a checkout ahead of
the ref (count 0, on main) is left alone, which is what stops old and new beat code flip-flopping during rollout.
(iii) An absent ref refuses with the init command, never falls back to main. (iv) `HPO_ALLOW_STALE_TOOLS` keeps its meaning.
(v) On a pull request `gate` is unchanged; `tools/policy/fixtures/required-contexts.json` is untouched.

**STALE CHECKOUT under the pin** means: the checkout holding the tools lacks seat-path commits of the stable ref. It can
now arise only between a promotion and the beat's forward move, so its rate falls from per-merge to per-promotion, and it
stays an environment refusal. Carry 2's HEAD-keyed rule is therefore kept, not dropped: the key is the tools checkout HEAD,
and the forward move after a promotion is the HEAD change that retries it.

## 3. Alternatives, and why each lost

- *Two new aggregate jobs (product, machinery) in `ci.yml`*: two runner starts per push and a second place that lists the
  lanes beside `REQUIRED`; the jobs dict already carries everything the function needs, also for past runs, which is what
  lets the share be printed for the 20 runs that precede the merge.
- *Commit statuses written by the gate*: a second stored verdict that can disagree with the jobs it was derived from, and
  a `statuses: write` grant in a job that today only reads.
- *A moving tag*: `git fetch` does not move an existing tag without force, so every caller would carry its own refspec.
- *Keep three freshness sites and repoint each*: keeps the mirrored constant that `beatd.py:113` admits to.
- *Promote on product green as well*: couples tool delivery to solver reds, the reverse of the ruling's separation.

## 4. Sibling sites (run each; cover or dismiss in `## Figures`)

- `git grep -n "origin/main" -- tools/audit/seat tools/pr` : every checkout-vs-main comparison; only tool-freshness ones move.
- `git grep -n "GATE_JOB\|REQUIRED\[\|machinery_line\|PUSH_REPORT_ONLY" -- tools .github` : every reader of the push verdict.
- `git grep -n "STALE" -- tools/audit/seat` : every reader of the refusal text (`reason` in `open_driver.py:215` greps it).
- Out of scope, measured first as part 3: cloud seats, which run repo-relative tools from the session checkout at the
  dispatched head (`tools/audit/seat/cloud_dispatch.py`). Enumerator for tools that resolve the work tree from their own
  location: `git grep -n "parents\[3\]\|PR_ARGS_DIR" -- tools/audit/seat tools/pr tools/policy`.

## 5. Evidence plan, by file

| file | failing test first | null control | mutation target |
|---|---|---|---|
| `tools/ci/gate.py` self-test | a run red only in `governance / instrument-self-tests` reads PRODUCT green, MACHINERY red | a red `tests / fast (3.14)` reads PRODUCT red | emptying the machinery tuple; reading unknown as green |
| `tools/release/stamp.py` self-test (rule 2, near `gate_verdict`) | machinery-red, product-green head stamps | product-red and product-unknown heads refuse without `--allow-red` | the product tuple swapped for the whole push set |
| main-status self-test (offline runs file) | prints k/20 for a fixture of known k; a cancelled run counts unknown, not green | 20 green runs print 20/20 | window constant; unknown counted green |
| toolchain self-test (`tests/throwaway_git.py` repos) | promote refuses off-main, non-ff, non-green; behind is 0 for a checkout ahead of the ref; absent ref refuses | green on-main ff promotes and the read-back equals the pushed sha | each refusal dropped in turn |
| `tools/audit/seat/beatd.py` self-test | `fresh` moves to the stable ref, not main; ahead-of-ref checkout stays | behind-ref checkout moves | the forward-only test |
| `tools/audit/seat/open_driver_selftest.py` | carry 1 (i)-(iv) and carry 2 (i)-(v), verbatim from the brief | as the brief states | as the brief states; add the plants to `dev/audit/harnesses/r10_open_driver_mutants.py` and move its expected count |

Acceptance for "done": main-status prints the share at the fixer's merge base and after (literals in `## Figures`); the
toolchain self-test is a step of `instrument-self-tests` in `.github/workflows/governance.yml` with its measured entry in
`tools/ci/selftest_closures.json`. No golden moves; neither claim file is touched. `tests/structure_budgets.json` measures
product code only and is not reached.

## 6. Hot files, serial position, parts, carries

Hot: `tools/audit/seat/beat_jobs.py` and `dev/governance/roles/orchestrator.md` (serial across the R11-PRE groups,
`dev/programme/HANDOVER.md`), `tools/audit/seat/open_driver.py` (overlap admitted with R10-SEAT-IDENTITY-P5),
`tools/ci/gate.py`, `tools/release/stamp.py`, `.github/workflows/governance.yml`.
Parts: **p1** carries 1 and 2 in `open_driver.py` plus the toolchain instrument, its three callers and the beat row;
**p2** the status split, main-status and rule 2, with the `orchestrator.md` sentence on stamping and promotion (policy:
owner's approving review); **p3** cloud seats, only if its enumerator returns a bounded set. Each part registers its own
self-test step and closure entry in the pull request that adds the file. p1 and p2 touch disjoint files and may run in
either order; "done" needs both.
Carry 0 received and re-measured at this base: `python3 dev/audit/harnesses/r10_open_driver_mutants.py` exits 0 in 109 s
with `RESULT mutants=24`, `RESULT survived=0` and no ABORT; the three grammar plants already target
`tools/audit/seat/topic_grammar.py`. Carry: dismissed: not reproducible at 26dbf7c43e, harness runs to completion.
Carries 1 and 2 received: built in p1 as written, with the one change that the recorded HEAD is compared by the driver's
own checkout, the one the toolchain instrument's behind verb judges.

## Notes for the fixer

- The roster at the base still lists `R10-CATALOG-PR` in this group's `after` (`dev/programme/rosters/wave-r10-groups.json`),
  while the dispatch payload says none; the orchestrator reconciles before the fixer dispatches. Carry: O1
- Rollout order for p1: the orchestrator runs promote with init at p1's merge commit straight after the merge; until then
  new-code callers refuse by invariant (iii). State this in the body's merge instructions. Carry: R11-PRE-TOOLCHAIN-PIN
- `toolchain/*` is outside the `main-protect` ruleset; protecting it and naming who may push it is a live-API change only
  the owner can make. The design works unprotected because promote verifies ancestry on every read-back. Carry: O2
- `tools/audit/seat/open_driver.py` has no verb dispatch (`main` handles a board and the self-test only); the retry verb adds
  the first one. Keep `run_pass` free of argv. Carry: R11-PRE-TOOLCHAIN-PIN
- New instrument docs and the `orchestrator.md` sentence count against `dev/governance/config/policy_budgets.json`;
  measure before writing, and pay by cutting, not by a raise. Carry: R11-PRE-TOOLCHAIN-PIN
- Not verified in this seat's 1 h box: whether a seat instrument may import from `tools/ci/` (check
  `git grep -n "tools/ci" -- tools/audit/seat`); if not, main-status lives beside `tools/ci/gate.py` and is indexed in
  `tools/audit/seat/INSTRUMENTS.md`. Also unverified: which required push job was red in the 11-09..11-13 window, so the
  share at the base may already differ from the audit's run-level 0 of 36. Carry: R11-PRE-TOOLCHAIN-PIN
