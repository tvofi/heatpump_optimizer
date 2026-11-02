Fix review: merge a76792d8f091dfa5232c1c0bb89965de4f2a506a

bus-nonce: bb0ed9a985eca6e996a07bb81c04fcd2

Round 1, record PR, reviewed at head a76792d8f091dfa5232c1c0bb89965de4f2a506a (still the PR head at posting).

## Findings

- The PR body says the diff is "one markdown file" while the three-dot diff holds two: the triage file and the PR's own delivery row `dev/programme/delivery/3157.md`. The body's ## Head section explains the extra commit, so it is wording only. Carry: dismissed: wording only, ## Head accounts for the second file
- The batch file calls itself "session s10" while the PR title and branch say "s9". Batch 107 uses the same pairing, so it is the existing convention. Carry: dismissed: matches batch 107 convention

## Evidence

- Three-dot diff: exactly two files, dev/programme/triage/s6-batch109.md (+53) and dev/programme/delivery/3157.md (+1). No custom_components, claim file, VERSION, manifest or RELEASE_NOTES change. No host path in the added lines.
- Merge with origin/main (78dd34354): merge-tree clean (ev/merge-tree.txt).
- Facts re-derived at 78dd34354: cloud_dispatch.py line 132 is WAIT_LINE, 193 is "Run anything heavy in", 207 is the classify "in the background" line, 1035 is the self-test pin. v7.1.1 tag is 78dd34354 (committed 00:05:45Z). Roster branch is dff6373f7.
- #3155 (via the PR files API): six files, all under dev/programme/delivery/. It adds its own row 3155.md and updates 3047, 3050, 3118, 3141 and 3142, matching the file's list.
- Mutation proof re-run on roster_edit.ruling_verdict: committed file gives P367 DEFER and P368 None. With the verdict flipped to ACCEPT it gives ACCEPT. The body's claims hold.
- Ruling: DEFER names a testable re-open condition (a count over a stated window above 10%, or a custom_components PR held). No carry or group is built, as the ruling says. The quantified claim "one instance gives no rate" states no baseline and is not a rate claim.
- Could not verify: the seat-ledger timestamps (00:04:45Z, 00:06:06Z, 00:09:35Z), session id cse_0189ZDZ9h5aHcURZsv2BSqoN and the orchestrator queue line, which live on the orchestrator's machine. The owner's LOG rule of 2026-11-01 ~19:50Z is cited by date and is not in the tree. P367 is not on the roster, as designed.
- Checks: merge_train classify returned GREEN, pending none, red none (rc=0, ev/classify.txt). ## Red checks says none, and no concluded red check exists at the head. carry_audit at the head found 0 findings in the packet.
