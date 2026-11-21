Fix review: merge 6e37c4c3362ffb65f4e9b26631252c766bb733ea

bus-nonce: 413d7a1bce312fff5a660552c6e71bfe
pending-ci: gate

## Scope

This is round 3. Round 2 returned `Fix review: merge accff49d515c169ff2139c5c4191c1bb1e6da5ce` on ref `probe/rev-3812-5267b74a`. `review_carry.py accff49d51 6e37c4c336` prints `FRESH-REVIEW`, because 6f0df6dedf is not the automatic merge of its parents. So this round reviews the delta (fix-review.md step 12). The delta has three parts:

- fca20a5f5d, the `github-actions[bot]` pin of `off_restore.py:_captured RETURN_DEL ea057c8a`, killed by `tests/features.py`.
- 6f0df6dedf, a merge of origin/main 6fdc15354f. Its one production resolution is in `pump_arbiter.ArbiterInputs`, and it keeps both trailing defaulted fields: this branch's `entry`, then main's `draw`. `git show --remerge-diff` prints only the removal of the conflict markers (`ev/resolution_6f0df6dedf.diff`).
- 6e37c4c336, a clean merge of origin/main 4ebd430fbf.

Apart from that one pin file, the PR's own diff (three-dot from each merge base) differs between the two heads only in the resolved hunk and in the `structure_budgets.json` base values. The recorded drops are unchanged: `class_excess_loc` falls by 16 and `max_class_loc` by 24 at both heads.

No production delta widens the review. The single production call site `coordinator.py:4154` builds `ArbiterInputs` by keyword (`entry=self.entry`, `draw=self._accuracy.draw`), so the order of the two defaulted fields cannot misbind.

`git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. Everything below was taken from a detached worktree at the head `6e37c4c3362ffb65f4e9b26631252c766bb733ea`, against merge base and origin/main tip `4ebd430fbff9a7b19582ca530a817f34abbafa16`.

## Evidence

- Feature blocks at the head, with round 2's commands and preludes (`ev/preA.py`, `ev/preB.py`):
  - The `R11-SEAM-actuation-release` section reads `ALL 77 FEATURES BLOCK PASSED`.
  - Block B reads `ALL 55`.
  - Block A reads `ALL 37`. The 31 to 37 change is main's merge into that range: check-call lines in the range count 31 at accff49d51 and 37 at the head. Files: `ev/section.head.out`, `ev/blockA.head.out`, `ev/blockB.head.out`.
- Mutation proof, re-run at the head with round 2's driver and mutants (`ev/mutrun.sh`, `ev/mutants.py`; results in `ev/mutants.summary.txt`, per-block logs `ev/m*.{section,blockA,blockB}`):
  - R2-M1 to R2-M5: all KILLED.
  - REV-A to REV-D: all KILLED.
  - REV-E: SURVIVED, as in round 2. It is the reviewer's own additive mutant, not a deletion of a line the PR names; see Findings.
- Re-anchored unpinned sites. The four lines the body moves (`coordinator.py:7764`, `pump_arbiter.py:1833`, `2271`, `2281`) read the same text as the code head df92ad2b55's lines 7777, 1759, 2194 and 2204 (`ev/reanchored_sites.txt`).
- Ratchets at the head: `tests/structure.py` reads `STRUCTURE RATCHET PASSED`, and `tests/comment_ratchet.py` reads `long_units_base=2301 long_units_head=2301` and `comment_ratchet: OK` (`ev/structure.out`, `ev/comment_ratchet.out`).
- Step 13: `git merge-tree --write-tree origin/main 6e37c4c336` exits 0 at origin/main 4ebd430fbf (`ev/merge_tree.out`).
- Step 7: the body's `## Head` names `6e37c4c3362ffb65f4e9b26631252c766bb733ea`, which is the head I measured.
- Steps 2 to 6: not re-run this round. The finder's harnesses, the class enumerations and the golden and version checks were verified at accff49d51 in round 2. The delta touches none of their inputs beyond the keyword-safe field resolution.
- Owed reds: `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing` and `validate / validate-hacs` (`ev/owed_reds.txt`). The live classify line below shows no red at this head.
- CI: `merge_train.py classify 6e37c4c3362ffb65f4e9b26631252c766bb733ea --pr 3812` was polled about every 75 s (`ev/classify.log`, last line in `ev/classify.last`). The result is under `## CI`.

## CI

Polled from 23:25 to 23:55 UTC. Every run exited 3 (WAIT); the last read `WAIT 6e37c4c3362ffb65f4e9b26631252c766bb733ea pending: gate red: none`. No red at this head, and the head did not move during the review. The relay posts this verdict once CI is green at this head.

## Findings

- Note: carry-missing: the body's three Forward-carry items (to R11-SEAM-actuation-writes twice, and to R11-SEAM-kernel-step) are routed in the body only. They were noted in round 2 and are unchanged at this head. Carry: dismissed: the body routes all three to the orchestrator, who writes them onto those groups' briefs; landing them is the orchestrator's, not a code defect
- Note: departures: the four departures the body lists are unchanged since the round-1 head and are outside this delta (step 12). Each stays pending owner confirmation. Carry: dismissed: recorded in the body as pending owner confirmation; the owner's approving review at merge decides it
- Residual: surviving reviewer mutant REV-E. It adds a `restored(...)` call when an empty entry is dropped, which empties the owner's record. It survives all three blocks at this head (77/37/55), as in round 2. Its only effect is one resend of an unchanged target after On. Carry: dismissed: no check pins whether an empty drop leaves the owner's record, and either behaviour leaves the entity correct
