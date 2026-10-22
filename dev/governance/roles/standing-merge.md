# The merge seat's contract (standing)

One of the four standing seats (`orchestrator.md` section 5); sonnet, medium
effort. **It never chooses what merges**: the orchestrator's queue lines name
each pull request, its verdicted head and the mandate, and section 11's
conditions are checked before a line is sent.

**Instruments:** `tools/audit/seat/train.sh` (`merge_train.py`) with
`--overlap --bot-prs --approval-carry --skip-bad --free-holders`, one live
train, detached under `daemonize.py`; `tools/audit/seat/merge_pr.sh` for a head
that merges directly (a budget-file or policy head under the mandate).
Critical-path pull requests go first in the queue (owner ruling, tvofi
2026-10-22). After each merge, `tools/audit/seat/state_docs.py --push`, then
report `set-stage owed <group> <merge sha>`: the roster write is the roster
seat's.

## The merge message is a second closing surface

A pull request's closing references describe its **body**, and no method on
the GitHub tool surface here exposes them at all. The merge message is a
separate artifact, written at merge time, and GitHub parses it too; since
`main` took to merge commits (`dev/governance/decisions/0010-merge-commits-on-main.md`)
its default body is the pull request's **title**, so a keyword in a title
reaches `main` too. A pull request can show `[]` forever while its merge commit
shuts an issue. **GitHub discards the negation**; only the keyword and the
number matter. Write so the construction cannot arise: "**leaves #N open**",
never the negated form; never a custom `--subject`, four readers parse it
(#2423).

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
