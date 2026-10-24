The merge train's pre-flight (`queue_pre_flight.findings_gate`, which runs `carry_audit.audit`) parked three `Fix review: merge` verdicts. In each, `carry_audit.items()` read evidence or notes as finding items with no `Carry:`: #2513 item 3b97e1aa (issue comment 6314156311), #2544 item aeeb9432 (6314170570) and #2547 item b579380b (6315224098). This change adds a barrier at the source, in two parts (owner-approved 2026-10-21: "do that").

**Lands after #2556.** #2556 (head 1beed40bf, `fix/r10-cloud-rev-head-ev`) edits the same reviewer prompt. This branch merges #2556's head and does not rebase onto it. Merge #2556 first, then this PR. Its diff against #2556 is the four files below.

1. **The prompt.** In `tools/audit/seat/cloud_dispatch.py`, the reviewer prompt now separates findings from evidence. A blocked verdict's block goes under `## Block`. Each finding the PR does not settle goes in its own bullet under `## Findings`, ending in its own `Carry:`. Everything else goes under `## Evidence`. The prompt also lists the words that still make an evidence item a finding.
   `fix-review.md` is unchanged. It defers the verdict's shape to the dispatch prompt ("in the exact shape your dispatch prompt gives"), so this changes no policy file and no role contract. `finding-propagation.md` still holds as written: every non-blocking note or residual still needs a `Carry:`.
2. **The classification.** In `tools/audit/carry_audit.py`, an item under a verdict's `## Evidence` heading is a finding only if it hands something on. The evidence requirement is not weakened.
   **How a finding under the heading is still caught.** An item there is a finding when any of these holds:
   - it opens with `LEAD`;
   - it sits under a lead;
   - it says `DEFERRED` anywhere (`follow-up`, `for/to/in/until a later`, `out of scope`, `not fixed here`, `known-open`, `distinct finding`, `residual`, `caveat`, `observation`, `still has/have/needs to`);
   - it says `NONBLOCK` (non-blocking, not blocking, deferred, minor, advisory, ...).

   There is one exception. NONBLOCK is not read inside a single **sentence** that calls its check not a required one (`NOT_REQUIRED`: "not (a) required context|check"). Such a sentence states a check's state, not a note.
   That one sentence-scoped carve-out is the whole relaxation. Everything else under the heading is read at least as strictly as on main, and the `DEFERRED` words make it stricter.
   The heading is read only in a verdict. `RESULT` lines stay trailers, as on main.

Alternatives tried, and why each lost:
- **Exempting `NONBLOCK` under `## Evidence` entirely.** Under the what-if below, that freed a nit (#2441: "One nit, not blocking") and a defect left in place (#2465: "written 0.27 K low ... so it is not blocking"). That is smuggling, so it was refused.
- **Applying the evidence rule to `RESULT`/`Evidence:` lines everywhere.** Over the 84-PR sweep this added 6 distinct refusals on real verdicts (#2465, #2469, #2479, #2516). Every one was a false positive ("a run 0.2 s later", a quoted residual), so it was reverted.
- **Bare `later`.** It fires on times like "0.2 s later", so it was narrowed to the prepositional deferral.

## Head

821507dca0f1e238cb832d265946b4590504d6f2. It is cut from origin/main 289426c1f (`git merge-base origin/main HEAD`), and #2556's head 1beed40bf is merged in. Every figure below was taken at this head unless it names the merge base, 289426c1f.

## Mutation proof

- **M-A**: delete the evidence branch of `items()` (the `elif verdict and EVIDENCE_HEADING.match(sec):` arm and its body, 4 lines).
  `python3 -I tools/audit/carry_audit.py --self-test` then prints `182 checks, 30 failed`. The failing checks include:
  - `under the Evidence heading a check that is not a required context and does not block is no finding`
  - `the carve-out is its sentence's: a nit after it is a finding (#2441's shape)`
  - `a defect left in place, not blocking, under the Evidence heading is a finding (#2465's shape)`
  - `a deferral under the Evidence heading is a finding`
  - `a `;` ends a sentence: a nit after a not-required check's clause is a finding`
  - 22 more, including one `DEFERRED reads <w>` check per word.

  Under M-A, the replay `python3 dev/audit/harnesses/r10_verdict_item_barrier.py` prints `v2544_reshaped=1 v2544_planted=2`, the merge-base figures. Restored with `git checkout`.
- **M-B**: delete the new prompt sentences in `cloud_dispatch.py`.
  `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` then prints `31 checks, 1 failed`, and the failing check is `the reviewer is told to separate findings, each with its own Carry:, from evidence`. Restored.
- **Every predicate alone.** `python3 dev/audit/harnesses/r10_carry_parser_mutants.py` enumerates the parser's sites from its AST and kills each mutant by itself. This PR adds the new sites to it: 6 `I-ev-*` arms, `I-ev-split`, `P-sentence-semi`, `P-notreq-a`, `P-ev-word`, and the generated `V-NOT_REQUIRED-*`, `V-DEFERRED-*` and `V-EVIDENCE_HEADING` alternatives.
  - At the head: `RESULT sites=168 unmapped=0 mutants=224 survived=0`.
  - At the merge base: `sites=152 unmapped=0 mutants=190 survived=0`.
  - In an intermediate state, six `DEFERRED` words that duplicated `NONBLOCK` survived as equivalents. They were removed from `DEFERRED` rather than recorded as equivalent.
- **Failing first.** The self-test rows were written before the fix. In that first draft of the rows, at 289426c1f's classification, the self-test printed `173 checks, 23 failed`. The rows as they stand now fail under M-A (the head's rows with the classification arm removed), at 30 of 182.

## Unpinned sites

n/a: every site the diff adds is pinned by `r10_carry_parser_mutants.py` (unmapped=0, survived=0 above). `mutation-autofix` has nothing to pin.

## Null control

- **The planted control.** The `planted` form of each replay adds one `## Evidence` bullet that states a defect and defers it ("The stale-head guard misses a deleted ref; deferred to a later round."). It is refused for all three verdicts: `v2513_planted=1 v2544_planted=1 v2547_planted=1`.
- **The real smuggle shapes.** #2441's nit and #2465's defect are self-test rows, and both are read as findings under `## Evidence`.
- **Posted verdicts are untouched.** `carry_audit.py pr 2513`, `pr 2544` and `pr 2547` print the same refusal at the merge base and at the head (`1 finding item(s): 0 routed, 1 unrouted`). This is the finder's instrument, and it reads flat at both ends because the fix rightly leaves posted, old-format verdicts alone. The replay harness is the companion that moves (fixer.md step 3).

## Figures

Instrument: `python3 dev/audit/harnesses/r10_verdict_item_barrier.py --fetch`. It replays the three posted verdict comments verbatim; `--fetch` re-reads them read-only and prints `fetch_<pr>=identical`. Each verdict runs in four forms (the harness header defines them), and each form prints the count of finding items not routed.

| form | head (2513 / 2544 / 2547) | base 289426c1f |
|---|---|---|
| verbatim | 1 / 1 / 1 | 1 / 1 / 1 |
| evidence | 1 / 1 / 1 | 1 / 1 / 1 |
| reshaped | 0 / 0 / 0 | 0 / **1** / 0 |
| planted | 1 / 1 / 1 | 1 / **2** / 1 |

- **What the rows show.** At the base, #2544's CI paragraph ("`composed-proof` is still queued, but it is not a required context and does not block the PR") is refused under any heading. At the head, the `evidence` form (text moved under `## Evidence`, unedited) still refuses each verdict, on the item that hands something on:
  - #2513: "noted for a later tightening";
  - #2547: "advisory";
  - #2544: a post-merge check that "still has to be done". The base never flagged this one.
- **Real-corpus sweep, both ends.** `python3 -I tools/audit/carry_audit.py sweep --prs <84 PRs> --from-dir DIR`. The corpus is the last 80 merged PRs by update time plus #2513, #2544, #2547 and #2556: 84 PRs, 59 `Fix review:` verdicts.
  - Base and head both print `CARRY-AUDIT: 131 finding item(s): 85 routed, 42 unrouted, 4 bad destination(s)`. The UNROUTED/BAD-DEST line sets are identical (`diff` returns 0).
  - Null control for "changes nothing that is not under the new heading": an earlier draft, which extended the rule to `RESULT` lines, moved this sweep to 138/49.
- **Adversarial what-if.** `python3 dev/audit/harnesses/r10_verdict_item_barrier.py --whatif DIR`, over the same corpus, renames every heading of every verdict `## Evidence`.
  - Base: `whatif_flagged=18`. Head: `whatif_flagged=32`.
  - The one item flagged at the base and not at the head is #2544's aeeb9432 (`diff` of the FLAGGED id sets). The head's extra 14 come from the added `DEFERRED` words.
  - In a real verdict, much of what they catch sits under `## Block` (for example, #2452's and #2469's block text). Under the new format that text is not read as notes.
- **Cheap checks at the head** (run with `PYTHONPATH=tests/hastub`):
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`
  - `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused`
  - `python3 tools/audit/archscore/score.py --diff 289426c1f`: `Architecture score: dS +0.0000 NULL`
  - `python3 tests/closure.py select --diff 289426c1f`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and it runs `tests/entities.py`
  - run_always: `env_drift.py --claims-only`: `claims hygiene: ... ok`; `closure.py selftest`: `ALL 124 closure shrink pins PASSED`; `layout.py`: `layout self-test: ok`
  - `harness_headers.py` and `entities.py` under `/opt/hpo/venv-ci` (3.14.7): `ALL 109 HARNESS HEADER CHECKS PASSED`, `ALL 2375 ENTITY CHECKS PASSED`
- **The generator, run** (fixer.md step 10). `python3 -I tools/audit/seat/cloud_dispatch.py --role reviewer --head <40-hex> --pr 7 --nonce n0nce --env-id e --model m --repo o/r`. At the head, the rendered message contains `## Findings`, `## Evidence`, `## Block` and "not a required check". At 289426c1f it contains none of them. `grep -c` for each of `## Evidence`, `## Findings`, `## Block` and `not a required check` gives 1 at the head and 0 at the base.
- **The class, enumerated** (fixer.md step 8). The seam is every path by which a verdict item becomes "not a finding" in `items()`. `r10_carry_parser_mutants.py`'s `sites()` enumerates them from the AST: 168 sites, 0 unmapped. Their dispositions:
  - the new `## Evidence` arm: closed in this diff;
  - `TRAILER` (attribution, `bus:`, `Evidence:`, `RESULT`): unchanged, already exempt on main. Extending the evidence rule to it was measured as 6 false positives and 0 true ones over the corpus;
  - `block_sec` (a block heading): unchanged; the block is owed in this PR;
  - the lead paragraph: unchanged; its bullets carry.

  The other reviewer-prompt generators were found with `git grep -l "Fix review: merge" .claude tools`:
  - `.claude/workflows/web-fix-wave.js` (code-owned; its verdicts reach the same pre-flight): not changed here, see Forward-carry;
  - `web-decomp-stage.js` and the retired `audit-wave.js` and `audit-fix.js`: not changed.

## Red checks

none

## Forward-carry

- `.claude/workflows/web-fix-wave.js` (code-owned) is the local reviewer prompt. It still asks only for RESULT lines after the first line, so a local-seat verdict can still be parked on a check that does not block. The pre-flight fails closed: it parks, it never passes an unrouted finding. Adding the same three-section format there is the owner's call on a code-owned file. Carry: dismissed: fail-closed park only, owner's code-owned prompt
- The three posted verdicts stay parked under the head (`carry_audit.py pr N` is unchanged). Each needs a reviewer re-post in the new format, or a `Carry: <dest> (item <id>)` that routes it: #2513 3b97e1aa, #2544 aeeb9432, #2547 b579380b. This is the orchestrator's next step on those PRs, not a defect. Carry: dismissed: orchestrator routing step, three named items

## Friction

- CLAUDE.md: unclear: the brief says carry_audit lives at `tools/audit/seat/carry_audit.py`, but it is `tools/audit/carry_audit.py`. The dispatch said the toolchain is on PATH, but `python3` here is 3.11 with no `voluptuous`, and `/opt/hpo/venv-ci/bin` is not on PATH. Carry: dismissed: path corrected in place, venv found under /opt/hpo
