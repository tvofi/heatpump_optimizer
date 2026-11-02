# Proposal triage, session s10, batch 109 (P367)

The rolling batch after batch 108. Facts were read at origin/main `78dd34354`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`dff6373f7`), at pull request #3155, and in the
session's seat ledger. This is the first ruling under the owner's LOG class (tvofi,
2026-11-01 ~19:50Z): a proposal whose friction blocks no production merge and that proves no
improvement above 10% is recorded with its evidence, and no carry or group is built. The batch
grammar has no LOG verdict, so the ruling is written as DEFER, naming what would change it.

## P367: a cloud reviewer ended its session with its CI poll in the background, so no verdict posted

Verdict: DEFER (LOG, by the owner's 2026-11-01 ~19:50Z rule). No carry and no group. The answer
changes on a measured figure above 10% in CI time, completion time, right-first-time or tokens,
with a baseline and a null control. It also changes if this friction holds a pull request that
touches `custom_components/`.

Source: the orchestrator s10's queue line of 2026-11-02T00:10:47Z. It proposes that the reviewer
and fixer brief template require foreground polling until the verdict posts.

Instances:
- **#3155, one instance.** The cloud reviewer session `cse_0189ZDZ9h5aHcURZsv2BSqoN` ended with a
  background CI poll still running, so no verdict was posted.
  - #3155 is `record/autofix`, the delivery rows for #3047, #3050, #3118, #3141 and #3142. Its six
    files are all under `dev/programme/delivery/`; none is under `custom_components/`.
  - The seat ledger shows the cost. At 00:04:45Z the stamp's flush timed out after 3000 s waiting
    on #3155. At 00:06:06Z v7.1.1 was stamped at `78dd34354` with `--no-flush --allow-rowless --allow-red`.
    The merge seat added #3155 to the train in normal order at 00:09:35Z. The release went out; its delivery rows
    follow #3155's merge.
- **The brief says background on purpose.** `tools/audit/seat/cloud_dispatch.py` at `78dd34354`:
  - line 193 tells every seat to "Run anything heavy in the background with Monitor and no
    timeout";
  - line 207 tells the reviewer to wait for CI by re-running `merge_train.py classify` "in the
    background, at least 60 s between runs";
  - `WAIT_LINE` (line 132) caps a single tool call at 240 s.
  - A foreground rule would cap the poll at 240 s per call, which the brief already allows, so
    what the proposal changes is only the wording around ending the session.
- **A recovery path exists.** `bus.sh dispatch` mints a fresh nonce for a head with no verdict, so
  a reviewer that returned none can be re-fired. The cost of an instance is one re-fire and the
  wait until someone notices.

Cost:
- As filed it is S: one or two sentences in `_prompt()` in `cloud_dispatch.py`, plus its
  self-test's text pins (line 1035 pins the "in the background" wording).
- No figure was given for the benefit. One instance in this window does not measure a rate.

Binding:
- **Why LOG.** No production merge is held: #3155 is a record pull request. Nothing measures
  how often a cloud seat ends without a verdict against all cloud dispatches. Without that rate
  there is no >10% figure.
- **What would re-open it.** A count of cloud reviewer and fixer sessions that ended with no
  verdict or no return push, over all cloud dispatches in a stated window, with the token or
  wall-clock cost each one added. The figure must exceed 10% of review rounds or of review
  tokens.
