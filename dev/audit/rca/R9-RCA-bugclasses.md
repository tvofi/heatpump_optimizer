# RCA-bugclasses: every root-cause PR appends after the same last `_rca` entry

The root-cause seat for the register's own merge conflicts. Two root-cause pull
requests in flight each append an `_rca` entry to
`dev/audit/config/bugclasses.json` after the same last entry; whichever merges
second goes `DIRTY` and needs a seat to re-merge main. It runs beside no fix
(`dev/governance/roles/root-cause.md`). Base measured: `origin/main` at
`8d7903e6` (2026-10-07). Raw evidence is under `dev/audit/rca/bugclasses/`.

**Trigger.** Recurrence: four hand-resolved merges on one file in one day. This
is process friction, not an audit class, so the cost test decides and a refusal
would have been legal.

## 1. The count, reproduced

`scan.sh` replays, with `git merge-tree --write-tree`, every merge commit since
2026-09-23 (the day the register was created) in which both parents changed the
register, at either path (`tools/audit/bugclasses.json` until `#1917` moved it).
I ran it over every merge reachable from the 268 `origin/*` refs, not only
`main`, so branches still open count too. That is 27 merges (`merges.txt`). Four
conflicted on the register, all on 2026-10-07:

| merge | branch, PR | main merge it took | entry pair |
|---|---|---|---|
| `82af801a` 14:49 | `fix/r9-rca-1990`, #2012 | #2013, 14:23 | R9-RCA-1990 / R9-RCA-1985 |
| `e62b8b63` 14:48 | `handoff/r9-rca-stress-recording`, #2018 | #2013, 14:23 | stress-recording / 1985 |
| `af62b2b8` 14:48 | `handoff/r9-rca-2004`, #2014 | #2013, 14:23 | R9-RCA-2004 / 1985 |
| `dfe2bb79` 21:27 | `fix/r9-rca-2004`, #2014 | #1987, 21:01 | R9-RCA-2004 / stress-recording |

The other 23 merged cleanly. All four conflict hunks sit at the tail of `_rca`,
which is the file's last key: each side turns the last entry's closing `}` into
`},` and adds a different entry after it.

The brief said there were several earlier instances in this round. I did not
find any. No merge reachable from any remote ref conflicted on the register
before 2026-10-07. A conflict resolved by recreating a branch would leave no
merge commit, so this count is a floor. It is still the only number I measured.

**Rate.** The rule that every RCA cites an in-tree `_rca` entry landed in
`606ad289` (2026-10-02). Since then, five pull requests have added an entry:
#1875, #2013, #2012 and #2018 on `main`, and #2014, which is open. Three of
those five conflicted. Before 2026-10-07 no two of them were open at the same
time. On 2026-10-07 four root-cause seats ran at once.

## 2. Cause

The register is one JSON object, and every new `_rca` key goes at its end. A
line merge treats two different insertions at the same point as a conflict,
even when the keys are disjoint. This is the same shape the ledger driver was
built for: `tools/merge/ledger_merge.py` already merges
`tests/{mutation,structure}_budgets.json` and `tests/closures.json` key by key,
because every fix branch re-records those files (60 conflicts to 0, its own
replay). It was never routed to the register.

## 3. Process state: (d)

The process existed and was sound. `.gitattributes` routes each file that many
branches write at the same place to a driver: the claim files to `claimnotes`
and the three ledgers to `ledgermerge`. Its precondition was the set of files
that every branch of some kind writes. That set grew on 2026-10-02, when
`defect-root-cause.md` ("cited by `rca` in `bugclasses.json`", `606ad289`) made
every root-cause PR a writer of the register. Nothing in the routing process
noticed the change. A firmer instruction to resolve conflicts carefully would
treat this as (b). The resolutions were obeyed and correct: the driver
reproduces each of them, as section 5 shows.

## 4. Cost test

- **cost(defect)**: main's conflicting merge landed at 14:23 and at 21:01. The
  resolutions were committed at 14:48 and 14:49, and at 21:27. That is **25 to
  26 minutes per instance**, waiting for a seat to merge main by hand. Each
  resolution also moved the head, so the PR needed a new review verdict at that
  head and a CI rerun. A CI rerun follows any main merge, so the driver does not
  remove it. The final heads measured 6 minutes (`5efb428d`) and 45 minutes
  (`189b57b6`, `e476f931`) for Tests.
- **P(recurrence)**: 3 of 5 entry-adding PRs since the rule existed. The rate
  is about 1 for any two RCA PRs open at the same time. Today that happened 4
  times in one day.
- **cost(countermeasure, recurring)**: the driver runs only when both sides
  changed the register. It took 0.08 s on the real `dfe2bb79` inputs, measured
  3 times. The self-test that `tests/entities.py` already runs grew by 4 checks.
  The whole self-test takes 0.25 s.

0.08 s against 25 minutes times a probability near 1 for each concurrent pair.
The countermeasure is built.

**What the driver does not do.** GitHub never runs a merge driver, so the
second PR still shows `DIRTY` (`claim-files.md`). The difference is who clears
it. The orchestrator's merge train recarries with `remerge_main.sh`, which runs
`git merge origin/main` in a clone where `ledgermerge` is installed (verified:
`git config --get merge.ledgermerge.driver` in the programme clone). That merge
is now clean, so it is "an automatic merge, no resolution", and no fixer seat or
review round is needed. Git reads `.gitattributes` from the branch's own tree.
So the routing works only for branches cut from `main` after this lands. A
branch cut earlier conflicts once more.

## 5. Countermeasure, shown working

`.gitattributes` routes `dev/audit/config/bugclasses.json` to `ledgermerge`.
`ledger_merge.py` gives it a `"refuse"` mode with two rules:

- `_rca` is a table of records, so it merges entry by entry. An entry that
  both sides rewrote differently still refuses, under the existing depth-2
  record rule.
- A class record (`P1`, `N-*` and the rest) refuses when both sides changed
  it. If two branches each add one instance, both raise `total` to the same
  number, the merge would accept it, and the count would be wrong.

The writer keeps raw non-ASCII, so that text is written back raw.

**Perturbation.** `replay.sh` re-runs all 27 merges with a real `git merge` in a
standalone clone, routing the register to a copy of the driver through
`.git/info/attributes`. The `without` arm routes nothing (`without.log`):

    ARM=without merges=27 conflicted=4 merged-equal-to-recorded=23 merged-differing=0
    ARM=with merges=27 conflicted=0 merged-equal-to-recorded=27 merged-differing=0

In each of the four conflicts, the driver's merged JSON equals the resolution
the seat committed. Two of them differ in bytes only because the two new
entries are in the other order.

**Null control.** The 23 merges that were already clean give the same JSON with
the driver, and 23 of those 25 bytes-equal lines in `with.log` come from them.
The driver did not pass by skipping. It resolved 16 merges itself. In 6 others
it fell back to git's text merge, which was clean: before the register's v2
format, a side did not match the writer's format. Five merges never invoked it.
The self-test's refusal checks prove that a rewrite of the same entry, or a
class both sides added to, still conflicts.

**Mutation.** Each of these four mutations turns `ledger_merge.py --self-test`
red:

- removing the class-record refusal;
- `ensure_ascii=True`;
- routing the register as `"sum"`;
- emptying `RAW`.

Removing the `.gitattributes` line fails "routes every ledger to the driver".

## 5a. How far the class reaches

`conflicts_since_0920.tsv` replays every merge since 2026-09-20, across all
refs, and lists each file that conflicted (217 file-conflicts). The register
had 4 of them. Files ahead of it:

- claim files: 31. They already have `claimnotes`, and `merge-tree` does not
  load it in this replay.
- `tests/features.py`: 16.
- `tests/entities.py`: 11.
- round-4 D6 claims: 10.

These are code or prose, which a JSON driver cannot merge. Whether the
`entities.py` conflicts are tail-append conflicts like this one is **not
established**. That is the next candidate if the cost recurs. The delivery
record already uses one file per row (`dev/programme/delivery/<N>.md`), which
is the other cure for this shape. For the register I rejected it: 9 scripts read
`bugclasses.json` as one file.

## 6. Recorded refusals

- I did not build a check that notices a newly hot append file, the generic
  (d) countermeasure. The routing list is short, and both kinds of instance so
  far showed up within one day of the writer change. A check would cost a
  history replay on every run.
- I did not split the register into one file per entry. That cost is in 5a.
