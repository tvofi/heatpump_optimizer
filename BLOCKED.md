Part 1 (Carry 0-4): every carry is already implemented on main (evidence: standing.md Wait/Reads/Autofix hold/Recycle at 1b174e9b3; fixer.md BOOTSTRAP, designer.md, design-review.md at 1b174e9b3; ci_predict.py:656,872 at e566f7e02; orchestrator.md section 5). Nothing to change, so the diff against main is empty, and the pr-body lint refuses an empty diff. Body (all 5 carries as `Carry: dismissed: implemented at <sha>`) kept at refs/heads/handoff-wip/r10-standing-contracts-p2-body.

REFUSE pr-body: ERROR   [pr-body] --paths-file is empty. A pull request changes at least one file; an empty list means the derivation failed. (1 error line(s) in all) -- no budget leaf raised over ba544faa2...ba544faa2
body_push: REFUSED BODY-LINT

Question: the relay should fold Carry 0-4 as dismissed on the roster (no PR), or name one file for the part to touch. Carry 5-30 untouched.
