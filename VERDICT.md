Fix review: blocked 5a4b43320394fb57480d835773d02913eb1de4cd class-open: flow_range never reads the row's own default argument, so a row whose default moves off the named constant prints a stale default level at rc 0
bus-nonce: 25a3b3199c59bada37c2f3b35236b658

Round 1 (full scope, no reviewed head). I measured at head 5a4b433203 (code head e395a9f66f) against merge base cb8edb65a5, from detached worktrees at both SHAs.

RESULT finder-harness carry 0: I fed `check_scopes.py --population` into `plant_recall.population`. At the base, all six `tank_volume=` and `house_size=` `min|default|max` print `no population level`. At the head, all six are accepted. Controls at both ends: `layout=no_valve` is accepted, and `layout=moon` and `tank_volume=typical` are refused. At the base `--population` prints `NO-READ AXES: 2`; at the head it prints `NO-READ AXES: 0`, rc 0.
RESULT finder-harness carry 1: I ran `product_reads.py operation --ledger .../operation.tsv --jobs 3`. At the base it prints REFUSE at line 2, rc 2. At the head it reads the ledger, rc 0, `RESULT read=operation universe=532 examined=4 moved=4 reached=2`. The per-row verdicts match the body.
RESULT re-cut control (my own): I wrote a ledger citing the same checks in the states full, partial, both and observe. Every row prints `not witnessed: state differs (recorded duty=control plan=idle ...; duty=control plan=k=none ...)`. So the only states recorded are idle and baseline, and the cut into 12 rows is the read's own record.
RESULT mutation (my own mutants, run on population_self_test): swapping min and max, dropping the const.py fallback, switching off the dict branch, switching off the call branch, not expanding a starred range, and ignoring `field` are all killed (15 to 17 of 19 arms hold). Unmutated: 19/19.
RESULT live plants: moving a range constant, a default constant or a `_number` bound makes the axis UNREADABLE, rc 1 (P1, P2, P5).
RESULT class-open: two plants print a stale level at rc 0 (P3, P4 in evidence/plants.txt).
- P3 changes the default argument of the tank `_F` row (config_flow.py:1827) from `DEFAULT_DHW_TANK_VOLUME` to `300.0`. `--population` still prints `tank_volume 3 default,max,min`, rc 0.
- P4 changes the heated-area default in `_QUESTIONNAIRE_DEFAULTS` (config_flow.py:1249) from `DEFAULT_HEATED_AREA` to `180.0`. `--population` still prints `house_size 3 ...`, rc 0.
The cause is that `flow_range_levels` reads `default` only from the constant the record names. It never checks that this constant is still what the row presents. The body says "a moved flow row never leaves a stale level printed", and 0018's new sentence says "a row that moves makes the command refuse, never print a stale level". Neither holds for a row's default. Two ways to resolve it:
- Read the row's default where the row carries one, as the `_F` third argument or the key's value in a defaults dict, and refuse when it does not name the record's `default` constant. The heat-loss row presents `_SUGGESTED`, so it needs a recorded exception.
- Or disposition the gap in the body and narrow the 0018 sentence to bounds and default constants.
RESULT claims/version: the diff touches no golden, claim file, VERSION, manifest or notes heading.
RESULT merge-tree: `git merge-tree --write-tree origin/main HEAD` rc 0.
RESULT head: the PR head is still 5a4b43320394fb57480d835773d02913eb1de4cd, and the body names it.
RESULT checks: no red at the head when read. mutation, closure-scope, policy-docs, instrument-self-tests and the gate were still pending.

Note: harness: the finding has no committed harness file. The finder's instruments are the ones each carry names: `plant_recall.population` over `--population`, and `product_reads.py operation --ledger`. I ran both at both ends. The re-cut control ledger and the mutant driver are mine (evidence/).
Note: policy: the one 0018 sentence changes what a seat must do. Tank volume and house size stop being NO-READ, which owes no card. Their six levels join the population cells the term counts, so planters and finders now cover them. It needs the owner's approving review, or one under the mandate. As written, it also over-claims (P3/P4 above).
