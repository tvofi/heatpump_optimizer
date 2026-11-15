# Design note: R11-PRE-TOOLCHAIN-PIN (round 4, re-cut to the minimal shape)

The payload pins `Design review: revise ab1d7b76789a6cde6d8ebf7678016790e076bda8 architecture-unsound` (ad7f4bd612). Its
point [R1] and notes [dr6]..[dr10] were answered by df3267eba7 and judged answered by the third verdict,
`Design review: revise df3267eba7d6e70490afcbdb8aa1802dc0a0c14d class-open` (f3e850c7e0, design-verdict/R11-PRE-TOOLCHAIN-PIN
tip, written two minutes after the payload). That is round 3 of 3, so by `design-review.md` this note **re-cuts to the
minimal shape**: its revise point [R3] is p1's first acceptance row, its notes [dr11]..[dr13] are carries, and every
earlier answer is kept. Base `98847b99d7bb3238686efd6869f805c89c6d1ff1` (= `origin/main`; no predecessor handoff head).
`git diff e75ad291ff 98847b99d7` over the files named here touches only `tools/audit/seat/pr_args.sh` (+41, a REST read; the
freshness function moved to `:201-210`). Evidence: owner ruling 2026-11-13 on card P1; audit row a1 at
`d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7`. No finder harness: owner ruling on a process audit.

## 1. Owning seams

| concern | owner | callers only |
|---|---|---|
| product vs machinery jobs of a push run; the pair of verdicts of one run | `tools/ci/gate.py` | `tools/release/stamp.py`, `tools/audit/seat/scorecard.py`, promote |
| the 20-run window and every share over it | `tools/audit/seat/scorecard.py` `line_a` (`:102-111`), beat cache only | the `scorecard` beat row |
| the stamp's refusal, and the single-run pair at a sha (a read-only check flag) | `tools/release/stamp.py` `tests_gate` | `dev/governance/roles/nudge.md`, `.claude/workflows/web-stamp.js` |
| the stable tools ref: name, seat paths, behind, promote | a new seat instrument named toolchain | the freshness sites of section 3, `tools/audit/seat/prune_refs.py` |
| [R3] which copy of the outside contract executes | `tools/audit/seat/merge_train.py` (`OUTSIDE_PATH`, `_outside_gate`, `outside_is_mains`) | `tools/audit/seat/merge_pr.sh`, which already reads the train's constants (`:64-72`) |

## 2. Shape (unchanged from df3267eba7 except [R3] and [dr11])

**Status.** `gate`'s conclusion never changes. `tools/ci/gate.py` gains a named tuple of machinery jobs (`tests /
arch-instrument`, `tests / briefs`, `tests / closures`, `governance / policy-docs`, `governance / wave-script`, `governance /
env-matrix`, `governance / instrument-self-tests`) and one pure function: listing and event class in, PRODUCT and MACHINERY
out, each `green | red | unread`; product is the class's required set less the tuple, computed. Unread: a member absent,
unfinished or cancelled. `tests / ci-ratchet` stays printed and in neither verdict (owner 2026-11-11: advisory on push).
Stamp rule 2 reads PRODUCT from the jobs `gate_runs` already fetches; a check flag prints the pair at a sha and writes
nothing. `scorecard.py` keeps each cached listing whole, loads `gate.py` by path, and prints A_prod and A_mach beside A_gate
and A_run over A's window.

[dr11] **`skipped`.** A skipped *required* member is red, the rule `gate.py:245` already applies ("a skipped required job"
FAILs), so a run concluded success never holds one. A skipped `governance / instrument-self-tests` (its scope chose
nothing) is not applicable: neither green nor unread; MACHINERY is over the members that ran, and unread if none did.
Under that rule the success-run shortcut (`scorecard.py:106`) equals the function on the run's own listing, which a
self-test case asserts.

**Toolchain.** Branch `toolchain/stable` points at a commit of main. *behind* `<dir> [--from <sha>] [--all]` counts
`<from or HEAD>..origin/toolchain/stable` over the seat paths. *promote* `[<sha>]`: newest main commit whose MACHINERY
is green; refuses off-main, non-ff, not green; pushes, reads back, prints `PROMOTE <utc> <old> -> <new> run=<id>`;
`PROMOTE-HELD` when the newest three concluded main runs are machinery red or unread; `--init` only while absent. A beat
row runs promote. Invariants: (i) fast-forward along main only; (ii) no checkout moves backwards; (iii) an absent ref
refuses with the init command; (iv) `HPO_ALLOW_STALE_TOOLS` keeps its meaning; (v) `gate` and the required-contexts
fixture untouched; (vi) `prune_refs.py` `classify` keeps `toolchain/*`; (vii) no second run window.

**[R3] The outside contract executes main's tree, never the checkout's.** At the base the train and the hand-merge
launcher compare the checkout's copies with origin/main's blobs on *every* pull request: `merge_train.py:2676` (`fork_head`,
called at `:2761`, `:2890`, `:2938`, `:2953`, `:3037`, `:3149`, `:3366`) and `merge_pr.sh:147` before `head_is_ours`; the
whole `OUTSIDE_MAIN_COPIES` (`merge_train.py:1258`) before the contract (`:2735`, `merge_pr.sh:151`). Under the pin both
run from `toolchain/stable`, so a merge changing `tools/pr/outside.py` (7 commits since 2026-10-15) would stop every merge
until the next promotion, and a machinery-red main would hold it there. After: `merge_train.py` owns a **main mirror**, a
detached worktree beside its checkout, moved to the origin/main sha fetched in that call (`git -C <mirror> checkout -q
--detach <sha>`, created on first use). `_outside_gate(root)` loads `tools/pr/outside.py` from the mirror, so outside.py's
`ROOT` (`tools/pr/outside.py:75`) is the mirror and every code file it reads or runs is main's; its data reads stay
`git show <ref>:<path>`. `outside_is_mains` becomes "the mirror is at the fetched origin/main sha": a mirror that cannot be
moved is a Stop naming it, never a fall-back to the checkout. `merge_pr.sh` gets the mirror root from one train verb and
sets `OUTSIDE=<mirror>/tools/pr/outside.py`; its bash comparison (`:64-79`) is deleted. Rule kept: origin/main's blob or
none, never the head's, never a stale seat's. Merge flow no longer reads promotion or machinery status.

```
merge -> main push run -> gate.py: gate (unchanged) + PRODUCT / MACHINERY
   stamp rule 2 + check flag <- PRODUCT          scorecard line_a <- function per cached run (window 20)
   beat promote <- MACHINERY green -> toolchain/stable -> behind <- every freshness site (section 3)
   train / merge_pr.sh <- fetch origin/main -> main mirror -> outside.py (main's tree)    [R3]
```

## 3. Sibling sites, enumerated

[R3] Widened enumerator: `git grep -n -E '\.\.origin/main|detach[^|]*origin/main|-B [^ ]+ origin/main|origin/main:\$?\{?(rel|tools)' -- tools/audit/seat tools/pr .claude/hooks ':!*selftest*' ':!*/instruments/*' ':!*/fixtures/*'`;
launchers with no check: `git grep -ln "pr_args.sh" -- tools/audit/seat ':!*selftest*' ':!*.md'` less `git grep -l "pr_tools_fresh" -- tools/audit/seat`;
the outside sites: `git grep -n -E 'fork_head\(|outside_is_mains' -- tools/audit/seat`.

| site | after |
|---|---|
| `tools/audit/seat/pr_args.sh:201-210` `pr_tools_fresh` (`open_pr.sh`, `update_pr.sh`) | refuses on behind > 0, naming the stable ref |
| `tools/audit/seat/beatd.py:420-465` `fresh`, `:597-607` STALE-CODE | stable ref, forward only; STALE-CODE is behind the ref |
| `tools/audit/seat/tick_loop.sh:108-139` `fresh_check` | stable ref; `CODE_PATHS` deleted |
| `tools/audit/seat/cloud_relay.sh:556-573` `tools_level` | relay worktree at the stable ref |
| `tools/audit/seat/orchestrator_tick.py:1846` | counts behind `--all`; edit of the existing count, no arm ([dr9]) |
| `tools/audit/seat/train.sh:475`, `tools/audit/seat/remerge_main.sh:29`, `tools/audit/seat/merge_pr.sh:490` | refuse on behind > 0 before work, same text and override ([dr6], carry 7) |
| [R3] `merge_train.py:2703-2720` `outside_is_mains`, `:2676`, `:2735`, `_outside_gate` `:1262-1272` | the main mirror (section 2) |
| [R3] `merge_pr.sh:64-79`, `:147`, `:151`, `OUTSIDE` `:27` | the train's mirror root; comparison deleted |

Dismissed, as in df3267eba7 and re-run at the base: `.claude/hooks/session-start.sh` (informational); `orchestrator_tick.py:1375`,
`:2133`, `:2140` (pull-request heads, handover) and `:2909`, `:2911`, `:2930`, `:3415`, `:4033` (self-test fakes);
`roster_edit.py:1083`, `:2247`, `roster_queue.py:334`, `:443`, `:622`, `closeout.py:668` (roster data follows main);
`bus.sh:2439`, `pr_args.sh:726`, `cloud_relay.sh:1532`, `beatd.py:1448`, `tick_loop.sh:406-490`, `app_approve.sh:2009`,
`app_push.sh:1258` (self-test fixtures); `tick_loop.sh:20`, `:24` (comments). Readers of `gate`: as df3267eba7 section 4,
unchanged.

## 4. Alternatives

- [R3] *Keep the checkout comparison, route the all-merge stop to the owner*: couples merge flow to promotion and so to
  machinery status, which the ruling separates.
- [R3] *Materialize only `OUTSIDE_MAIN_COPIES` with `git show`*: incomplete. outside.py runs `bash ROOT/tools/pr/app_approve.sh
  --carry` (`tools/pr/outside.py:138`), which resolves `../audit/seat/gh_read.py` (`tools/pr/app_approve.sh:166`), a file
  outside the list; every such edge would need a hand-kept closure. The mirror has the whole tree at one sha.
- [R3] *Compare against the stable ref*: an allowlist or CODEOWNERS revocation merged to main would not bind until promotion.
- A separate main-status reader; the scorecard printing one sha; `gate` concluding on product; two aggregate CI jobs;
  commit statuses; a moving tag; per-site hand repointing: lost as df3267eba7 section 3 states.

## 5. Evidence plan

| file | failing test first | null control | mutation target |
|---|---|---|---|
| [R3] `merge_train.py` self-test (first row of p1) | a checkout whose `tools/pr/outside.py` differs from origin/main's: `fork_head` admits a head of ours, having loaded outside.py from the mirror path | a mirror that cannot be moved Stops naming it; a fork head still runs main's contract | `_outside_gate` loading `ROOT`'s copy; the mirror not moved to the fetched sha |
| [R3] `merge_pr.sh --self-test` | the `FAKE_STALE` rows now pass, executing the mirror's outside.py; a policy_lint.mjs drift no longer refuses | an unmovable mirror refuses before any pull read | `OUTSIDE` set from `$PWD` |
| `tools/ci/gate.py` self-test | red only in `tests / closures`: PRODUCT green, MACHINERY red, `gate` red | red `tests / fast (3.14)`: PRODUCT red | empty tuple; unread read green |
| `tools/audit/seat/scorecard_selftest.py` | as df3267eba7; [dr11] a success run with skipped instrument-self-tests: shortcut equals function | success window prints 100% | skipped read as unread |
| `tools/release/stamp.py` self-test | a head red only in machinery stamps; check flag exits 0, writes nothing | product red or unread refuses | product = whole push set |
| toolchain self-test, `prune_refs.py` `_self_test_keeps`, the freshness sites, `open_driver_selftest.py` | as df3267eba7 section 5, carries 1 (i)-(iv) and 2 (i)-(v) verbatim | as there | as there |

Done: `scorecard.py report` prints A_prod at the fixer's merge base and after; the toolchain self-test is a measured step of
`instrument-self-tests`. No golden moves; neither claim file is touched.

## 6. Order, parts, carries

p1: toolchain instrument, section 3 sites, [R3] main mirror, prune guard, beat row, carries 1, 2, 7. p2 (after
`design/R11-PRE-PARALLEL-PIPELINE` part 2 and R11-PRE-ROUND-METRICS's cache producer): verdict function, scorecard lines,
stamp rule 2 and check flag, policy sentences (owner's review). p3: cloud seats, only if bounded. p1 lands before
`design/R11-PRE-SHARED-FILES` part 3 ([dr10]). Hot: `merge_train.py`, `merge_pr.sh` (#3619's area), `beat_jobs.py`,
`open_driver.py`, `stamp.py`. Carry 0 dismissed (no ABORT at the base, as df3267eba7). Carries 3, 4, 5, 6, 8 and the
A/B/C split: as df3267eba7 section 6, decision: orchestrator. decision: owner: the `main_green` question, who may push
`toolchain/stable` and its ruleset, and decision 0018's `product_green` (A_gate or A_prod).

## Notes for the fixer

- The mirror is a second worktree of the train's repository: put it under the train's state directory, never under the
  checkout, and have `prune_refs.py` and any worktree sweep leave it; `git worktree prune` must not drop it while the train
  runs. Re-measure its first-use wall on the Pi. Carry: R11-PRE-TOOLCHAIN-PIN (item dr14)
- `OUTSIDE_MAIN_COPIES` loses its compared role; enumerate its readers (`git grep -n OUTSIDE_MAIN_COPIES -- tools`) and keep
  it only where one remains, else delete it with its self-test row. Carry: R11-PRE-TOOLCHAIN-PIN (item dr15)
- `_outside_gate` is `lru_cache`d without arguments today; key it on the mirror sha so a main move inside one train run loads
  the new contract. Carry: R11-PRE-TOOLCHAIN-PIN (item dr16)
- [dr12] `design/R11-PRE-STANDING-SCRIPTS` part 1 moves `orchestrator_tick.py` payloads; re-anchor `:1846` after it merges.
  Carry: R11-PRE-TOOLCHAIN-PIN (item dr12)
- [dr13] #3612 left `scorecard.py` unchanged; the `after` edge on R11-PRE-ROUND-METRICS stays for the cache producer.
  Carry: R11-PRE-TOOLCHAIN-PIN (item dr13)
- Every note of df3267eba7's "Notes for the fixer" carries unchanged. Carry: R11-PRE-TOOLCHAIN-PIN

Tokens: this seat's count is not reported by the harness; no subagents.
