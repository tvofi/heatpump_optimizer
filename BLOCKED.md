# BLOCKED: r11-seam-actuation-writes

Question: Orchestrator NOTE 1 (inbox/r11-seam-actuation-writes, 2026-11-21 13:02 UTC) said to wait and re-dispatch this seat from main after #3728 and #3812 merge. #3728 has merged and #3812 has not. Should this seat stay stopped until #3812 merges and then be re-dispatched, as NOTE 1 says?

What this blocks on: a precondition, not a tool refusal, so there is no refusal line to quote. The approved design 28bedac8a678 puts this group "third on the actuation chain, after both predecessors merge" (section 6). Its Notes for the fixer item 1 makes the release group's merged diff an input: the frequency and valve tails move into their owners there, and the availability predicate goes before their send in those places. NOTE 1 says the same thing: wait.

Measured 2026-11-22T15:11Z against origin/main 8ef450936a1786abf4bb9610dc3336da4e77e8de:
- R11-SEAM-kernel-step: merged. `git log --oneline origin/main | grep -i -E 'kernel-step|actuation-release'` prints `4ebd430fbf Merge pull request #3728 from tvofi/fix/r11-seam-kernel-step` and no actuation-release merge. Null control: the same grep does print the kernel-step merge, so the command finds merges when they exist.
- R11-SEAM-actuation-release: PR #3812 (head 3af986ddb80b, code head e9922bc1c300) is `state: open`, `merged: false` and `mergeable_state: blocked` (pull_request_read get). `git log --oneline origin/main | grep -E '#3812'` prints nothing.
- The body of #3812 lists departures from design 349d6277 that are pending owner confirmation. Its frequency and valve tails are `FrequencyWatchdog.command` and `mixing_valve.ValveTarget.command`, with the registrations in `coordinator.py` and `number_restore.py`. It also carries two items forward to this group: invariant 2 and the GCHV night registers. If this group built on that head now, it would build on an unreviewed, unmerged tree whose tail placement this design's section 2 depends on.

Clears when: #3812 merges. After that, this seat is re-dispatched from that main (NOTE 1), reads the release group's merged diff first (design note 1), and takes #3812's two forward-carry items.

No code was written in this fire. Comms: topic r11-seam-actuation-writes, NOTE 1 acknowledged.
Carry: R11-SEAM-actuation-writes
