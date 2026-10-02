Fix review: merge 7231ed14a7e6a640b865dad2b3b48fc45f89c668

Head 7231ed14 (handoff/r9-proc-4), body 7a71cab7. Merge base is d536fb4d. This round judges the delta from ec166685.

FIX (c9fedbd1)
- The dedupe now keys on "<pr> <tree>", which is exactly what the signature covers. signed_by_approver also refuses a signature line that does not re-encode to itself.
- Round 2's exact replay is refused: replay_exact_7231ed14.txt shows "already posted (a replay)".
- Round 3's padding variant is refused: replay_malleable_7231ed14.txt shows "BUS unsigned". Either check alone would stop it.
- Both probes posted the stale merge at ec166685 (round 3 evidence), so this is the red-to-green proof.
- bus.sh --self-test passes 45 of 45 here. The new cases cover the "=" and trailing-space re-encodings.
- Legitimate later rounds still post: each dispatch mints a fresh nonce, so each round's VERDICT.md and tree differ. The probe's round 2 posted.

MERGE (b58bf00b)
The merged tree equals `git merge-tree --write-tree c9fedbd1 d536fb4d` (04468757). It is a clean automatic merge with no hand resolution. Against d536fb4d, the PR's diff is still the same six files.

TRIM (7231ed14)
This is a one-line rewording of orchestrator.md's identity bullet. No rule was dropped: confirm-only posting, the key held on the orchestrator's machine, and code-owned paths needing tvofi are all still stated. policy_lint reports 0 errors across 40 files. No *_budgets.json changed, so there is no raise.
Nit, not blocking: "its writes can vanish retroactively" became "its writes vanish retroactively", which is slightly stronger than the evidence. Fix it on any later touch.

STANDING FROM EARLIER ROUNDS
Authorship needs hpo-approver's key on the orchestrator's machine. Cross-PR replay and tampering are refused. The bus approves nothing, so code-owned PRs still need tvofi's approving review. The three passages cut in round 1 are restored. The 0011 citation is pinned by policy_lint.
Residual, by design: the replay record lives in $HPO_BUS_STATE on the Mac. If that directory is wiped, an old signed tree could post once more.

Not run here: entities.py and the full gate. CI on 7231ed14 is the authority, and the Mac reports it. This merge verdict stands on that CI being green.
