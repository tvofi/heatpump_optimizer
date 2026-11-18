# BLOCKED: r11-outside-rooms-p3

Code head pushed to handoff/r11-outside-rooms-p3 at bae00a2be106bafe4e012f142bda4662f151cc06; prepr.sh clean there (`PRE-PR: bae00a2be106bafe4e012f142bda4662f151cc06 ... rc=0`, the code steps scoped with PREPR_SKIP_CLOSURES=1, the body re-checked with PREPR_SKIP_CODE=1 after a text-only delta). body_push.sh exited 1 on a figure-block base mismatch it cannot pass on its own: it re-renders the scope-line block with `--base` the pull request's recorded base (76bbf637442f, unchanged while fix/r11-outside-rooms-p3 sits at 9597676033), then verifies it against the merge base of the new head (99a4010e479f, after this round's main merge). Rendered at either base before the push, the result is the same refusal. Its output:

~~~text
fill-red: `## Red checks` already names mutation; nothing written
figure_block: refreshed 1 block(s) at bae00a2be106
ancestry reds ok: [code-scanning alerts NOT READ: no code run of ci.yml at 9597676033 yet] the body answers every red this branch pushed (governance / wave-script tests / mutation tests / mutation-autofix tests / nightly-status tests / replay)
pr-body ok: PR-BODY: 0 error(s) in /root/fixer-r11p3/BODY.md -- no budget leaf raised over 99a4010e47...bae00a2be1
carry ok: CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster bcc0511836
preflight ok
figures ok: FIGURES: 13 resolved, 5 not verified, 0 refused
  ERROR   [figure-block] line 78: block `scope-line` names head=bae00a2be106 mb=76bbf637442f, this run is head=bae00a2be106 mb=99a4010e479f; re-render with `figure_block.py refresh <body>`
figure_block verify: 1 block(s), 1 refused
REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
ref_privacy ok: ref_privacy --check at HEAD: 32 file(s) with a push site, 12 guarded, 1337 line(s) added since 99a4010e479f judged, 0 refused
ref_privacy (body) ok: no host identity in the body
body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again
body_push: REFUSED BODY-LINT
body_push: refused body kept at handoff-wip/r11-outside-rooms-p3-body 8f99e70d279de192d4a8ef4444006e1ef34fd242
~~~

The body is kept at handoff-wip/r11-outside-rooms-p3-body 8f99e70d279de192d4a8ef4444006e1ef34fd242; its figure block reads 76bbf637 because body_push rendered it. Once the pull request's head is moved to bae00a2be1 its recorded base follows, and `figure_block.py refresh` at that base renders the block body_push verifies.
