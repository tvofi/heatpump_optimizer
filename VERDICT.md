Fix review: blocked 32c768ae03ddbed07c5f4975f458930a1054e35e root-cause-detectable: pr-contract / pr-contract refuses the body's stale scope-line figure block, and gate is red on it alone; figure_block.py verify shows it locally in seconds

bus-nonce: 76f4ef9ed9970c3189dd63618b7c3934

## Block

- The required check `pr-contract / pr-contract` concluded failure at this head on both runs, job 132550761259 and job 132553014911. The required `gate` (job 132553332629) fails only on it (`FAIL pr-contract / pr-contract: failure (this run)`). `merge_train.py classify 32c768ae… --pr 3532` reads `RED … pending: none red: gate` (rc=1, 19:03:05Z). Both contexts are in the `owed-reds` set. The body's `## Red checks` names neither (it answers only `tests / fast (3.14)` and `tests / mutation`).
- The cause is in the body, not the code. The `## Figures` block `<!-- figure-block: scope-line mb=9fdba3b8… head=32c768ae… -->` holds `MODE: FULL -- every test script runs, nothing is scoped out.`. At this head over that merge base, the registered instrument prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` I reproduced the refusal locally with `python3 -I tools/pr/figure_block.py verify <block> --base 9fdba3b8… --head 32c768ae…` (`1 refused`, ev/figure-block-verify.txt). `figure_block.py refresh` renders the SCOPED line (ev/body-figure-block-refreshed.md).
- A cheaper detector exists: `figure_block.py verify`, run on the body before it is set, costs about 1 s and is the same command CI runs. The body says the orchestrator's script set it without a push. Remedy: refresh the block (`figure_block.py refresh <body>`) and let `pr-contract` re-run. If that red recurs, answer it under `## Red checks`. No code change is owed: the resolution reviewed below is sound.

## Evidence

- Round: a later round (delta scope) over the reviewed head 3ab3d5b5ab (verdict `Fix review: merge 3ab3d5b5ab…`, nonce 6200efa5…). The delta has two merges. 5d630d46bd merges handoff 5e1fac78ad, which is 3ab3d5b5ab plus origin/main 237fad4453. 32c768ae03 then merges origin/main 9fdba3b854.
- Resolution: `git show --remerge-diff` (ev/remerge-*.txt). 5e1fac78ad resolves exactly one key, `options.step.entities.sections.indoor.data_description.space_setpoint_unit`, in strings.json and translations/en, de and sv, each to the 237fad44 (main) side. tests/closures.json was resolved by the LEDGER-MERGE driver, with no marker left. 5d630d46bd and 32c768ae03 have empty remerge diffs, so both merged clean.
- Four files equal main: the blob of each of the four files at the head equals its blob at 237fad4453 and at 9fdba3b854 (ev/four-files.txt). Each file has 1509 leaf keys (ev/key-counts.txt), and strings.json and en.json are the same blob (1dd5049033). This re-derives the body's "1509 keys each" and "strings.json equals en.json".
- Nothing else of the patch changed: the head tree equals `git merge-tree --write-tree 3ab3d5b5ab 9fdba3b854` except in those four files. The only differences there are the 4 marker and losing-side lines per file, 16 deletions in all (ev/tree-oracle.txt). Files that left the three-dot patch (patch-R.diff against patch-H.diff) are the train PRs' content, now on main. The `_share.RETURN_DEL.3eede229` ledger deletion is in both patches.
- No production delta widens scope: the only `custom_components/` change beyond main's own is the four string files, taken from main verbatim.
- VERSION, the manifest version and the notes heading are untouched in `git diff $(merge-base)...HEAD` (CI's version-edit step agrees: "no version edit").
- Merge with main: `git merge-tree --write-tree origin/main 32c768ae…` returned rc=0 at origin/main 5b8f05ba4e (ev/merge-tree.txt).
- CI: ev/classify.log. The poll read WAIT (pending gate) at 19:00:57Z and 19:02:01Z, then RED (red: gate) at 19:03:05Z. Other required contexts are green. `tests / nightly-status` is red but is not in the owed set.
- Previous finding (body duplicated sections): resolved. `## Mutation proof` through `## Unpinned sites` now each appear once.
- carry_audit check: rc 0 over this verdict (ev/carry-audit.txt). The PR body there is a stand-in holding its Forward-carry and Friction "none"; CI's pr-contract run of carry_audit over the live body printed 0 finding items.
- Head re-read before return: refs/heads/fix/r10-duty-switch-restart-learning-pr-b-p2 = 32c768ae03ddbed07c5f4975f458930a1054e35e (ev/head-reread.txt).

## Findings

- The `## Head` section repeats its first paragraph word for word ("`32c768ae…` is this PR's head, unchanged: … main merged cleanly …"). That holds for the last merge of main (9fdba3b8), but 5e1fac78 did conflict, which the next paragraph states. This is a body-text defect from the orchestrator's body script, with no code effect. Carry: dismissed: body text owned by the orchestrator's body script, fixed by the same body refresh the block requires; no code effect
