Fix review: blocked 8cf976936e013314c513ecf4bb283b7c88f63d8b mutation-vacuous: quoted_lookbehind_alone, quoted_lookahead_alone, mdlink_url_any survive on added carry_audit.py lines

bus-nonce: 8a69e49b99d510bf91791a7b3a946ef1

This is round 4, the delta review from the reviewed head 686b06f80ac7661a1d7cc84b67ac7c156566ed6d. A further blocked review means `fixer.md` owes a re-cut. Every item of the 686b06f8 verdict is resolved at this head (see Evidence). Splitting the prior driver's compound mutant, and mutating the delta's own new lines, leaves three survivors.

## Block

I ran the mutants with the reviewer's harness at this head: `ev/mutant_driver_head.py`, which is the prior `ev/mutant_driver.py` with its anchors re-spelled for the edited lines, plus mutants on the delta's added lines. Survivors, in one block (`ev/mutants_head_driver_head.txt`):

```
quoted_lookbehind_alone  QUOTED_PHRASE (?<![\w"])"[^"\n]*"(?!\w)  ->  "[^"\n]*"(?!\w)       444 checks, 0 failed
quoted_lookahead_alone   QUOTED_PHRASE (?<![\w"])"[^"\n]*"(?!\w)  ->  (?<![\w"])"[^"\n]*"   444 checks, 0 failed
mdlink_url_any           MD_LINK \]\([^)\s]*\)                     ->  \]\([^)]*\)            444 checks, 0 failed
```

(`para_bullet_readded` also survives. It is an equivalence probe that adds back the clause the fixer deleted, and its survival confirms body item 3. It is not a survivor.)

- The body's item 5 says `quoted_lookbehind` is killed, and it is for the prior driver's spelling. That spelling removed both lookarounds at once (`ev/mutants_prior_driver_head.txt`). The single pin, `5" pipe ... "y"`, is killed by the lookahead alone. So each of the two conditions survives when it is removed by itself, against the body's "one pin per added shape-guard condition". Each survivor has a distinguishing input that the head classifies differently (`ev/survivor_probes.txt`):
  - lookbehind: `x. the 5" pipe. Carry: R10-LIVE and 6" too.` At the head the marker routes. Under the mutant it is swallowed, a silent fail-open.
  - lookahead: `x. said "q. Carry: R10-LIVE "x" too.` At the head it routes. Under the mutant it is swallowed.
- `mdlink_url_any`, on the new `MD_LINK` line: `x. Carry: [#100](a b)` gives no segment at the head (fail-open under `## Evidence`). Under the mutant it gives one marker. The `[^)\s]` exclusion decides real input and nothing pins which way it should go.

Each survivor needs either a killing check or an `## Unpinned sites` disposition (fixer.md step 2). The body's `## Unpinned sites` dispositions only `_self_test` deletions.

## Evidence

- RESULT head reviewed: 8cf976936e013314c513ecf4bb283b7c88f63d8b (`ev/HEAD.txt`). It is still the tip of `fix/r10-carry-audit-p5` at 10:43Z. It matches the body's `## Head`, which merges the authored head 45ae9ae729.
- Prior item 2, the five survivors. All are resolved at this head (`ev/mutants_prior_driver_head.txt` and `ev/mutants_head_driver_head.txt`). At the base, the same driver reproduces the prior verdict's five survivors exactly (`ev/mutants_prior_driver_base.txt`, 434 checks).
  - `kindsec_noNote`: KILLED by the `## Open residuals` check.
  - `para_nobullet`: its clause is deleted. Adding it back survives, so the clause was equivalent, as body item 3 says.
  - `para_nocarry`: KILLED.
  - `quoted_lookbehind` (the compound spelling): KILLED.
  - `marker_brief`: KILLED.
  - `marker_issue` and `marker_true` now apply, with unique anchors, and are KILLED.
- Prior item 3, the spelling corpus: present. The check `carry 3 corpus` asserts 104 marker spellings (13 × 8) and 8 mention spellings, and passes at the head. It is the check that kills `marker_dismissed`, `marker_issue`, `marker_brief`, `blank_off` and `mdlink_shaped`. P1 and P2 are each pinned by their own check. `blank_off`, `blank_shrink`, `mdlink_shaped` and `mdlink_dests` are all KILLED.
- Prior body-figure item: `## Figures` now says 178. RESULT `bus.sh --self-test` at the head gives 178 checks, 0 failed (`ev/bus_selftest_head.txt`). It re-derives.
- RESULT `carry_audit.py --self-test` at the head gives 444 checks, 0 failed (`ev/carry_selftest_head.txt`). It re-derives.
- RESULT bus.sh mutant `&& echo x` removed: 178 checks, 1 failed, `CARRY-LANDED-SENTINEL` (`ev/bus_mut_sentinel.txt`). It matches the body.
- Not re-derived: the body's `mutant_run.py` figure of "54 mutants drawn" at the pre-fix head. I did not re-run it, and it does not change this verdict.
- Delta (`git diff 686b06f8 8cf97693`): it touches `tools/audit/carry_audit.py` and `tools/audit/seat/bus.sh` only, an instrument and its self-test. None of it is in `custom_components/`, so nothing widens the scope.
- Merge: `git merge-tree --write-tree origin/main 8cf97693` exits 0 against origin/main fc2a7edcf2be (`ev/merge_tree.txt`).
- Versions: VERSION, the manifest and RELEASE_NOTES.md are untouched. There are no golden or claim files in the delta.
- CI: `merge_train.py classify 8cf97693 --pr 3493` returned WAIT twice (`pending: gate red: none`, `ev/classify.txt`). The packet refusal `introduced-red` was unreadable because instrument-self-tests was still queued. CI was not waited out, because the block does not depend on it.
- Role drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` changes fix-review.md. I read the current text through role_pack, and it does not change this verdict.
