Fix review: merge 87e5c30f7c30f9d52381a8e19d341c2bdddc8f65

bus-nonce: 7956f76de68eebb94364201b34297869

## Findings

- The ruling's sample is not reproducible from the verdict refs as they stand: #2955's ref tip (`077584681`, merge of 502b0df) no longer holds item `158ad202` ("NOT one of the required contexts on main-protect and does not block a merge"). It sits in the superseded merge verdict `885d4751` of the same ref's history. The fixer of the carry must build the #2955 fixture from that commit's VERDICT.md, not the tip. Carry: R10-FLY-CARRY-DISPOSITION
- A flagged item the ruling does not list: #2955's current verdict, item `2471d3e6` ("None. The merge resolution is a pure union; nothing is deferred or owed."), is flagged `non-blocking` outside `## Evidence`; a statement that nothing is owed is read as a deferral. Null-control candidate for the carry's classifier work. Carry: R10-FLY-CARRY-DISPOSITION

## Evidence

- RESULT diff: two files only, `dev/programme/triage/s6-batch64.md` (new) and `dev/programme/delivery/2980.md` (new, one `open` row for #2980 in the same shape as #2974's); no code, VERSION, manifest, notes or claim file touched.
- RESULT sample: re-ran `carry_audit.items(text, True)` (module at head, identical to the base for this file's purpose) over the 30 highest-numbered `verdict/<pr>` refs opening `Fix review: merge`, #2936 to #2974 (ev/flagged.txt). 9 flagged, matching the ruling's 9. 6 are in `## Evidence`, not 7: #2937 19d896fa, #2939 3c055bc1 and f76b3ac3, #2959 dde38e84 and 50a530e7, #2969 c21695db all re-derive and are measurements. The seventh (#2955 158ad202) is the superseded text above. The other 3 flagged are non-blocking items (#2947, #2955, #2971), which the ruling counts as 2. Class counts A 4 / B 2 / C 1 stand if 158ad202 is taken from `885d475`; I did not re-derive that item from the tip.
- RESULT null control: the ruling names four controls that must stay findings (#2465 row, deferral row, new "not this pull request's" row, `minor` drift outside the span) and puts them in the carry, not in this PR; nothing to run here. The rejected arm is justified by the two self-test rows it names.
- RESULT destination: `R10-FLY-CARRY-DISPOSITION` is in `dev/programme/rosters/wave-r10-groups.json` at origin/main, stage `not-started`, and its brief names `carry_audit.py`'s classifier. The carry text is in the ruling for `roster_edit.py` to cite; this PR does not edit the roster (the contract forbids it).
- RESULT carry_audit: the packet prints `CARRY-AUDIT: 0 finding item(s)` and `FIGURES: 0 refused` at the head.
- RESULT merge: `git merge-tree --write-tree origin/main 87e5c30f7c30f9d52381a8e19d341c2bdddc8f65` exits 0 (ev/merge-tree.txt). Roles directory unchanged on main since the merge base.
- RESULT CI: check-runs API on the head shows no failed run; success on mutation, closure-scope, delivery-status, nightly-status, budget-raise-gate, briefs, hassfest, wave-script and CodeQL. Still in progress when read: tests fast/closures/coverage/typing/browser/arch-instrument, governance policy-docs/env-matrix/instrument-self-tests, arch-score. Not re-run (cite CI's heavy runs).
- RESULT cost claim: the ruling states `carry_audit.py` has no `--budgets` row; not re-derived by me.
