# BLOCKED: r11-pre-round-metrics-p3, body_push figure-block base mismatch

Question: re-render the body's scope-line figure block against the base pr-contract verifies with, and re-run body_push for r11-pre-round-metrics-p3? The code is pushed and passes prepr.

Code head: handoff/r11-pre-round-metrics-p3 = 411d996cdd2879646543a448730f3a96e5b2ac73 (fast-forward over the reviewed head 321d7f9f34526984b5eca8d18870cd14cffbe6f6).
prepr: passed rc=0 at 411d996cdd2879646543a448730f3a96e5b2ac73 (PREPR_SKIP_CLOSURES=1).
Body: the refused body is kept at handoff-wip/r11-pre-round-metrics-p3-body 7c1898fa4cf10adf28306bd6b8d87fd73efbfcec.

Refusal, `bash tools/audit/seat/body_push.sh r11-pre-round-metrics-p3 <body>`:

~~~text
fill-red: the diff adds no unpinned mutation site; nothing written
figure_block: refreshed 1 block(s) at 411d996cdd28
ancestry reds ok: [code-scanning alerts NOT READ: FAIL closed: code-scanning/analyses page 1: HTTP 403] the body answers every red this branch pushed (tests / nightly-status)
pr-body ok: PR-BODY: 0 error(s) in /root/seat-r11p3/BODY.md -- no budget leaf raised over 6f422812d5...411d996cdd
carry ok: CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s), at origin/handoff/audit-r10-roster 25d8744c03
preflight ok
figures ok: FIGURES: 4 resolved, 1 not verified, 0 refused
  ERROR   [figure-block] line 64: block `scope-line` is not what the registered instrument printed at 411d996cdd28; a figure block is rendered, never typed -- run `figure_block.py refresh <body>`
figure_block verify: 1 block(s), 1 refused
REFUSE figure blocks: figure_block verify: 1 block(s), 1 refused
ref_privacy ok: ref_privacy --check at HEAD: 30 file(s) with a push site, 12 guarded, 327 line(s) added since 6f422812d5d8 judged, 0 refused
ref_privacy (body) ok: no host identity in the body
body_push: the pr-body lint refuses this body (above), as open_pr.sh's prepr step 7 would; repair it and push again
body_push: REFUSED BODY-LINT
body_push: refused body kept at handoff-wip/r11-pre-round-metrics-p3-body 7c1898fa4cf10adf28306bd6b8d87fd73efbfcec
~~~

Cause, measured. body_push renders the block with `figure_block.py refresh --base <PR #3658 recorded base 6f422812d5d8b918beace0283419c153f6df66ce>`. Its pr-body lint then verifies the block against origin/main (30f9caac90735c402c8e3ae60fbaa80c45dc6d26). The registered scope-line instrument overlays the base's `tests/closure.py` and `tools/pr/figure_block.py` onto a detached worktree at 411d996cdd and runs `figure_block.py _scope 6f422812d5d8b918beace0283419c153f6df66ce <workdir>` with the registry's stripped environment:
- base 6f422812d5d8b918beace0283419c153f6df66ce: `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`
- base origin/main 30f9caac90735c402c8e3ae60fbaa80c45dc6d26: `MODE: FULL -- every test script runs, nothing is scoped out.` (reason `no changed files could be determined`)
No single rendering satisfies both bases, so the seat cannot repair it.
