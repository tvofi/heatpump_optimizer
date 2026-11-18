# R10-RCA-JIDOKA-YIELD: why step 7e did not cut carry-missing blocks (probe at 437f1ba9b)

## Premise correction: the step is #2838's, not #2853's

Step 7e (`carry_line`, `tools/pr/prepr.sh:990`), and its call inside `--body-check` (the call `body_push.sh` runs), arrived in commit 1b9a86266. They reached main in **#2838** (bdf69a5c3, 2026-10-26T04:40:21Z). `git show bdf69a5c3^1:tools/pr/prepr.sh | grep -c 'cline=$(carry_line'` prints 0, and the same command at bdf69a5c3 prints 1. **#2853** (53c4b9cb0, 2026-10-28T03:16:58Z) added only `--fill-red` to `body_push.sh`, plus claims, privacy and figure steps. So the window that tests step 7e starts at #2838. Below, both cut points are reported.

## Re-measured yield

Enumerator. Corpus: every commit reachable from `refs/heads/verdict/*` and `refs/tags/archive/verdict/*` (534 refs, 1328 commits). Each subject is parsed as `verdict: #N Fix review: <word> [<sha>] [<class>:...]`. Verdicts are deduped on (PR, word, sha, class), keeping the earliest, which leaves 1126 verdicts and 459 blocked. The clock is the commit's `%ct` (epoch, so no timezone is involved). The window runs from the first verdict (2026-10-06T18:01Z) to 437f1ba9's commit (2026-10-30T20:32:38Z).

```
git fetch origin '+refs/heads/verdict/*:refs/remotes/origin/verdict/*' '+refs/tags/archive/verdict/*:refs/tags/archive/verdict/*'
git log --format='%H%x09%ct%x09%cI%x09%s' $(git for-each-ref --format='%(refname)' refs/remotes/origin/verdict refs/tags/archive/verdict) | sort -u > vc.tsv
python3 -I vcore.py vc.tsv   # vcore.py: the parser/dedupe/window script in the appendix
```

| window | carry-missing / blocked verdicts | PRs with carry-missing / PRs with a block | PRs reviewed |
|---|---|---|---|
| before #2838 | 50/334 (15.0%) | 45/199 (22.6%) | 390 |
| #2838..#2853 | 5/35 (14.3%) | 5/23 (21.7%) | 50 |
| after #2853 | 16/90 (17.8%) | 14/53 (26.4%) | 122 |
| after #2838 | 21/125 (16.8%) | 19/73 (26.0%) | 168 |
| after #2838, PRs numbered >2838 only | 18/100 (18.0%) | 16/56 (28.6%) | 146 |

The rate is 2.57/day before #2838 and 4.51/day after it. Measured from block to the next verdict on the same PR, a carry-missing block costs a median 84 min (p25 36, p75 216, n=69). The step did not lower the share on either cut. The orchestrator's crude 95/652 and 22/121 differ from this table in dedupe and class prefix. This table counts the `carry-missing` class exactly. The `carry-unrouted`, `carry-stale` and `carry-scope` classes are excluded.

## (1) Each post-#2838 carry-missing block: did step 7e run, and why did it not refuse?

Step 7e runs at every `open_pr.sh` (prepr `CARRY_LINE=$(carry_line "$BODY")`, `prepr.sh:3936`). For a cloud seat it also runs at `body_push.sh` whenever `handoff/<topic>` exists, because `--body-check` folds `carry_line`'s rc into its own and `body_push` refuses on it. Cloud and local fixers therefore both reach it. PRs numbered below 2838 (#2528, #2554, #2580) were opened before it existed.

"Reviewer's carry_audit" below means what the blocking verdict's own evidence printed for `carry_audit.py check --body` at the blocked head (`git grep CARRY-AUDIT <verdict commit>`).

| verdict | PR | reviewer's carry_audit | shape |
|---|---|---|---|
| 9008a6854 | #2849 | 2 routed, 0 unrouted | A |
| 36b59ff31 | #2852 | 2 routed, 0 unrouted | A (marker names the PR's own group, which closes at merge) |
| e3bc3b7fd | #2854 | not in evidence | A (codes "live only in the PR body") |
| 9cabb1d70 | #2871 | 3 routed, 0 unrouted | A (carried only in this body) |
| a374d0b6c | #2899 | not in evidence | A |
| aa2a03c01 | #2906 | not in evidence | A |
| aca91d7d1 | #2896 r1 | 17 routed, 0 unrouted | B (`#2733`'s groups done/absorbed; the reviewer notes carry_audit accepts it) |
| d91a634f7 | #2896 r2 | 17 routed, 0 unrouted | B (second destination; "it does not see the double destination") |
| b70714b39 | #2914 | not in evidence | B (destination groups re-derived `done` by the same batch) |
| 403f83c25 | #2528 (pre-step) | not in evidence | B (routed to #201, which has no carry file citing it) |
| a1c12e533 | #2554 (pre-step) | not in evidence | A |
| 98ef788b0 | #2580 (pre-step) | 2 routed, 0 unrouted | A ("That routing is syntactic. The block above is about the destination's content.") |
| d0033ecbe | #2946 | 3 routed, 0 unrouted | A |
| e5e2a0c8b | #2925 | 1 routed, 0 unrouted | A (open seam carried to no stage) |
| 16e5d627e | #2961 | 7 routed, 0 unrouted | A |
| 39f4cfdfa | #2962 | 0 finding items | B (`Carry: #2959` sits in `## Mutation proof`, a section carry_audit does not read as a finding) |
| 1af0c637c | #2925 | 2 routed, 0 bad (body) | A |
| 258bc873b | #2992 | 4 routed, 0 unrouted | A (seam "only in the PR body") |
| 0f8e3454e | #2995 | not in evidence | A |
| 354e3f218 | #3004 r1 | not in evidence | B (owed roster carry routed to R10-FLOW-WIP, a consumer after-edged on it: a live destination, an invalid disposition) |
| 35f15ea69 | #3010 r1 | 0 finding items | C |

The shapes, as counts of the 21 verdicts:
- **A (14).** The marker names a live destination, but the destination's brief on `handoff/audit-r10-roster` does not hold the finding and its control.
- **B (6).** The marker names a destination that carry_audit's liveness test accepts, but the disposition is invalid for a reason that test does not model.
- **C (1).** An owed roster carry is stated in prose outside the sections carry_audit reads, and the carry sections say `none`.

In none of these did the step skip, or refuse and get bypassed. Where the verdict recorded the run (12 of 21), carry_audit returned 0 unrouted on the very body that was blocked. Step 7e ran, could not have refused these bodies, and so passed them.

**#3010 r1, reproduced.**
- The fixer's code head 0b79e8de equals `handoff/r10-fly-train-defaults`.
- The fixer's base cf4f6b7a6 contains bdf69a5c3, and its prepr.sh holds the `--body-check` carry call (count 1).
- `handoff-body/r10-fly-train-defaults` da4e6e9ea (2026-10-30T18:43:56Z) is the r1 body.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <da4e6e9ea:BODY.md>` prints `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`, rc 0, in 0.31 s.

The owed item ("**Roster carry (open, not answered by this change).** Carry 1: **not done in this pull request.**") sits in an untitled paragraph before `## Head`. Its first words do not match `LEAD` (`carry_audit.py:121-123`), and `## Forward-carry` says `none`, so `items()` (`carry_audit.py:218-222`) flags nothing. The handoff's `brief-carries` arm (`review_packet.py:358`) also passes it, because it only counts that `Carry 1` is named. Each check passes, and the hole lies between the two: a carry the body names as *not done* owes no route.

## (2) Process state: (c)

The process existed and was followed: step 7e ran at the open and at `body_push`. It did not produce the intended result, because its unit is narrower than the defect class it was built to remove. The WHY at `prepr.sh:974-978` says "25 were `carry-missing` ... This is that same checker". That premise is false. The `carry-missing` verdict is fix-review.md step 10: "open it (a roster carry at the body's `handoff/audit-r<N>-roster` SHA) and confirm it states its control as a precondition". That step judges whether the destination holds the finding. carry_audit judges whether a marker exists and names a live destination. The evidence is the 12 verdicts above whose own carry_audit run printed 0 unrouted on a body they blocked as carry-missing. The case is not (b), since nothing was skipped, and not (d), since the class had the same shape before and after (15.0% → 16.8%). This is #2073's pattern: a half-port that checks one direction of the reviewer's test.

**Class reach.** The 222 `handoff-body/*` tips were run under the patched arm below. They hold 8 further bodies, besides #3010, with an owed roster carry stated as not done and no route: r10-cop-partload-p2, r10-fly-openpr-atomic (2 items), r10-orch-planpage, r10-sav-comfort, r10-sav-comfort-r2, r10-sav-comfort-r3, r10-train-overlap-grade (9 items) and r10-ux-health-p2. Shape C is therefore latent at about 4% of bodies, though only one has been blocked so far. Shapes A and B are 20 of the 21 blocks.

## (3) Countermeasure and cost test

This is an audit class (21 carry-missing verdicts in round 10 since the step, 71 in all), so a barrier is owed.

**M1, demonstrated (covers shape C).** A body item outside the carry sections that names a roster carry index together with a not-done phrase becomes a finding item, which then needs a `Carry:` marker. Scratch copy of `tools/audit/carry_audit.py`:

```
+OWED_CARRY = re.compile(r"\bcarry\s*\[?\d+\]?\W{0,6}[^.\n]{0,80}?\b(?:not done|not (?:built|answered|implemented)|not in this (?:part|diff|pull request|change)|still (?:not met|open|owed)|owed (?:by|to|in))", re.I)
@@ items(), body branch
-                   else "under lead" if inherited else "")
+                   else "under lead" if inherited else "owed carry" if OWED_CARRY.search(t) else "")
```

- **On the defect** (#3010 r1 body, da4e6e9ea): rc 1, `UNROUTED body item c78ecb78 [owed carry]: "**Roster carry (open, not answered by this change).** Carry 1: **not done in this pull request.** ..."`, summary `1 finding item(s): 0 routed, 1 unrouted`.
- **Once routed** (the same body with ` Carry: R10-FLY-TRAIN-DEFAULTS` appended to that paragraph): rc 0, `1 routed, 0 bad destination(s)`.
- **Null control** over the 222 `handoff-body/*` tips: the unpatched script returns rc 0 on 164 and the patched one on 155. The 9 bodies that flip are #3010 and the 8 listed under class reach. Each is an owed carry with no route, so each is a catch by finding-propagation.md's own rule, not noise. The patched copy's `--self-test` prints `206 checks, 0 failed`. The arm has no fixture or mutant yet. When it is built, it owes a fixture, a mutant, and its `field_coverage.mjs` registration.
- **Cost test**, in wall-clock per day of round 10:
  - Defect side: shape C was 1 block in 4.66 days (0.21/day) × 84 min median = **about 18 min/day**.
  - Standing cost: carry_audit runs in 0.12 s (patched, #3010 body) and runs about 3 times per PR (body_push, open, pr-contract). At about 45 PRs/day (122 reviewed in the 2.72 days after #2853), that is about 16 s/day. Add one marker line on 4% of bodies at about 1 min each, about 108 s/day. Total **about 2 min/day**.
  - 2 < 18, so M1 passes.

**M2, not demonstrated (shape A, the yield).** For each `Carry: <GROUP>` marker in the body, require the group's roster entry at the round ref to hold a carry naming the item id (carry_audit's printed `item <id>`) or the source topic. That is the mechanical form of fix-review step 10's "open it". It would have refused every A row whose verdict says "only in the PR body". It needs fixers to write carries with the item id, which changes what a seat must do. That makes it policy (finding-propagation.md), so it is the owner's call and this probe does not build it. Its cost test, against shape A at 14 blocks / 4.66 days × 84 min = **about 252 min/day**: the roster read is the same fetch `carry_line` already does, and the added time is under 1 s per run.

**Shape B (6)** is a set of distinct liveness rules: a done or absorbed group behind `#N`, a double destination, a marker outside finding sections, an after-edged consumer, and a batch that marks its own destinations done. Each is a candidate `Dests.check` arm. No barrier was found within the bound, so the owner is asked.

The WHY at `prepr.sh:974-978` misstates the class. M1's pull request (R10-PREPR-CAP) corrects it.

## Appendix: vcore.py (the enumerator)

```python
import re,sys,collections,datetime as dt
rows=[]
for l in open(sys.argv[1]):
    h,ct,ci,s=l.rstrip('\n').split('\t',3)
    m=re.match(r'verdict: #(\d+) Fix review: (\w+)(?: ([0-9a-f]{7,40}))?\s*(.*)',s)
    if not m: continue
    pr,word,sha,rest=m.groups(); cls=''
    if word=='blocked':
        cm=re.match(r'([A-Za-z0-9_.-]+)',rest); cls=cm.group(1).rstrip(':').lower() if cm else ''
    rows.append((int(ct),int(pr),word,sha or '',cls,s,h))
seen={}
for r in sorted(rows):
    k=(r[1],r[2],r[3],r[4])
    if k not in seen: seen[k]=r
V=list(seen.values())
T={'2838':dt.datetime(2026,10,26,4,40,21,tzinfo=dt.timezone.utc).timestamp(),
   '2853':dt.datetime(2026,10,28,3,16,58,tzinfo=dt.timezone.utc).timestamp()}
end=dt.datetime(2026,10,30,20,32,38,tzinfo=dt.timezone.utc).timestamp()
first=min(v[0] for v in V)
wins=[('pre-2838',first,T['2838']),('2838..2853',T['2838'],T['2853']),('post-2853',T['2853'],end),('post-2838',T['2838'],end)]
for lab,opened in [('all PRs',lambda n:True),('PRs numbered >2838',lambda n:n>2838)]:
  for name,a,b in wins:
    w=[v for v in V if a<=v[0]<b and opened(v[1])]; bl=[v for v in w if v[2]=='blocked']; c=[v for v in bl if v[4]=='carry-missing']
    print(lab,name,len(c),len(bl),len({v[1] for v in c}),len({v[1] for v in bl}),len({v[1] for v in w}))
```
