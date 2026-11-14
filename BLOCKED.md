# BLOCKED: r10-sav-valuation-residue-p4 (Carry 9)

Question: body_push.sh refuses the handoff body with `REFUSED REVIEW-PACKET` (15 x `brief-carries: carry N is not named in the body`), because `review_packet.part_carries` matches only the plural part line `This part: Carries <n,...> (0-based roster indexes`, and this dispatch PROMPT (15312a068a56) reads `This part: Carry 9 (0-based roster index, text verbatim below).`. Should the relay re-render PROMPT.md with the plural spelling (or fix the regex in tools/audit/seat/review_packet.py, outside this part's files), or am I to name all 16 carries against the brief's "the body names Carry 9 only"?

Measured: `review_packet.part_carries(PROMPT)` -> None, `prompt_carries` -> [0..15]; the same PROMPT with the line respelled `This part: Carries 9 (0-based roster indexes,` -> [9] (the control).

State:
- Code head pushed: refs/heads/handoff/r10-sav-valuation-residue-p4 = 8fac4e7e5b18dff2973f3cf35848199b9de26fb1, `tools/pr/prepr.sh` rc=0 there (PRE-PR ... 00000000000000000000000000000000 rc=0) with MUTANT_CMD set; `prepr.sh --body-check` ok on the body.
- The refused body is kept by body_push.sh at refs/heads/handoff-wip/r10-sav-valuation-residue-p4-body (d5886e47e05b). Once the part line scopes to [9], `bash tools/audit/seat/body_push.sh r10-sav-valuation-residue-p4 <that BODY.md>` is the only remaining step; no code change is needed.
- Origin/main was a77d71fb755f at the run (3481 and 3574 not merged); `git merge-tree --write-tree origin/main HEAD` reported no conflict.

body_push output (tail):
body_push: REFUSED REVIEW-PACKET
fatal: expected 'acknowledgments', received 'packfile'
warning: push negotiation failed; proceeding anyway with push
body_push: refused body kept at handoff-wip/r10-sav-valuation-residue-p4-body d5886e47e05b45ae6957f114052d75b63ebe25ef
