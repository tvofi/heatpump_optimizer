Fix review: merge 18656e4c23a664ca9c58de75f3c5589078631a1c

bus-nonce: d0a8b645d24fb23761cfdb9176390c09

Round 1. Measured head 18656e4c23a664ca9c58de75f3c5589078631a1c. Docs-and-detector PR (RCA record, bugclasses entry, schema/enum registration, read-only detector); no production code under custom_components or tools.

## Findings

- Follow-up: the RCA's countermeasures (freeze premise check via merge-tree, wall bound on relay handoff updates, lag level on the board) are proposals only and unbuilt; the class entry records status detector, barrier null, to be decided on a fourth instance. Carry: dismissed: owned by the RCA record itself (class N-relay-handoff-starvation, reopen rule in bugclasses.json non_round_note)
- Residual: the body's lag table (10 carried, 4 uncarried, 9 late) is a sliding window and I could not re-derive it; at this head the same command prints late=29 over its window. The body already says re-run, do not carry. Carry: dismissed: sliding-window figure, body discloses it
- Residual: #3299 and #3310 20-60 min lags and the relay logs are the orchestrator's record, not re-derivable from refs (body discloses). Carry: dismissed: disclosed unverifiable, not asserted as measured

## Evidence

- Head: PR live head is now c2259f9fecc15e02ad1908bbc0499b74aa07e165 (one "ci: merge main" commit). review_carry.py 18656e4c23a664ca9c58de75f3c5589078631a1c c2259f9fe prints CARRY (0 of 1 branch-only commits non-merge), so this verdict carries.
- CI: merge_train.py classify 18656e4c23a664ca9c58de75f3c5589078631a1c --pr 3352 exit 0: GREEN pending: none red: none. Body's red gate/pr-contract at fae447091 were from a cancelled run-id group; answered in the body (cause: livehead cancel, no cheaper detector); both green at this head.
- Merge: git merge-tree --write-tree origin/main 18656e4c23a664ca9c58de75f3c5589078631a1c rc 0; only MERGE stderr is LEDGER-MERGE: resolved dev/audit/config/bugclasses.json.
- VERSION, manifest, RELEASE_NOTES untouched (0 matching paths in three-dot diff). No golden, claim, budget, closures or INERT file touched.
- Mutation/null control: --self-test passes (fast=2m, slow=40m, never=uncarried). Mutant: flipped lag subtraction to addition in relay_handoff_lag.py; self-test fails with AssertionError (fast 68.7, slow 106.7). Restored; passes.
- carry_audit at head: 0 finding items, 0 unrouted.
- Class enumeration: new class id present in bugclasses.json, finding.schema.json and audit-find.js CLASS_GUESS; CI agreement/wave-script green.
- Body forward-carry: none claimed; the RCA changes no later stage's brief, countermeasures are proposals.
