Fix review: blocked ae5ed33ac8cfd8fbc62ed131ca28946c8858e5dc harness: class-open a path literal opened by a for-target bind, and by .open() on a /-join receiver -- two members of the rule the body names that _sp_literals still does not read

bus-nonce: c0cf2f4718f4040735a6fb7da59c9503

Round 1. Reviewer seat, detached worktree at `ae5ed33ac8cfd8fbc62ed131ca28946c8858e5dc`
(re-read at posting time below), merge base `92accb2cff702c910d33ee1a276d38f5b482061c`,
seat venv python 3.14.7. The preamble diff of `dev/governance/roles/` against
`origin/main` is empty, so this contract is current. Evidence: the `evidence/`
directory of this verdict's bus ref.

**Everything in the body re-derives except one figure and the class.** Steps 1-5,
7-15 pass; step 6 is the block. Read the block first; the RESULT lines below are
its support.

## The block (step 6, open the class)

The body names the fix's rule: *"`_sp_literals` now follows a literal through
every binding, join, dict subscript, f-string and read site"*. `_sp_bindings`'
own docstring says *"for every binding the module makes"*. The class RCA the
group's own countermeasure comes from — `dev/audit/rca/R10-N-move-stale-path.md`,
point 1 — states the same rule as the arm's spec: *"checks that each path literal
the file opens resolves"*. I ran that rule as an enumerator over the class
(`cls_enum.py`, my own script, not the finder's and not the fixer's; 34 shapes,
the round-1 plant list as its population plus 21 more).

At this head **9 of the 34 still escape**, and two of them are plainly inside the
named rule and neither in the diff nor dispositioned in the body:

1. **A `for` target holding the literal — a binding.** `_sp_bindings` follows a
   plain assignment, an annotated assignment and a tuple/list unpack; a `For`
   target is a binding the module makes and is not followed.
   `for _P in (<retired>,): open(_P)` reads as HELD, not as an open.
2. **`.open()` on a receiver — a read site.** The fix's own comment on
   `_SP_READS` says *"the method is an open site of its own"*, and the set is
   `{"read_text", "read_bytes"}`. `open` cannot be added to it as written: `open`
   is already in `_SP_OPENS`, and that branch reads only the call's *arguments*,
   so an attribute call `.open()` takes the args-only branch and the receiver is
   never traversed. `(Path('.') / <retired>).open()` and
   `_P = Path('.') / <retired>; _P.open()` both escape — the exact structure of
   the two round-1 plants `_SP_READS` was added for, with `.open()` in place of
   `.read_text()`. (`Path(<retired>).open()` happens to be caught, but only
   because the inner `Path(...)` call is an open — by accident, not by design.)

Neither is hypothetical for this repository. A `for` target over path literals
occurs at least 15 times in tracked `.py` — including in the corpus this arm
probes: `dev/audit/rounds/round3/D11/mechanisms.py:242`
(`for f in ("tests/golden/claimed_drift.txt", "tests/golden/card_claimed_drift.txt")`),
`dev/audit/rounds/round3/D6/claims.py:80`, `dev/audit/round9/D14/s1/p1_store.py:71`,
`dev/audit/round10/D15/s1/intake.py:35`,
`dev/audit/round8/evidence/D11/v1_owner_flip.py:135` (a tuple of
`.claude/workflows/` paths, with `.claude/workflows/policy_lint.mjs` two lines
below at a path that has moved). `.open()` on a pathlib receiver is live too:
`tests/layout.py:689` reads a file that way.

**I am not claiming a live fault today.** I widened the reader to the missing
shapes and re-ran it over every cited program at this head
(`widened.py`, my own; its positive control reads
`_P = Path(".") / "dev/nope_xyz/file.py"; _X = _P.open()`, which the arm does not
and the widened reader does). Result: **0 live faults** — the 5 cited programs
name no path through these shapes. The seams are latent, exactly as the 8 the
fix closes were latent. That is why the remedy is cheap either way.

**Remedy.** Either follow the two shapes — `open` needs its own attribute branch
or to leave `_SP_OPENS`, and `_sp_bindings` needs `For`/`NamedExpr` — or
disposition them by name in the body, with a destination under
`finding-propagation.md` (`carry-1922.json`/R9-RO-9 is *not* a destination for a
shape gap; a new issue under class `N-move-stale-path` is). The remaining 7 —
walrus, function-parameter default, class attribute, `+=`, and the
`joinpath`-without-a-read case — are the same binding family and can ride the
same disposition; `pathlib joinpath` alone opens nothing, so I do not count it as
a seam. Then correct the "every binding" claim to the forms the code follows.

## RESULT lines

```
RESULT step 1, mutation proof re-run at this head with the finder's driver, the named line deleted each time and restored with cp (worktree `git status` clean after every one):
RESULT   M0 null run (unmodified): all four arm checks PASS
RESULT   M1 `_sp_reach` stops following a bound name: FAIL both the round-1-shapes check (escapes ['annotated assign', 'dict value then subscript', 'pathlib / via a name then read_text', 'tuple-unpack assign', 'two-hop alias', ...]) and the pre-existing cited-program check -- the body's claim
RESULT   M2 `_SP_READS` branch deleted: FAIL the round-1-shapes check (escapes ['pathlib / then read_text', 'pathlib / via a name then read_text'])
RESULT   M3 f-string leading-slash strip removed: FAIL the round-1-shapes check (escapes ['f-string root prefix'])
RESULT   M4a `_is_citation_source` off the is_inert override: FAIL the sources-select check (49 sources back INERT)
RESULT   M4b closures.json reverted to the merge base: FAIL the sources-select check (all 49 sources read `selecting no script or the whole suite`)
RESULT step 3, the null control is load-bearing (my own ablation M5, not claimed by the body): making every string constant read as an open FAILs the round-1-shapes check outright (held-literal clause empty in the detail) and, in the two checks beside it, fires 4 false faults on codeowners_gap.py's classifier inputs -- which is the design choice the body's Rejected alternatives names
RESULT step 2, the FINDER's harness, both ends (round-1 `arm.py` + round-1 `plants.py` of #2289, md5 08964449.../754a7b9a..., run with ARM_EXTRA unset and set): base 92accb2cf = 8 ESCAPES / 5 REFUSED; head ae5ed33ac = 0 ESCAPES / 13 REFUSED. The body's figure re-derived exactly, with my own RESULT lines
RESULT step 6, class enumeration (cls_enum.py, my own): base 24 of 34 shapes escape, head 9 of 34 -- so the fix closes 15 and leaves 9; the 9 are the block above
RESULT step 6, live-seam test (widened.py, my own): 0 unresolving opens among the 5 cited programs through the missing shapes; positive control fires, so the zero is the instrument working, not a vacuous pass
RESULT step 6, class rule: the body names the rule; the class RCA (dev/audit/rca/R10-N-move-stale-path.md point 1) states the same one; so `class-rule-missing` does not apply -- a rule is named and it returns seams the diff does not close
RESULT step 6, F2 both ends: `tests/closure.py select --files dev/programme/carries/carry-201.json` = `MODE: SCOPED -- 0 script(s) run` at the merge base, `MODE: SCOPED -- 1 script(s) run` / `RUN tests/entities.py` at the head. Re-derived
RESULT step 6, F4 both ends: the review's moved-spelling rule over carry-201's from/control/brief, `locate(w) != w and not isfile(w) and isfile(locate(w))` with any extension = 30 at the merge base, 0 at the head. The body's 30/0 re-derived
RESULT step 6, layout reference arm: `python3 tests/layout.py --report --verbose` against `dev/programme/carries/carry-201.json` = 30 lines (15 distinct line numbers) at the merge base, 3 at the head (lines 56-58, all `tools/audit/round4/`). The head figure re-derives; the body says 16 at the merge base and I cannot re-derive 16 --
RESULT   see "Not verified" below
RESULT step 4, claim files: the diff touches no golden, no claim file and no card; both claim files are byte-identical to the merge base. Nothing owes a claim
RESULT step 5, VERSION / the manifest version / the RELEASE_NOTES heading: untouched (the diff is 5 files, none of them)
RESULT step 3, both-ends floors: the arm still reads 41 policy files and 8 carries, finds 5 cited programs, all of which run, `_SP_STALE_RUN=[]` at both ends
RESULT step 7, head: the body's ## Head names ae5ed33ac8cfd8fbc62ed131ca28946c8858e5dc, the head I measured and re-read at posting time
RESULT step 9, harness provenance: the finding has no committed harness -- the round-1 `arm.py`/`plants.py` live only in #2289's verdict evidence. The fixer discloses it as the fix review's own and does not claim it as the finder's; the fix's own check plants the 13 shapes in-tree, so the class is pinned in the tree even though the driver is not. Not a block
RESULT step 10, forward-carry: the residual (3 carry-201 lines citing tools/audit/round4/, whose two files still live there) IS recorded with its control and its precondition, in carry-201's entry 5 `brief` ("Constraint on preparing the NEXT round's baseline") and in the entry's `control`. Present, so not `carry-missing`
RESULT   correction: the body says that entry "names them and the R9-RO-9 that ends the pin". It names them; R9-RO-9 is not in carry-201.json at all -- it is the stage of dev/programme/carries/carry-1922.json, which carries the move of tools/audit/round4/D11/governance_cost.py. The destination exists; the body's sentence points at the wrong file
RESULT step 11, checks: no check went red on any commit of the branch. Head ae5ed33ac: 45 check-runs, 30 success / 15 skipped, 0 failure/cancelled. The code head 04fcb74f2: 45 runs, 24 success / 12 skipped / 1 neutral / 8 CANCELLED, 0 failure -- so the root-cause trigger does not fire --
RESULT   correction: the body's reason is wrong. It says "Four commits were made locally and none was pushed for CI before this handoff"; 04fcb74f2 carries 45 check-runs. The conclusion ("Red checks: none") is right, the reason is not
RESULT step 14, metric-gamed: not earned by the instrument. The closures.json movement is 0 removals and additions to tests/entities.py only, at 4 hunks; no other script's recorded closure holds any of the 49 sources; `_is_citation_source`'s set is EXACTLY the arm's read set (49 == 49, both set differences empty); `closure.orphan_files()` = 0 at the head. Planted the diff's own kind of move with nothing improved -- naming a file the arm does not read (SECURITY.md) in _CITATION_POLICY makes it non-inert and `orphan_files()` returns exactly it, so the movement cannot be faked; `select` then reads `full`. `tests/deployment_shape.py` passes at both ends
RESULT step 13, merge-tree: `git merge-tree --write-tree origin/main ae5ed33ac` exits 0, no stderr, no MERGE-CLAIM line. The ledger driver is not invoked because nothing conflicts
RESULT step 15, architecture: sound on added lines. One concern one owner (the arm's shape reader stays in tests/entities.py beside the arm; the INERT carve-out stays in closure.py, where INERT lives); no parallel mechanism (the worktree read replaces the index read rather than sitting beside it, and `_sp_source` is a one-line helper); the class is pinned in-tree by the 13 planted shapes so a later seat can re-run the class without the out-of-tree driver
RESULT step 12, head at posting: re-read with `git ls-remote origin refs/heads/fix/r10-stale-paths-2-pr` and `gh pr view 2344 --json headRefOid` -- see the posting line below
```

## Not verified

- The layout reference-arm figure **"16 lines at the merge base"** does not
  re-derive: I read 30 lines / 15 distinct line numbers for
  `dev/programme/carries/carry-201.json` at `92accb2cf` (evidence
  `layout_base.txt`). 30 is the whole file's reference-arm count and equals the
  F4 probe's count; 15 is the distinct line numbers. I could not find a rule
  yielding 16. The head figure (3) re-derives, and the fix's effect does not turn
  on it, so this is a note and not the block.
- Body figures I took as CI's or did not re-run: `entities.py`'s full "ALL 2333
  ENTITY CHECKS PASSED" and `harness_headers.py`'s 109 (heavy runs are CI's,
  `fix-review.md` step 11). I did re-run the cheap ones:
  `tests/structure.py` -> STRUCTURE RATCHET PASSED;
  `tests/closure.py selftest` -> ALL 115 closure shrink pins PASSED;
  `tests/layout.py --guard` -> 0 refusal(s) against 92accb2cf.

## Notes, not blocks

- The body's `## Friction` asks whether a reviewer's one-shot driver belongs in
  the tree (`fixer.md` 18). It does not, on this reading: 18 binds what a *later
  round or seat reruns*, and the class is re-runnable from the in-tree plants.
  The friction is real but its resolution is "no", which the body has already
  recorded.
- `dev/programme/delivery/2344.md` is the row-only commit on top of the authored
  head, so the head's own runs and the code head's are the same tree for every
  path this verdict measures.
