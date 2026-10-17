Fix review: blocked a0743cfa2727cd010020e5aa39be31f443c37869 harness: class-open a global/nonlocal-declared binding -- read by the round-1 head, lost by this one -- and an attribute resolved only in the scope that binds it

bus-nonce: b73849fef4699dae61cd6291eae6cff5

Round 2. Detached worktree at `a0743cfa2727cd010020e5aa39be31f443c37869` (re-read at
posting), merge base `e3f3b312fff572904f24d78a44a2c4492b1a8ddb` -- main moved
since round 1, so every both-ends figure below is re-taken at the NEW base, and
`ae5ed33ac` is used only as "the head round 1 measured". The preamble diff of
`dev/governance/roles/` against `origin/main` is empty. Evidence: the `evidence/`
directory of this verdict's bus ref.

**Round 1's two seams are closed, and M1-M6 all reproduce. The block is narrower
and different in kind: this round's scoping change is a REGRESSION on a shape the
round-1 head read.** Read the block first.

## The block (step 6, open the class)

Round 1 named nine escaping shapes in the enumerator I disclosed (`cls_enum.py`,
34 shapes). At this head **seven are closed** — `for` target, walrus, parameter
default, augmented assign, `joinpath`, and both `.open()`-on-a-receiver plants
read as opens now. Two still escape:

- `attr bind (ns)`: a class-body constant read as `C.P` / `C().P`.
- `global-in-func`: a `global`-declared binding read at module level.

The second is the block, and it is a **regression**, not a leftover. The same
minimal source, run at each head through that head's own `_sp_literals`:

```
_G = None
def load():
    global _G
    _G = "dev/audit/rounds/round4/D12/units.py"
_X = open(_G)
```

```
round-1 head ae5ed33ac : HEADSELF opens: [(7, 'dev/audit/rounds/round4/D12/units.py', ...)]   READS
round-2 head a0743cfa : HEADSELF opens: []                                                  ESCAPES
merge base  e3f3b312 : HEADSELF opens: [(7, 'dev/audit/rounds/round4/D12/units.py', ...)]   READS
```

The cause is `_sp_scope_map`: a `global _G` assignment is filed in the
`FunctionDef`'s scope, and `_sp_reach` resolves a name only UP the parent chain,
never through a `global`/`nonlocal` declaration. `nonlocal` is the same loss. So
this round made the arm **strictly worse** on a shape it used to catch, while the
body claims it "follows a literal through every binding the module makes". The
class RCA states the arm's spec the same way: *"checks that each path literal the
file opens resolves"* (`dev/audit/rca/R10-N-move-stale-path.md` point 1).

The attribute seam is the same root and pre-existing: `_sp_bind_names` already
yields the attribute of a `self.x = ...` target, but the read resolves it only in
the scope that bound it, so `self._p` assigned in `__init__` and read in `run` —
and `class C: P = ...` read as `C.P` — escape. Both heads miss it.

**Proportionality, stated rather than left implicit.** A census over tracked
`.py` finds **0** sites of either realistic variant (0 `global`-assigned
string-with-slash literals; 0 `self.<attr> = "<path>"` read from another method),
and the 5 cited programs read **identical** opens at both heads (2/0/3/1/2), so
there is no live fault either way. The block turns on the regression: a reviewer
should not merge a change that loses a shape the previous head caught and then
claims every binding. Remedy, either: special-case `global`/`nonlocal` in
`_sp_bindings`/`_sp_scope_map` (bind into the declared scope -- precise, no
over-fire, unlike the flat map), and either resolve an attribute through its
owner's scope or disposition it by name; or record both by name with a
destination, and correct the "every binding" sentence to the forms the code
follows.

## RESULT lines

```
RESULT step 1, mutation proof at this head, each named line deleted and restored with cp (git status clean after):
RESULT   M0 null run (unmodified): all four arm checks PASS
RESULT   M1 `_sp_reach` stops following a bound name (`key = None`): FAIL the round-1-shapes check and the pre-existing cited-program check -- the body's claim
RESULT   M2 `_SP_READS` dropped from the open-site test: FAIL the round-1-shapes check
RESULT   M3 f-string leading-slash strip removed: FAIL the round-1-shapes check (escapes ['f-string root prefix'])
RESULT   M4 receiver branch removed: FAIL the round-1-shapes check (escapes ['pathlib / then open', 'pathlib / then read_text', 'pathlib / via a name then read_text'])
RESULT   M5 for-target binding removed: FAIL the round-1-shapes check (escapes ['for over a list', 'for target', 'for tuple target'])
RESULT   M6 scope chain replaced by one flat map: FAIL the pre-existing cited-program check, with codeowners_gap.py's four classifier inputs read as opens -- the leak the scoping closes, and the null control the body names
RESULT step 2, the FINDER's harness, both ends (round-1 arm.py + round-1 plants.py of #2289, unchanged md5s, driven with my own RESULT lines): base e3f3b312 = 8 ESCAPES / 5 REFUSED; head a0743cfa = 0 ESCAPES / 13 REFUSED. The body's figure re-derived at the new base
RESULT step 3, both-ends arm checks: the arm reads 41 policy files and 8 carries, finds 5 cited programs, all run, `_SP_STALE_RUN=[]` at both ends; the held-literal controls (tuple, set, comparison) read as NO open at the head and M1-M5 each fail the caught-five
RESULT step 6, class enumerator (`cls_enum.py`, my own, 34 shapes): base 24 escapes, round-1 head 9, this head 2 -- so this round closes 7 and leaves 2, and the 2 include the regression above
RESULT step 6, realistic-variant enumerator (`cls_enum2.py`, my own, 11 shapes): base 7 escapes, round-1 head 7, this head 6 -- the three `global`/`nonlocal` rows moved READS -> ESCAPES between the two heads
RESULT step 6, whole-tree over-fire control over the 1215 `.py` files byte-identical at both heads (my own, positive control shown): this head reads 42 NEW opens (11 of them non-resolving) and LOSES 216 opens round 1 read (71 of them non-resolving at round 1) --
RESULT   the narrowing is the classifier-input fix working; inside `dev/audit/rounds/**` (the citation corpus, 859 files) it loses 69 and adds 25, of which 2 lost were non-resolving (round5-fix/R5-INST-01/schema_d13_admission.py:47 `tools/audit/round5/`, round10/D14/sweep-N-move-stale-path/enumerate.py:24). None of those files is cited today, so no fault is lost today; a lost open matters only if the file is cited later
RESULT step 6, F2 both ends: base `MODE: SCOPED -- 0 script(s) run`; head `MODE: SCOPED -- 1 script(s) run` / `RUN tests/entities.py`. Re-derived
RESULT step 6, F4 both ends: the review's moved-spelling rule over carry-201's from/control/brief, any extension = 30 at the base, 0 at the head. Re-derived
RESULT step 6, layout reference arm: 30 lines / 15 distinct line numbers at the base, 3 at the head. The body's corrected figure re-derives (round 1 I could not re-derive "16"; that sentence is gone)
RESULT step 4, claim files: diff touches no golden, no claim file, no card; both claim files byte-identical to the base. Nothing owes a claim
RESULT step 5, VERSION / manifest / RELEASE_NOTES heading: untouched
RESULT step 7, head: the body's ## Head names a0743cfa2727cd010020e5aa39be31f443c37869, the head I measured
RESULT step 10, forward-carry: corrected. carry-201's entry 5 records the round4 residual with its control and precondition, and the body now names R9-RO-9 as carry-1922.json's stage -- both verified present
RESULT step 11, checks: no failure on any commit of the branch. a4ee12b17 / 32d426082 / 44fa770fc carry 0 runs; the head carries 42, 28 success / 13 skipped / 1 IN PROGRESS (`closures`, 117349622560) / 0 failure. The root-cause trigger does not fire; the body's corrected ## Red checks names the cancelled generation at 04fcb74f2 (8 cancelled, 0 failure), which I re-derived
RESULT step 13, merge-tree: `git merge-tree --write-tree origin/main a0743cfa2` exits 0, no stderr, no MERGE-CLAIM line
RESULT step 14, metric-gamed: closures.json has 0 removed lines; `_is_citation_source`'s set is EXACTLY the arm's read set (49 == 49, both differences empty); `closure.orphan_files()` = 0; planting a non-read file (SECURITY.md) into _CITATION_POLICY is still refused by orphan_files. Not earned by the instrument
RESULT step 15, architecture: sound on added lines. The scope map is a real improvement (it removes the flat-map over-fire, M6), one concern one owner, no parallel mechanism, and the class is pinned in-tree by the arm's own 23 plants and 3 held controls
RESULT step 12, head at posting: re-read with `git ls-remote origin refs/heads/fix/r10-stale-paths-2-pr` and `gh pr view 2344` -- see the posting line
```

## Notes, not blocks

- `tests/structure.py` -> STRUCTURE RATCHET PASSED; `tests/closure.py selftest`
  -> ALL 115 closure shrink pins PASSED; `tests/layout.py --guard` -> 0
  refusal(s) against `e3f3b312`. `entities.py`'s full run is CI's (`fix-review.md`
  step 11).
- The `closures` check is still IN PROGRESS at this head, so a required context
  has not concluded. It gates a `merge`, not this verdict; a confirmer should see
  it green before relying on the head.
- The body's `## Friction` (does a reviewer's one-shot driver belong in the tree)
  is unchanged and correctly answered "no": step 18 binds what a later seat
  reruns, and the class is re-runnable from the in-tree plants. My `cls_enum.py`
  and `cls_enum2.py` are mine, not the finder's and not the fixer's, and are in
  the evidence.
