Part of #201. Closes no filed issue: roster group R10-STAMP (the wave-1 stamp owes the suspended may-drift restores); the v7.0.1 stamp was refused on it.

`tools/release/stamp.py` deletes every claim at a stamp but restored no suspended may-drift entry. main's claim file carries nineteen suspension notes (R10-SAV-BASELINE, #2255) and 41 R10-PUMP-MODEL claims. Seven of those names already have live entries again. The other twelve (capacity_tariff_15min, cycling_cost, direct_flow_carnot, everything_on, flat_prices, fuse_guard, narrow_band, precip_snow, shoulder, shoulder_two_zone, tariff_plus_two_zone, winter_two_zone_dhw) exist only as notes. The stamp deleted the claims, so its claims self-check (`env_drift.py --claims-only HEAD^1`, the R8-P3 coverage rule) refused with MAY-DRIFT UNCOVERED and threw the commit and tag away. The check was right. The stamp was missing a step.

No commit before the stamp can do the restore:
- At VERSION 7.0.0 the claims are still live, and a name cannot be both claimed and may-drift (CLAIMED AND MAY-DRIFT).
- A branch that moves no fixture may not delete them. Measured: a claims-only branch restoring the twelve and emptying the list gets `RECORD PR CLAIMS ... Restore the files to the baseline's content`, exit 1.
- Rule 1 refuses a stamp tree dirty beyond RELEASE_NOTES.md.

So the restore has to happen in the stamp commit, which is what the R10-STAMP carry names (`tools/release/stamp.py`).

`restore_suspended` undoes the suspension in place. Each two-line note `# (<who> suspends <name>'s may-drift entry ...; restore it,` / `#  verbatim, when the stamp empties the list) <entry>` becomes `# may-drift: <entry>`. The entry's continuation lines stay where the suspension left them. A note whose name already has a live entry is stale, so it is dropped. A note head without its tail, or two notes for one name, raises, and the stamp refuses before writing anything. `rewrite_claims` calls it first, and the stamp plan lists what it restored and dropped. No check is changed or loosened.

## Head

`2a9ca2b23ee750177666f4e6fd6d33c49b80e0bd`, one commit on origin/main `5b9c33d58`.

## Mutation proof

- Replacing `rewrite_claims`' call `text, _, _ = restore_suspended(text)` with `pass` turns three self-test checks red. They are "claims: suspended entries restored, the stale note dropped", "claims: a note after the reason block ends it and keeps its continuation" and "claims: an entry below the claims is restored in place", and the run reads `RESULT stamp_self_test=fail`. tests/entities.py's "tools/release/stamp.py's --self-test passes" turns red with them.
- The same mutant turns the new tests/entities.py check red: "the claim file stamp.py would write from this tree covers every allowed may-drift name". It fails with the same MAY-DRIFT UNCOVERED list of twelve that the v7.0.1 stamp printed. This was measured by running the check's block alone against the mutated file and against origin/main's stamp.py. Both fail, and this head passes.

## Null control

- If the claim file has no suspension note, `restore_suspended` returns the text unchanged. The existing claims self-tests ("may-drift kept", "old reason gone", "may-drift survives without a blank line") are unchanged and pass.
- The card claim file has no notes. The stamp still reports "39 claim(s) deleted" for it, the same count as the refused run.

## Figures

- `python tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass` at the head.
- `PYTHONPATH=tests/hastub python tests/env_drift.py --claims-only origin/main` at the head: `claims hygiene: origin/main ok`. The claim files are byte-identical to the base, so this branch claims nothing.
- Stamp simulation without `--push`: a standalone scratch clone whose origin is a local bare repository. Its main is origin/main plus a no-ff merge of this head, the merge subject uses a placeholder PR number, and the release notes are the stamp seat's v7.0.1 section with that placeholder added. `python tools/release/stamp.py --bump patch --title "<the v7.0.1 title>" --allow-red --allow-rowless`. `--allow-red` and `--allow-rowless` are needed only because the scratch head has no CI run and its placeholder merge has no row. It printed:
  - `tests/golden/claimed_drift.txt: claims-for 7.0.0 -> 7.0.1, 41 claim(s) deleted`
  - `tests/golden/claimed_drift.txt: 12 suspended may-drift entries restored verbatim (...); 7 stale suspension note(s) dropped (...)`
  - `claims self-check: claims hygiene: HEAD^1 ok`
  - `RESULT stamped=v7.0.1 tag_pushed=false`
- Verbatim check on the stamped text: all 19 may-drift entry blocks (first line plus continuation lines) equal v7.0.0's `tests/golden/claimed_drift.txt` line for line. The scratch script compared each block of `git show v7.0.0:tests/golden/claimed_drift.txt` against the stamped file and reported `blocks checked 19 all verbatim`.

## Red checks

none at push. `tests/entities.py` (full run) is CI's at this head. Locally only the new check's block and the stamp self-test were run.

## Forward-carry

- R10-STAMP's carry ("restore the 19 suspended may-drift entries verbatim when the stamp empties the claim list") is discharged by this diff once it merges. The v7.0.1 stamp is then re-run from origin/main as before, with the same RELEASE_NOTES.md. Carry: dismissed: discharged by this diff; the stamp re-run is the orchestrator's next step, not a carry.
- The carry-201 remeasure line says "Before running tools/release/stamp.py over a main whose claim file carries a suspension note, restore every suspended entry verbatim". That step cannot be done by hand: rule 1 refuses a dirty stamp tree, and a pre-stamp branch is refused as above. After this diff the stamp does it itself. Carry: dismissed: superseded by this diff, which makes the stamp do the restore itself.

## Friction

- R8-P3: contradiction: the suspension note promises a restore "when the stamp empties the list", and carry-201 asks the stamping seat to do it before the stamp. No path existed for that: rule 1 refuses a dirty tree, the claims are live at the old VERSION, and RECORD PR CLAIMS refuses a claims-only branch. Fixed here by making the stamp perform it. Carry: dismissed: fixed in this diff.

## Approval

Opened by the hpo-author App. Instrument change under tools/release/ and tests/, not a policy file and no budget raise. Review: adversarial reviewer seat at this head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
