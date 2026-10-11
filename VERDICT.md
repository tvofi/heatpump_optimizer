Fix review: merge c565a0d5595b98eb862b1e43d1c930439f9d1fe1

bus-nonce: 42e67513f5d9767c9a05e7618baaf6bd

Round 2 -- the resolution delta only (round-1 blocked verdict's measurements stand and are re-confirmed below where the delta could move them).
RESULT repair: 156fe40a1 touches only tools/audit/seat/a1_dispatch_arms.sh; the fixture repo now builds through tests/throwaway_git.sh (throwaway_git_init/clone under throwaway_git_env). Measured: throwaway_git.py --self-test 44/44; --check "0 raw git init or clone site(s) refused", exit 0. The two refused sites are gone; nothing else changed.
RESULT arms: a1_dispatch_arms.sh re-run at the head -- output BYTE-IDENTICAL to my round-1 run (diff empty): inert-only=skip, closure-touching=scoped, diff-underivable=full; base arm unchanged.
RESULT round-1 figures stand: all six gate files (closure.py, derive_closures.sh, a1_dispatch_arms.sh, entities.py, prepr.sh, tests.yml) byte-identical between effd8a95f (measured) and c565a0d55 (published head); the further delta to c565a0d55 is main's own #2121 content plus merge/row commits. closures/inert_reads tables byte-identical to round-1 (only two recorded-seconds refreshes from main's re-record); all nine (a2) boundary probes re-run and unchanged; (e) recording set (34 rec targets) and lane layout untouched; entities.py ALL 2260 PASSED at the head.
RESULT red checks: instrument-self-tests completed SUCCESS at c565a0d55 (check-runs API), pr-contract SUCCESS -- the body names and answers both round-1 reds. mutation, typing, policy-docs, briefs, delivery-status, budget-raise-gate, closure-scope: success. closures/coverage/fast/browser still in progress at review time: the branch's own gate, which merge_train waits on; the closures full arm is itself the (e) wall acceptance instrument (<= 35 min, two runs, orchestrator observes).
RESULT rule 1: unchanged from round 1 -- (e) is scheduling only (recording set proven identical), (a2) only moves skip->scoped with both bound edges pinned, (a1) scopes only the dispatch arm and fails closed; main-push and nightly full arms untouched by all three plus this repair.
RESULT head: measured and published at c565a0d5595b98eb862b1e43d1c930439f9d1fe1 = branch head at push time.

Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2129/ev/ (round2-summary.md names the head; round-1 files carry the rest).
