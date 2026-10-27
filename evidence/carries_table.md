# The 22 roster carries of R10-FLOW-JIDOKA against the body of #2853 at fa18c13d206e312e2fe959d825ffa04ed77025e3

| carry | body disposition | verified |
|---|---|---|
| 1 | context: "these five are its cheapest stops; the rest are routed below" | yes: every other carry is itemised (rows below) |
| 2 | (a) per-file ids prepr-1..prepr-10 in a block beside the tools/pr/ mutants; (b) no new git repo; (c) no push site; (d) Red checks names nightly-status | yes: harness diff places the block after merge_main_bot-1, before stamp-1; throwaway_git --check 0 refused; ref_privacy --check 26 push-site files, 0 refused; Red checks has the nightly-status line |
| 3 | moved to R10-FLY-CARRY-DISPOSITION by revision 15 | yes (the carry's own text says so) |
| 4 | not built; Forward-carry, Carry: R10-FLOW-JIDOKA | yes, routed |
| 5 | built, step 3f7 (with 19) | yes: privacy_line runs ref_privacy --check; carry19_instances.txt |
| 6 | "honoured, with the budget above" | NO: budget restated 5 s/10 s -> 8 s/15 s after 6g measured over 5 s; --fill-red's wall time unstated (## Block) |
| 7 | not built; Forward-carry (base-pinned replay) | yes, routed |
| 8 | built, figure lint in --body-check | yes: carry8.txt (control, mutant, null) |
| 9 | not built; Forward-carry (base-pinned replay) | yes, routed |
| 10 | not built; Forward-carry (stale S36) | yes, routed |
| 11 | not built; Forward-carry (--body-check parity) | yes, routed |
| 12 | not built; Forward-carry (--body-check parity) | yes, routed |
| 13 | not built; Forward-carry (quiet output) | yes, routed |
| 14 | not built; Forward-carry (--body-check parity, one grammar owner) | yes, routed |
| 15 | partly answered (3f7); rest Forward-carry | yes, routed |
| 16 | not built; Forward-carry (base-pinned replay, field_coverage registry) | yes, routed |
| 17 | built, --fill-red | yes: carry17.txt (control, null, idempotence, mutant) |
| 18 | built, WAVE_INPUTS | yes: carry18.txt (#2736 instance, null, mutant) |
| 19 | built, step 3f7 and --body-check | yes: carry19_instances.txt, carry19_mutant.txt |
| 20 | built, step 6g | yes on behaviour: carry20_instance.txt (#2609 ff83a3d7 refuses, merged head passes, mutant passes); over budget (## Block); trigger narrower than claims.py's inputs (## Findings) |
| 21 | partly answered (6g); rest Forward-carry | yes, routed |
| 22 | not taken (policy_lint --stats HTTP 500 on the seat); Forward-carry | yes, routed |

`python3 -I tools/audit/carry_audit.py pr 2853`: `7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)` (carry_audit.txt).
