# R10-RCA-OTHER-UNTAUGHT: the untaught family is mostly spellings, and one real obligation hides in three of them (#3283)

The root-cause record for the recurring-friction family key `other (untaught)`
(#3283), filed by the governance cron's friction step. It ran apart from any
fix. It lands this record only: it changes neither the keying rule nor the
classifier. The one countermeasure it proposes is policy-adjacent and waits for
the owner, section 6.

**Merge base and window.** Every figure was taken on 2026-11-08 at merge base
`origin/main` `73365699a135fb813a43380096b6776d57f8ff4c`, window `v7.1.4..origin/main`.
Counts below are dated to that base; re-derive them, do not copy them.

## 1. The count, re-derived

`node tools/policy/policy_lint.mjs --stats --since v7.1.4` prints the row
`other (untaught) (family)` and a would-open line for it, with its union reduced
by the pull requests `ci-red` already files on its own line. The family is built
at read time (`statsFamilies`, `UNTAUGHT_FAMILY` in `tools/policy/policy_lint.mjs`):
every verdict key the wave script's block classes (`.claude/workflows/web-fix-wave.js`)
do not teach, other than `merge`. #3283's body was written at an earlier, smaller
reading of the same window; the count reproduces and grows because the window does.

Per-key entries were read with `dev/audit/rca/ci-red/entries.py` over a
`--window-cache` of the same window (the histogram's own rule: first line
matching `VERDICT_RE`, key = the class word after the head sha).

## 2. The pull requests and the friction each hit

Pull requests the family holds on its own (not held by `ci-red`):

| PR | key | friction |
|---|---|---|
| #3232 | `regression` | `select.select` refuses pipe fds >= 1024; `tests/entities.py` fails the log-flood barrier on the new WARNING |
| #3246 | `wait-cycle` | the deferring edit gate waits on a later edit run whose prelude waits on it |
| #3247 | `owner-words` (x2) | `D0.md` owner text reworded across four sections, not cut; same verdict posted twice at one head |
| #3250 | `instrument-broken` | a mutant self-test plant's anchor occurs zero times |
| #3252 | `red-checks` (x2) | body's `## Red checks` names none of the head's concluded reds, in both rounds |
| #3253 | `selftest-red` | `roster_queue.py --self-test` crashes under `python3 -I`, red in `instrument-self-tests` and unnamed in `## Red checks` |
| #3255 | `policy-unapproved` (x3) | policy text deleted outside the approved text; round 4 re-dispatched the blocked head unchanged |
| #3261 | `citation-false` | an RCA cites a lead as unbuilt that a record says another group closed |
| #3264 | `defect` | `--since-tag` credits no multi-PR group's part-branch merges, and `## Red checks` names no concluded red |
| #3287 | `settle-unjudged` | a higher-id gate that deferred to a lagging lower run is never re-run |
| #3295 | `claim-refuted` | a prior RCA's "no check failed" claim; `tests / mutation` had concluded failure |

Held by `ci-red` and so left out of the family: #3242, #3244, #3265, #3273.
(#3242 also carries the window's one `carry-unanswered` entry.)

Spot-verified against the window cache for `red-checks`, `selftest-red`,
`defect`, `owner-words`, `policy-unapproved`; the other rows are the PR
comments as read by the dispatching seat and are not independently re-read.

## 3. Cause

The reviewer writes a free-text class word; the wave routes any word it does not
teach to the untaught family. The family therefore measures **spelling
dispersion**, not one obligation. Of the eleven pull requests, seven are
singletons whose mechanism no taught class and no other pull request shares
(`regression`, `wait-cycle`, `instrument-broken`, `citation-false`,
`settle-unjudged`, `claim-refuted`, `owner-words`). They are noise as a family
and each is already fixed by its own pull request. `policy-unapproved` is one PR
with three rounds.

One cluster is not noise. Three pull requests, #3252 (`red-checks`), #3253
(`selftest-red`) and #3264 (`defect`), were blocked for the same obligation:
the body's `## Red checks` did not name a concluded red of the head. That is the
taught `root-cause-unanswered` obligation (`defect-root-cause.md`, Enforcement),
spelled three ways. The taught `root-cause` family holds one pull request in the
same window; with these three it would hold four, over the threshold of three.
Three further pull requests held by `ci-red` (#3242, #3244, #3265) carry the
same unanswered-body shape and are already counted under `ci-red`.

## 4. Process state, with evidence

**(c): the process was followed and did not produce the intended result.**
The derived family exists (#2436) so that an obligation whose spelling moves
still reaches the threshold. It ran, fired, and filed #3283. Its premise, that
an untaught word marks one obligation, holds for the red-checks cluster and
fails for the seven singletons, so the filing is mostly un-actionable while the
real cluster is buried in it. The reviewers were not disobeying: the grammar
asks for a class word and lets any word through to `other`; nothing told them
`red-checks` was already taught as `root-cause-unanswered`. This is not (b); a
firmer instruction to reviewers is the wrong-direction fix that
`root-cause.md` section 2 warns of.

## 5. Class reach, and the cost test

Reach: the same split recurs wherever the verdict word is free text. The
declared families (`mutation`, `environment`, `root-cause`) are each a past
instance of it, measured in an earlier window. Nothing here widens that class.

Cost test, `cost(countermeasure, recurring) < cost(defect) x P(recurrence)`:

- Teach all thirteen words to the classifier: standing cost is a grammar that
  grows by one word per new mechanism and a reviewer reading a longer list on
  every verdict. The seven singletons have measured recurrence of one pull
  request each in this window, so P(recurrence) per word is at most one in a
  window. This fails the test.
- Add `red-checks`, `selftest-red` and `defect`-with-unnamed-reds to the
  `root-cause` family in `FRICTION_FAMILIES`: standing cost is zero seconds per
  run (a list entry read at stats time). Defect side: the unanswered-body block
  cost the three pull requests of section 3 a measured 396, 279 and 852 minutes
  to their next verdict (the `entries.py` gap column, upper bounds that include
  idle time). Passes the test, but `defect` is not a reliable key for this
  obligation (the #3264 line names a second defect), so only `red-checks` and
  `selftest-red` are proposed, and the second is a weaker fit.
- Recommending nothing for the remaining ten is the recorded result.

## 6. Countermeasure, and what this record changes

This record changes nothing in the tree except itself.

1. **Refusal, with the number from section 5:** do not teach the seven
   singletons (`regression`, `wait-cycle`, `instrument-broken`,
   `citation-false`, `settle-unjudged`, `claim-refuted`, `owner-words`) nor
   `policy-unapproved`. The family is noise for them. #3283 should be disposed as
   noise for those, with this record cited.
2. **Proposed, for the owner (state c):** fold `red-checks` into the
   `root-cause` family in `FRICTION_FAMILIES`. It is a one-line change to
   `tools/policy/policy_lint.mjs`; it is a check of the classifier and so owes
   the demonstration `defect-root-cause.md` requires, a window where it fails
   (family below threshold, obligation hidden) and passes (family counted), plus
   a null control on a window with no `red-checks`. That demonstration is not
   built here; it belongs to the group the owner approves. The declaration rule
   (a family must be measured in a real window first) is met by section 3.

## 7. Not established here

- The rows of section 2 not named as spot-verified were not re-read from the
  PR comments by this seat.
- Whether `selftest-red` and `defect` are the unanswered-body obligation or a
  second one beside it: their lines name another defect too, so they are not
  folded in this proposal.
- No class-barrier is owed: this is a friction family, not an audit class.
