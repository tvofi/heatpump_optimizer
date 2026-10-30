Fix review: merge 16b89c74fc45da55428c174f27cce412111766bc

bus-nonce: e97bcecc06030da4c81078d907c58935

Round 1. Head measured: 16b89c74fc45da55428c174f27cce412111766bc (equals the PR head, re-read before posting). The diff against the merge base is two files: `dev/programme/triage/s6-batch69.md` and `dev/programme/delivery/2986.md`. No production code, no VERSION, manifest or RELEASE_NOTES change (0-line diff), no claim, closure or budget file.

## Findings

None. The bash-3.2 class sweep of the other array sites is the ruling P303 scope for the new group, not a defect here.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 16b89c74fc45da55428c174f27cce412111766bc` rc=0, no conflict, no MERGE-CLAIM lines (ev/HEAD.txt).
- RESULT roles-current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
- RESULT ruling-parse (mutation proof, re-run): `roster_edit.ruling_verdict` reads P301 DEFER, P302 ACCEPT, P303 ACCEPT. With P303's Verdict changed to REJECT it reads REJECT, so the parser consumes the file and the mutant is caught.
- RESULT structure: `tests/structure.py` prints STRUCTURE RATCHET PASSED.
- RESULT figures re-derived: bus.sh:134 comment and set -uo pipefail, bus.sh:645-649 arms=() with "${arms[@]}" at :649; the same comment at body_push.sh:11 and seat_venv.sh:41; `git log -S'arms+=(--no-ancestry)'` names d0f6de273; `git grep seat_gen b646e8306` hits only wave-r10-groups.json and s6-batch5.md; sweep_template.md:45 carries the transcript placeholder; the cited "" sites in body_patch.sh:98, cloud_relay.sh:439, pr_args.sh:172/239/242 and cloud-setup.sh:64,103-119 exist; R10-ORCH-BEATD is on the roster branch (4c91e6877 fetched).
- Figures not re-derived, out of tree or not reproducible here: seat-ledger.md lines 1100-2471 and its :1372/:1376 hits, orch-sweep.log's 31 board lines (21 rc=1), the s7/ script line counts (256/46/67/94), the `seat-launch.sh --dup` states, and the bash 3.2.57 repro (this host's /bin/bash is 5.2.21). The rulings rest on these; I could not check them.
- RESULT roster state: R10-FLY-SEAT-ALIVE-ID and R10-FLY-BUS-BASH32 are absent from the roster branch's groups file. The body calls the roster ops held and none cites P301, so this is consistent.
- RESULT forward-carry: body says none; P302's carry text is held in the file for `roster_edit.py append-carry`, as the file states.
- Red checks: none at the last read. 40 check-runs, no failure. At that read `tests / fast (3.14)` and `governance / instrument-self-tests` were still in progress; every other run was success or skipped, including mutation, closures, env-matrix, browser and arch-score. No pr-contract run was listed yet. This verdict does not cover those two runs or pr-contract finishing green.
- carry_audit at the head: 0 findings, 0 unrouted. review_packet refusals: none.
