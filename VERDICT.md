Fix review: blocked 90788b1e5ea8ce015e7ae6c432d308d7a5aab476 harness: class-open the NOT_REQUIRED carve-out frees every NONBLOCK word in its sentence, so a nit or defect sharing a sentence with "not a required check" passes under ## Evidence

bus-nonce: 4754a76a2b269a20cfbe6c86d9b4e3a8

Round 1 of review for this head. Measured head: 90788b1e5ea8ce015e7ae6c432d308d7a5aab476 (ev/HEAD.txt), still the branch tip when this verdict was written (git ls-remote). Merge base with origin/main: 5d433771a; body's figures name 289426c1f, an ancestor of 5d433771a, and I measured the base end there.

## Block

- **The carve-out is wider than the body's account of it.** The body says the NOT_REQUIRED sentence states "a check's state, not a note" and that this carve-out "is the whole relaxation". The body also refused a NONBLOCK exemption under `## Evidence` because it freed #2441's nit and #2465's defect, and called that smuggling. But `items()` drops every sentence that matches NOT_REQUIRED before it reads NONBLOCK (`claims = " ".join(x for x in SENTENCE.split(t) if not NOT_REQUIRED.search(x))`). So the same two shapes pass when they share that sentence.
- **The attack.** `ev/class_attack.py` was run at the head and at 289426c1f (output in `ev/class_attack.txt`, verbatim sentences there). Each case is one bullet under `## Evidence` in a merge verdict, and each puts a NONBLOCK word in the same sentence as "not a required check":
  - case `same-sentence nit`: #2441's nit;
  - the second case in that file: a defect given a low-severity word;
  - case `parenthetical`: #2465's 0.27 K defect with "(not a required check)" inserted.

  Each reads as no finding at the head and as a finding at the base. Controls: under `## Notes` the same text is a finding at both ends. With a `;` or `.` between the check clause and the nit, the head flags it too, as the PR's self-test row claims.
- **The path is realistic.** The new prompt tells every reviewer that a check is evidence only "in a sentence saying it is not a required check". That makes the sentence the exempt unit. The pre-flight fails closed everywhere else, so this is the one fail-open path the diff adds.
- **Proposed fix, a few lines.** Narrow the carve-out from the whole sentence to the check's own clause. Two ways:
  - strip only the NOT_REQUIRED match and an adjoining block-state clause, then read NONBLOCK over the rest of the sentence; or
  - exempt a NOT_REQUIRED sentence only when every NONBLOCK hit in it is a block-state phrase.

  Either way, the nit and severity wording still flags. Add the three attack sentences as self-test rows, which fail on this head. The #2544 aeeb9432 sentence about composed-proof must still read as no finding.

## Findings

none

## Evidence

- **Role file current:** `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- **Mutation proof (step 1), re-run by me:**
  - M-A, the `elif verdict and EVIDENCE_HEADING.match(sec):` arm deleted (4 lines): `carry_audit self-test: 182 checks, 30 failed`, with the failing rows the body names. The replay under M-A prints v2544_reshaped=1, v2544_planted=2. See ev/mutation_MA.txt.
  - M-B, the new prompt sentences deleted: `cloud_dispatch self-test: 31 checks, 1 failed` (the "separate findings ... from evidence" check). See ev/mutation_MB.txt.
  - Unmutated head: 182/0 and 31/0.
- **Per-site mutants:** `r10_carry_parser_mutants.py` head `RESULT sites=168 unmapped=0 mutants=224 survived=0`; at 289426c1f `RESULT sites=152 unmapped=0 mutants=190 survived=0`. These match the body (ev/mutants_*.txt). The harness has no mutant that widens the carve-out's scope beyond the check clause, so it cannot see the block above.
- **Finder's instrument at both ends (step 2).** The group R10-VERDICT-ITEM-BARRIER is not in `dev/programme/rosters/wave-r10-groups.json` at origin/handoff/audit-r10-roster 2c76c3128 (`git log --all -S VERDICT-ITEM-BARRIER` finds nothing), so no roster brief names a harness. I used the instrument that parked the verdicts, `carry_audit.py pr N`. Head and 289426c1f print the same line for each PR:
  - #2513: `2 finding item(s): 2 routed, 0 unrouted`;
  - #2544: `1 finding item(s): 1 routed, 0 unrouted`;
  - #2547: `1 finding item(s): 0 routed, 1 unrouted`.

  So it reads flat. The body's figure "1 finding item(s): 0 routed, 1 unrouted" for each no longer reproduces for #2513 and #2544, because the live comment threads moved since the body was written (ev/finder_carry_audit_pr.txt).
- **Companion (the fixer's replay harness, disclosed as the fixer's):** `r10_verdict_item_barrier.py --fetch` at the head prints `fetch_*=identical` and the body's table exactly: verbatim 1/1/1, evidence 1/1/1, reshaped 0/0/0, planted 1/1/1. Run against 289426c1f's `carry_audit.py`, it gives reshaped 0/1/0 and planted 1/2/1, matching the body (ev/replay_*.txt).
- **Sweep, both ends:** my own 83-PR corpus (the last 80 merged PRs by update time over REST, plus 2513, 2544, 2547 and 2556, de-duplicated; ev/sweep_corpus_prs.txt). Head and base both print `CARRY-AUDIT: 124 finding item(s): 83 routed, 38 unrouted, 3 bad destination(s)`, and the UNROUTED/BAD-DEST line sets are identical. The body's 131/85/42/4 over 84 PRs is not re-derived: the corpus is live and moved. The claim that this sweep reads identically at both ends holds.
- **What-if:** on the same corpus, base `whatif_flagged=17` and head `whatif_flagged=33` (body: 18 and 32, on a different corpus). The only id flagged at the base and not at the head is #2544 aeeb9432, as the body says (ev/whatif_*.txt).
- **Null control:** v*_planted=1 at the head for all three verdicts, confirmed.
- **Generator, merge, and cheap checks:**
  - The generator renders the new sections; covered by the M-B row.
  - `git merge-tree --write-tree origin/main 90788b1e5ea8ce015e7ae6c432d308d7a5aab476` exits 0, tree b980d7a52 (ev/merge_tree.txt).
  - VERSION, the manifest, RELEASE_NOTES and the claim files are untouched.
  - `tests/structure.py`: STRUCTURE RATCHET PASSED. `tmp_paths.py --check`: 0 refused. `archscore --diff 5d433771a`: dS +0.0000 NULL.
  - The new harness is classified in tests/closures.json, the only closures move.
- **Head (step 7):** the body names 90788b1e5ea8ce015e7ae6c432d308d7a5aab476 as the head, and it is the head I measured.
- **Forward-carry (step 10):** both items carry `Carry: dismissed: <reason>` in the body. No roster carry is claimed.
- **CI on this head, read once from the check-runs API (ev/check_runs.tsv):**
  - Concluded green: pr-contract (twice, the second started 14:20:44Z), hassfest, budget-raise-gate (first run), validate-hacs, arch-score, mutation, scope, closure-scope, briefs, delivery-status, policy-docs.
  - Still queued or running when read: fast (3.14), env-matrix, wave-script, typing, instrument-self-tests, browser, coverage, budget-raise-gate (second run), and the Analyze jobs. I judged on the rest.
  - `nightly-status` concluded red. It grades main's scheduled runs, and this diff (tools/audit, a harness, a delivery row, closures.json) does not reach what it reads.
  - Step 11 is not judged: workflows on this head have not all concluded, and this verdict blocks on step 6.
