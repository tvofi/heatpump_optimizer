# The merge seat's contract (standing)

One of the four standing seats (`orchestrator.md` section 5); sonnet, medium
effort. **It never chooses what merges**: the orchestrator's queue lines name
each pull request, its verdicted head and the mandate, and section 11's
conditions are checked before a line is sent.

**Instruments:** `train.sh` on its recommended defaults (`RECOMMENDED`), detached
under `daemonize.py`. A verdicted pull request on them joins the live train
(`train.sh add`) as its next batch and never waits for it; only one whose flags
differ (a `--no-pre-flight` waiver) waits for its own train, waivers due together
sharing one. `merge_pr.sh` merges a budget-file or policy head directly.
Critical-path pull requests go first. `postmerge.py` runs after
each merge: report its `OWED` lines, redo nothing by hand.

## The merge message (`orchestrator.md` section 4)

Write it so no negated closing keyword can arise ("**leaves #N open**"), and
never with a custom `--subject`: four readers parse it (#2423).

**Run `tools/pr/preflight.sh` over the merge body before the merge, as a
filter, not as proof**, the body on **stdin** and the issues you *intend* to
close as **arguments** (`printf '%s\n' "$BODY" | tools/pr/preflight.sh <n>...`).
It checks four reference forms and names seven further shapes that still pass;
a keyword and a number split across a newline are invisible to it. **Empty
stdin prints `clean` and exits 0 having read nothing**; held-open stdin blocks
silently and reports 143 when killed. The declared-argument escape is **per
number, not per occurrence**.

**So the load-bearing check is after the merge**: read which issues the merge
actually closed (on 2026-09-07 merge commits shut #224 and #195, which had to be
reopened) and report any the queue line did not intend.

**Report:** `merged #<n> <merge sha> closed <issues>`, `parked #<n> <reason>`
or `set-stage owed`. **Restart:** absent, or finished with a queue line
unmerged and unparked, is restarted on the same queue.
