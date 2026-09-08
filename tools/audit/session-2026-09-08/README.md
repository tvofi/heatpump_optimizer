# Session evidence — governance audit, 2026-09-08

**This branch is an ARCHIVE and is not intended for `main` as it stands.** It
exists because everything in it was session-local: a reclaimed container would
have destroyed it, and none of it is reproducible by re-running anything.

`docs/plan-2026-09-governance-audit.md` is the execution plan the programme ran
against. It is NOT `docs/plan-2026-09-open-issues.md`, which is the open-issues
programme's plan of record and is a different document with a different job.
Parts of this one are discharged and parts are stale; it is preserved as the
record of what was intended, not as instructions to follow.

The four seat reports are the evidence behind merged pull requests, kept because
a verdict quoted in a squash body is a claim and the report is what backs it:

| file | what it establishes |
|---|---|
| `root-cause-unmeasured-reachability.md` | the cause behind `docs/decisions/0004`, five instances, a 24-site sweep, and the cost test with numbers. ADR 0004 carries the conclusion; this carries the working |
| `review-618-round1-sixteen-refuted.md` | refuted an unmeasured causal claim in #618's body by executing both resolvers at `e4a388a` |
| `review-618-round2-merge.md` | the `merge` verdict #618 was landed on, measured in a real `--depth 1` clone rather than a simulated one |
| `review-619-round1-citation-block.md` | blocked #619: four citations repointed to a commit carrying none of the files |

**Before merging any of this to `main`, note the cost.** `docs/` is INERT by
prefix so no gate scopes to it, but `named-docs` refuses a capped policy file
that cites an uncapped document by name — so nothing in the measured corpus may
cite these files until the `docs/decisions/` corpus classification is decided.
That decision is the owner's and is open.
