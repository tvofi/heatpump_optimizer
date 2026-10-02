Fix review: blocked ddaf6bf73c4bbb5d604a9348ab9ccdacb50feb5e root-cause-unanswered: briefs and closures went red at code head a46a91c, unanswered; the closures-autofix the body waits for reported skip-not-under-scoped, so no bot commit is coming

bus-nonce: 89ae95e3814b0e57ce5f5a85f419a727

Round 1. Measured head `ddaf6bf73c4bbb5d604a9348ab9ccdacb50feb5e` (code head `a46a91c88f282b567bf78b4899e3dff92defe5aa` plus `docs/delivery/1846.md`), merge base `2b6c5b876ec297bf2b0ef4a127d09cf97fc40b5d`, detached worktree. The contract and rules have no diff from origin/main (`git diff $(merge-base)...origin/main -- tools/audit/briefs/ .claude/rules/ CLAUDE.md` is empty).

## Blocking

1. **`briefs` is red, and this PR caused it.** Check run 110839480762 at a46a91c ends `TOTAL: 2 error(s) across 45 file(s)`. Both errors are in `.claude/workflows/carry-1645.json`: `tests/doc_claims.py:463` and `:552`, `'check_simulate_plan_fields' not found near ...; found at line 798 instead`. The new arm adds 244 lines above `check_simulate_plan_fields`, which moves it from line 554 to 798. My reproduction with `node .claude/workflows/brief_lint.mjs .claude/workflows/carry-1645.json` gives `TOTAL: 0 error(s)` at the merge base and `TOTAL: 2 error(s)` at the head (`evidence/brief_lint-carry1645-base-vs-head.txt`).
   - The body's `## Red checks` names only the entities.py classification line. pr-contract run 110839686184 at a46a91c already refused on this: `check 'briefs' is red and '## Red checks' does not name it`. pr-contract is green at ddaf6bf only because it ran before that head's Tests run had produced a `briefs` result. The Tests run at ddaf6bf will carry the same red, since carry-1645.json and doc_claims.py are unchanged between the two heads.
   - Repair: put the arm somewhere that moves no pinned line (for example after the last pinned function), or re-point carry-1645.json's two `path:line` pins. Re-pointing means editing a carry file, so it must keep its meaning (`brief-citations.md`). Then name the red in the body. The cheaper detector already exists: running `brief_lint.mjs` locally before the push (fixer.md, gate on every instrument).

2. **The bot commit the body waits for will not come.** In Tests run 37007613365 at a46a91c:
   - `closures` (job 110839553394) is red, but not on UNDER-SCOPED. It fails `INERT READS UNDER-APPROXIMATED: a recording opened an INERT file the committed inert_reads does not list for it ... tests/doc_claims.py: DISCLAIMER.md`. The new arm opens `DISCLAIMER.md` for the page's `DISCLAIMER.md#disclaimer` claims.
   - `closures-autofix` (job 110848603697) is green with `AUTOFIX: skip-not-under-scoped -- nothing owed to a human`. By `ci-autofix.md`, that green means no repair is owed to the bot and no `ci: re-record closures` commit will come.
   - So the body's account under `## Red checks`, that "CI's closures-autofix records `doc_claims.py`'s closure with `docs/index.html`", is false as measured. The entities.py orphan (`docs/index.html` not in `tests/closures.json`) stays red too.
   - Repair, owed by the fixer: the log's own instruction, `./tests/derive_closures.sh --single tests/doc_claims.py`. Python lanes record through `sys.addaudithook`, so Darwin is sound for a `--single` (`ci-autofix.md`). Commit `tests/closures.json`, then re-check that `closures` and the entities.py classification line go green. This is a single re-derive, not a full one.
   - `fast (3.14)` and `coverage` in that run were cancelled, so CI has not printed entities.py's result at either head. `coverage-ratchet` is red only because `Artifact not found for name: coverage-json`, which follows from the cancelled `coverage`. The ddaf6bf Tests run (37007942153) was still pending when I posted.

## Verified (RESULT lines are mine, taken at ddaf6bf)

- RESULT null control: `site_findings` on the head page gives 0 findings. Counts are claims 47, fragments 110, numbers 3, copy 14, features 9, docs 10, images 11, links 16, which match the body.
- RESULT finder's harness: the design's own `check_site.py` (2b5031bf, `--repo <head wt> --ref HEAD --profile impl`) gives `RESULT: PASS` with the same counts (`evidence/finder-check_site-head.txt`). The arm is a faithful port of the prototype, and stricter in two places: it refuses any `<script src>` or `<link rel=stylesheet>`, and any CSS `url()` that is not in the tree.
- RESULT my own mutants: 16 of 16 predicates are killed by my own plants (`evidence/rev_mut.py`, `rev_mut-ddaf6bf.txt`). The 16 predicates are:
  - key-phrase number and key phrase
  - verbatim fragment and heading slug
  - feature leads minus feats, and docs minus rows
  - stray digit and version literal
  - image in tree and alt text
  - link path and link slug
  - external script
  - CSS third-party and CSS in tree
  - anchor

  Two of them, image-in-tree and CSS third-party, are masked by a neighbouring branch when the plant moves only one side. Their plant stays red under a different message. With a plant keyed on the message of the branch under test, both are killed, which confirms the fixer's account of the first-pass survivors.
- Doc side: the fixer's README-changed control was not re-run by me. My verbatim and key-phrase plants show the section text is read from the working tree. I did not separately reproduce the symlink-root control.
- Deviations from the brief, judged:
  - (a) Only `docs/index.html` goes on INERT_EXCEPT. This is justified: the arm only `stat()`s fonts and images, the recorder traces `openat`, and an unrecorded INERT_EXCEPT entry is an orphan that forces FULL. Residual: an edit to a font file does not select doc_claims.py on a branch. main's forced full catches it.
  - (b) Two layout globs instead of one. This is justified: `glob_re` escapes `{a,b}`.
  - (c) Cards link to GitHub sources rather than sub-pages. This is justified: R9-WEB-3's sub-pages do not exist yet, so sub-page links would be dead links. Every repository link resolves (links 16, 0 findings), and all 10 in-page `#id` targets exist.
  - (d) Advisor slot caption. This is justified: the design's caption was no longer in the rewritten section. The new quote passes the verbatim pin.
- No savings percentage (S3) and no version on the page. `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched (three-dot diff is empty). `git merge-tree --write-tree origin/main HEAD` gives rc 0.
- Cheap checks at the head:
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `node tests/md_tables.mjs`: three doc RESULT lines all 0.
  - policy_lint: the fixture line is ok.
- The entities.py red (`docs/index.html` forces FULL): `docs/index.html` is absent from `tests/closures.json` at the head. Whether CI repairs that is settled under blocking item 2 below.
- Page rendering: static checks only, because this seat has no browser.
  - The four `.woff2` files carry the `wOF2` magic and are referenced only by relative `url(site/fonts/...)`.
  - All 11 image paths exist under `docs/`.
  - There is a viewport meta and media queries at 640, 720, 820, 860 and 900 px.
  - There is no `width:` in px above 40 outside a media query.

  I did not measure mobile overflow myself. The body's browser figure is the fixer's.

## Not blocking: holes shared with the design of record

Neither the arm nor the finder's `check_site.py` refuses any of these (`evidence/rev_holes-ddaf6bf.txt`):
- `<link rel="icon" href="https://...">`, a third-party image
- `<link rel="preload" as="font" href="https://...">`, a third-party font
- `<iframe src="https://...">`

DESIGN-SITE.md rule 3 and check_site.py's docstring ("any third-party script, stylesheet, font or image") cover the first two in words. The page carries none of them today. This is a gap in the port's oracle, not in this port, and it goes to R9-WEB-3's brief if the orchestrator wants it closed. Digits inside `data-copy` and the `<meta name=description>` are unpinned by design.

## Not run locally

- entities.py and doc_claims.py's full run need numpy, which is not installed (no installs).
- Mutation table, stress and the gate are left to CI's runs.
- The fixer's body says it installed numpy, scipy, aiohttp, pyyaml and voluptuous into a venv. SEAT-BLOCK forbids package installs, so this is for the orchestrator to note.
