Fix review: blocked 0c3138c5f35760a738cf78694f91cb65af4c3726 root-cause-unanswered: gate

bus-nonce: 8e5af60d1dd4d41c4fb90737e729b717

Round 1 (sonnet), head 0c3138c5f35760a738cf78694f91cb65af4c3726. Fix-review contract read from main (roles dir unchanged between merge base and main per the check). I ran on Linux and could not reproduce the Darwin 127; the Darwin claim is reasoned from the diff and the body's recorded Mac evidence only.

## Block
- `gate` (check-run 128823275143) concluded failure at this head and the body's `## Red checks` says "none". The gate log's only line is "FAIL run(s) [42510666835] at this head are still being judged; their gate decides" at 18:36:40Z, i.e. an early-run race, not a code failure; every other concluded check of the head is green or skipped (env-matrix, instrument-self-tests, browser, closures were in_progress at render). I polled merge_train classify (>60 s apart, background) until it exited 1 (RED, pending: none, red: gate). Fix rule 11: the body must name the red gate and answer it (cheaper detector, or none). It does not, so I cannot tell which; the author should name it in `## Red checks` (a race of the gate against the head's still-running workflows, answerable by naming it) and re-trigger the gate. The code change itself is sound; nothing below blocks on it.
Carry: built-here

## Findings
- Residual: the arm's repair is Darwin-only in effect; no Linux CI arm exercises a shimmed python3 under a planted HOME, so the fix has no automatic regression guard (Mac-only evidence, mutation proof run by the author on a Mac).
Carry: dismissed: owner ruling scopes this as a hand-run hotfix for a shim host; no cheaper CI detector exists on Linux.

## Evidence
- Setup: cloud-setup check OK; merge-tree origin/main vs head: clean (tree bf0b4de2e98a, no conflict). Diff three-dot: tools/pr/prepr.sh (+5/-2 lines of change) and dev/programme/delivery/3343.md only; no new tracked file beyond the delivery row; no budget, VERSION, manifest, RELEASE_NOTES.md or closures change. `## Head` names the head and the authored code head.
- RESULT self-test at head (Linux): 514 passed, 0 failed, rc=0 (ev/selftest-head.log).
- RESULT self-test at main (Linux, null control: real python3 unaffected at both ends): 514 passed, 0 failed, rc=0 (ev/selftest-main.log).
- RESULT planted-HOME pair at head with the fix's PATH prefix, body_privacy_line extracted from the head: clean body rc=0, planted body rc=1 (ev/planted-home.txt).
- RESULT mutant (body_privacy_line's python call replaced with `true`, so the subject never fails): 513 passed, 1 failed, rc=2: "FAIL a body naming the host home directory is refused by body_privacy_line (got 0, wanted 1)" (ev/selftest-mutant.log). The arm still fails when its subject fails; the PATH change does not mask it.
- Reading the diff: the added `pfp` prepends the directory of `python3 -I -c 'import sys; print(sys.executable)'`, run under the real HOME before the planting; the two calls then use that PATH under the planted HOME, so a shim that resolves its venv under HOME is bypassed. It adds only the PATH variable to the call env and changes no assertion, so it cannot reach 127 via the shim; whether a shim's sys.executable names the real binary on Darwin is not verifiable here.
- tests/entities.py: did NOT run clean here: venv-ci python3 raises ModuleNotFoundError: homeassistant (ev/entities.log); venv-ha python3 raises ModuleNotFoundError: paho (ev/entities-venvha.log). Environmental, not caused by the diff; no BASH_ENV workaround used.
- Mutation proof of the body (removing the PATH prefix) is Mac-only; not re-derived here. Figures: none claimed (figure_lint 0 resolved, 0 refused).
- Review packet refusals at render: red-unanswered (gate), required-red (gate); packet in ev/review-packet.md.
