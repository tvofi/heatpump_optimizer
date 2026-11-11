# BLOCKED: r10-rca-dependabot-stale-hash

Question: fold the carry to R10-DEPENDABOT-3414-COMPAT on the roster and re-run body_push.sh?

Code head: handoff/r10-rca-dependabot-stale-hash at a1d062e3a7f074331cc8666f70e1b1b80e9713d6 (prepr.sh rc=0, receipt a1d062e3a7f0).
`bash tools/audit/seat/body_push.sh r10-rca-dependabot-stale-hash <body.md>` exited 4; its output (tail):

    body_push: REFUSED CARRY-LANDED
    body_push: refused body kept at handoff-wip/r10-rca-dependabot-stale-hash-body 7a09f5f56975798deef6c7009839a514aba05395

The carry, from the body's Forward-carry: reword every lock comment
`dev/audit/harnesses/dependabot_stale_hash.py --tree` lists so no pinned
package is spelled `name==`; in the same diff correct .github/dependabot.yml's
"Dependabot leaves some hash lines stale" to name the cause; run `--tree`
from the suite that reads the locks (exit 1 at its parent, exit 0 at its
head). Carry: R10-DEPENDABOT-3414-COMPAT
