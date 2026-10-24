R10-MERGE-SUBJECT-HARDEN: the merge-subject guard in `tools/policy/agreement.mjs` (`mergeSubjectGuard`). It started from two findings in the #2423 review that were recorded there and not fixed. Three review rounds since have widened the second finding to the whole class of merge-call spellings. Part of #201. No issue is filed for this group yet; the orchestrator files and wires one.

1. **The title template accepted too much.** `TEMPLATE_SUBJECT`'s second arm was `/\(#\d+\)$/`, which is only an end anchor. It passed subjects the host's `<title> (#N)` template never writes: `(#8)` (no title), `x(#8)` (no space), ` x (#8)` and `x  (#8)` (an untrimmed title), `x (#08)` and `x (#0)` (not a pull-request number), and `x \t(#8)`. The arm is now `/^\S(?:.*\S)? \(#[1-9]\d*\)$/`: a trimmed, non-empty title, one space, then `(#N)` with N ≥ 1.
2. **The writer scan read one line.** `subjectWriters` tested `MERGE_CALL` and `SUBJECT_ARG` against single lines. It missed:
   - a `--subject` on a shell continuation line;
   - one later in an argv list split over lines;
   - a `commit_title` on a later line of a `merge_pull_request(` call.

   The live seam is `merge_train.py`'s own merge call, which spans two lines. The scan now reads each match's call extent (`callExtent`):
   - It starts at the innermost bracket left open before the match on its line, or at the line's start.
   - It ends where that bracket closes, or at the first line end that is outside the call's brackets and not escaped by `\`.
   - A blank line always ends it, and quoted text opens no bracket.
3. **The guard read one spelling of the call (rounds 2 and 3).** `MERGE_CALL` was the literal regex `\bgh pr merge\b|"pr", "merge"|...`, and `SUBJECT_ARG` listed `-t`, `-b` and `-F` only as standalone words. So a `--subject` passed unseen on any other spelling that gh's argv and the Python, JS and shell call forms accept for the same call:
   - quoted words (`gh pr "merge"`, `['gh', 'pr', 'merge']`);
   - a gh option between the words (`gh pr -R o/r merge`, `gh --repo o/r pr merge`);
   - a `\`-newline in any gap;
   - the program in a variable (`$GH pr merge`, `[GH, "pr", "merge"]`);
   - whitespace before an argv comma;
   - a short-flag cluster (`-mt x`, `-tx`, `-dmb x`, `-mF f`);
   - the GraphQL merge (`mergePullRequest` with `commitHeadline`).

   `MERGE_CALL` is now built from named parts, each defined once, so no gap or word can be narrowed alone:
   - `word`: a bare or quoted word ending at a non-word character;
   - `GAP`: whitespace, `\`-newline and argv commas;
   - `OPTION`/`OPTIONS`: gh options, with or without a value, in any gap;
   - `PROGRAM`: `gh` on any path, or a shell variable;
   - a quoted `pr`/`merge` arm, for an argv whose program is a variable;
   - the REST, MCP and GraphQL merges.

   `SUBJECT_ARG` keeps base's long flags and adds the short-cluster arm `-[mrsd]*[tbF]` and the GraphQL `commitHeadline`/`commitBody`. gh 2.98's `pr merge` flag table is the source: `-m -r -s -d` are the boolean method and branch flags; `-t -b -F` take the subject, the body and the body file; `-A` takes a value, so `-Amt...` sets no subject. I checked each cluster against gh's own parser: `-mtX`, `-dmt X`, `-mb X`, `-mF f` and `-t=X` each parse, and `--subj X` is refused as an unknown flag. Every spelling is pinned by its own `spelling:` probe (35 of them), and every part is mutated (R1 to R26).

Design choices, stated so a later seat does not read them as bugs:
- The title arm cannot tell a hand `--subject "<anything> (#N)"` from the host's template. It refuses only shapes the host never writes. The writer scan, not the shape, is what keeps hand subjects out.
- The extent is the call's own bracket group, not the statement around it. So a sibling argv in the same table (`gh_read.py`'s argv table) is not read as the merge call's. A first cut that joined whole bracketed statements raised exactly that false positive on the tree and was replaced.
- The spellings are parts, not a list. Round 2's repair added one alternation per reported spelling, and round 3 found the next spelling beside it. The parts compose: any gap may be a continuation, any word may be quoted, and an option may stand between any two words. So the class is closed by construction for everything a lexical scan can read. What it cannot read is dispositioned under Forward-carry.
- Parts no probe can decide were deleted, not pinned:
  - an option value's guard against eating `pr`/`merge` (backtracking already retries without the value);
  - the quoted arm's end-of-word check (a required closing quote already ends the word);
  - the program's own end-of-word check (a gap must follow it);
  - the program's opening quote (it moves the match start by one character on the same line);
  - round 2's `\r?` in the continuation: bash does not continue a backslash before CRLF, which round 3's review found and dispositioned as widening-only. A null probe now pins that a backslash before CRLF is not read as a continuation.

The `never --subject` line in `dev/governance/roles/orchestrator.md` belongs to RCA-FRICTION, not this group, and is untouched. The diff touches `tools/policy/agreement.mjs`, plus four audit harnesses under `dev/audit/harnesses/`:
- `r10_merge_subject_argv_seam.mjs`: the dismissed argv-across-expressions seam;
- `r10_merge_subject_mutants.py`: the mutation table;
- `r10_merge_subject_plants.sh`: the finder's harness under plants;
- `r10_merge_subject_census.mjs`: the tree census.

It also adds their four `tests/closures.json` entries. It changes no `VERSION`, manifest or `RELEASE_NOTES.md`.

## Head

`051266ebce49fb2d1b2948150a952ba1e317fd83` (this handoff) is `757631fa40c1192f459813238c85b1db2ad6f138` (round 2's handoff, reviewed in the PR as `455d7c2001fc7b94d39f9a0feb933894d9ca704d`), then a merge of origin/main `4a00a3f053c252b3bbf9f0e75ae36d27331f8ac3`, then the round-3 repair:
- `e25ac7dd7` and `005cb4eff`: the guard and its probes;
- `3f292e1db`, `c9b8dc1be`, `f479e08d6` and `051266ebc`: the harnesses;
- `6e7a8b29e` and `17ed8207c`: two `ci_predict.py --apply-inert` entries in `tests/closures.json`.

Merge base with origin/main is `4a00a3f053c252b3bbf9f0e75ae36d27331f8ac3`. The figures below were taken between `17ed8207c` and this head, or at the SHA they name. The commits after `17ed8207c` change only `dev/audit/harnesses/` (the census filter and two mutant rows), so `tools/policy/agreement.mjs` and every gate input are as at `17ed8207c`. The mutation table and the self-test ran at this head's harness and guard. `git diff 455d7c20 051266ebc --stat -- tools/policy/agreement.mjs` gives `1 file changed, 87 insertions(+), 6 deletions(-)`.

## Review response (review/2697, round 3, `blocked 455d7c20 class-open`, verdict on `probe/rev-2697-d80279e6`)

- **Block 1, R-first-gap** (a continuation between `gh` and `pr` survived with 41 of 41 held). The gaps are now one part, `GAP`, so no gap can be mutated alone, and the reviewer's string does not apply any more. R2 (the continuation dropped from `GAP`) fails four probes, among them `spelling: a continuation between "gh" and "pr" is still a merge call, refused at its line` (table below). The plants runner also has a `gh \`-newline-`pr merge` plant: it gives `refused=0` at base and `refused=1` at this head (Figures).
- **Block 2, the spellings class.** Closed by the parts above rather than one alternation per spelling. Each of the reviewer's shapes (`ev/probe.mjs`, run unchanged against this head with its extraction marker moved to the new block) now gives `bad ["f:1"]`. Its three null shapes still give `bad []`: the comment line after a continuation, the heredoc and the CRLF continuation. Every reviewer shape is also a `spelling:` probe, alongside the members the reviewer did not list:
  - a braced, quoted variable program;
  - a quoted option value;
  - a tuple argv;
  - `os.spawnlp`-style and `asyncio.create_subprocess_exec` arguments;
  - `os.system` with an f-string;
  - JS `execFileSync` and a template literal;
  - every short cluster;
  - `--body-file`;
  - the REST `commit_title` and the GraphQL `commitHeadline`.

  Failing first: with the reviewed head's production block swapped back in under this head's probes, `SELF-TEST 63 of 84 probes held`, and the 21 FAILs are each a new `spelling:` probe. On the tree, the reviewer's plants each give `refused=0` at base, and the single-quoted rewrite of `merge_train.py:864` drops the count to 51. Each gives `refused=1` at this head.
- **Finding, `\r?`** (R-crlf, widening only). Deleted. The null probe `a backslash before CRLF is no continuation in bash: the next line is another command` pins the bash behaviour the reviewer measured.
- **Findings, Y9 and Y10.** The reviewer agrees with both dispositions; they stand under Unpinned sites and Forward-carry.
- **The class rule.** Round 3 found that the census's rule 2 was a literal-spelling grep, which cannot return a spelling it does not match. Rule 2 is now the census harness, `r10_merge_subject_census.mjs`. It lists every line in the 287 scanned files that holds the words `pr` and `merge` in any quoting and is covered by no `MERGE_CALL` match. Each such line is then read (Figures).

## Review response (review/2697, round 2, `blocked 96ad30e87 mutation-vacuous`)

- **Y8** (`MERGE_CALL`'s shell arm reverted to literal spaces) and **the continuation inside the command name**: answered in round 2 by the `runs of whitespace` and `a shell continuation inside "gh pr merge"` probes, which both still hold. Round 3 replaced the arm they pinned with the parts. R25 (`GAP`'s whitespace narrowed to one literal space) and R26 (`GAP` one separator, no run) now kill the whitespace probe, and R2 the continuation probe.
- **Y9 and Y10**: dispositioned (Unpinned sites, Forward-carry).

## Review response (review/2697, round 1, `blocked mutation-vacuous`)

- **M12, M13**: one probe each, `null control: a quote opened in a comment ends with its line, ...` and `a bracket closed before the call on its line opens nothing: ...`. Both still fail under their mutants (table).
- **X6** (beyond the verdict): `every merge call in a file is read: a --subject on the second is refused, at its line`.

## Mutation proof

Instrument: `python3 dev/audit/harnesses/r10_merge_subject_mutants.py`, run from the worktree root at this head. It applies each string-replacement mutant to `tools/policy/agreement.mjs`, runs `node tools/policy/agreement.mjs --self-test`, prints the summary and each FAIL, and restores the file. The rows are:
- M1 to M13 from round 1's `evidence/mut.py`;
- X1 to X6 and Y1 to Y12 from round 2's `evidence/mut2.py`;
- R1 to R26, which mutate each named part and sub-part of round 3's `MERGE_CALL` and `SUBJECT_ARG`.

M9, Y8, Y8a and Y8b mutated the literal regexes those parts replaced, and are retired with them.

Unmutated: `SELF-TEST 84 of 84 probes held`. 55 mutants ran and 52 were killed. A survivor prints `84 of 84` and no FAIL. The three survivors, X5, Y9 and Y10, are dispositioned under Unpinned sites.

- M1 title arm end-anchor: 83 of 84, `FAIL a subject GitHub's title template never writes is refused`.
- M2 number \d+: 83 of 84, `FAIL a subject GitHub's title template never writes is refused`.
- M3 extent ends every line: 75 of 84, `FAIL a --subject on a shell continuation line is refused, at the call line`, `FAIL a --subject in an argv list split over lines is refused`, `FAIL a shell continuation inside "gh pr merge" is still a merge call: its --subject is refused, at the call line`, `FAIL spelling: a continuation between "gh" and "pr" is still a merge call, refused at its line`, `FAIL spelling: a continuation with no space before it is still a merge call, refused at its line`, `FAIL spelling: a continuation in every gap is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL an argv list broken between "pr" and "merge" is still a merge call`, `FAIL a merge_pull_request call whose commit_title is on a later line is refused`.
- M4 backslash ignored: 79 of 84, `FAIL a --subject on a shell continuation line is refused, at the call line`, `FAIL a shell continuation inside "gh pr merge" is still a merge call: its --subject is refused, at the call line`, `FAIL spelling: a continuation between "gh" and "pr" is still a merge call, refused at its line`, `FAIL spelling: a continuation with no space before it is still a merge call, refused at its line`, `FAIL spelling: a continuation in every gap is still a merge call, refused at its line`.
- M5 depth ignored at line end: 83 of 84, `FAIL a merge_pull_request call whose commit_title is on a later line is refused`.
- M6 blank-line end deleted: 83 of 84, `FAIL null control: a split merge call with no subject passes, and a flag on the next command is not the call's`.
- M7 enclosing close not end: 82 of 84, `FAIL null control: a sibling argv in the call's own table is not the call's`, `FAIL null control: a quote opened in a comment ends with its line, so the next statement's flag is not the call's`.
- M8 start always line start: 82 of 84, `FAIL null control: a sibling argv in the call's own table is not the call's`, `FAIL null control: a quote opened in a comment ends with its line, so the next statement's flag is not the call's`.
- M10 quotes not read: 83 of 84, `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`.
- M11 escapes not read: 83 of 84, `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`.
- M12 blank-line state reset removed: 83 of 84, `FAIL null control: a quote opened in a comment ends with its line, so the next statement's flag is not the call's`.
- M13 pop on close before at removed: 83 of 84, `FAIL a bracket closed before the call on its line opens nothing: a --subject after "(cd repo) &&" is refused`.
- X1 backward quote skip: 83 of 84, `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`.
- X2 forward quote skip: 83 of 84, `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`.
- X3 push deleted: 83 of 84, `FAIL null control: a sibling argv in the call's own table is not the call's`.
- X4 depth++ deleted: 81 of 84, `FAIL spelling: a JS template literal is still a merge call, refused at its line`, `FAIL a bracket closed before the call on its line opens nothing: a --subject after "(cd repo) &&" is refused`, `FAIL a merge_pull_request call whose commit_title is on a later line is refused`.
- X5 forward from open bracket: **survives, 84 of 84.**
- X6 first match only: 83 of 84, `FAIL every merge call in a file is read: a --subject on the second is refused, at its line`.
- Y1 close quote not cleared: 82 of 84, `FAIL null control: a sibling argv in the call's own table is not the call's`, `FAIL null control: a quote opened in a comment ends with its line, so the next statement's flag is not the call's`.
- Y2 line number off by one: 46 of 84, `FAIL a --subject on a shell continuation line is refused, at the call line`, `FAIL a shell continuation inside "gh pr merge" is still a merge call: its --subject is refused, at the call line`, `FAIL spelling: a continuation between "gh" and "pr" is still a merge call, refused at its line`, `FAIL spelling: a continuation with no space before it is still a merge call, refused at its line`, `FAIL spelling: a continuation in every gap is still a merge call, refused at its line`, `FAIL spelling: "merge" double-quoted is still a merge call, refused at its line`, `FAIL spelling: 'merge' single-quoted is still a merge call, refused at its line`, `FAIL spelling: "pr" double-quoted is still a merge call, refused at its line`, `FAIL spelling: "gh" double-quoted is still a merge call, refused at its line`, `FAIL spelling: an option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an option=value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an option before "pr" is still a merge call, refused at its line`, `FAIL spelling: the program in a variable is still a merge call, refused at its line`, `FAIL spelling: the program in a braced, quoted variable is still a merge call, refused at its line`, `FAIL spelling: the program on a path is still a merge call, refused at its line`, `FAIL spelling: inside a command substitution is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL spelling: whitespace before an argv comma is still a merge call, refused at its line`, `FAIL spelling: an argv option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: a shell option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv whose program is a variable is still a merge call, refused at its line`, `FAIL spelling: a tuple argv with no spaces is still a merge call, refused at its line`, `FAIL spelling: os.spawnlp-style separate arguments is still a merge call, refused at its line`, `FAIL spelling: asyncio.create_subprocess_exec arguments is still a merge call, refused at its line`, `FAIL spelling: a shell string in Python (shell=True, os.system, shlex.split) is still a merge call, refused at its line`, `FAIL spelling: JS execFileSync's argv is still a merge call, refused at its line`, `FAIL spelling: a JS template literal is still a merge call, refused at its line`, `FAIL spelling: --subject=value is still a merge call, refused at its line`, `FAIL spelling: -t with its value attached is still a merge call, refused at its line`, `FAIL spelling: -t clustered after the method flag is still a merge call, refused at its line`, `FAIL spelling: -b clustered after two boolean flags is still a merge call, refused at its line`, `FAIL spelling: -F clustered after the method flag is still a merge call, refused at its line`, `FAIL spelling: --body-file is still a merge call, refused at its line`, `FAIL spelling: the REST merge's commit_title is still a merge call, refused at its line`, `FAIL spelling: the GraphQL merge's commitHeadline is still a merge call, refused at its line`, `FAIL every merge call in a file is read: a --subject on the second is refused, at its line`.
- Y3 no line-end check for backslash nor open (always continue): 79 of 84, `FAIL null control: a backslash before CRLF is no continuation in bash: the next line is another command`, `FAIL null control: a comment line after a continuation ends the command`, `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`, `FAIL every merge call in a file is read: a --subject on the second is refused, at its line`, `FAIL null control: a split merge call with no subject passes, and a flag on the next command is not the call's`.
- Y4 open.length ignored at line end: 81 of 84, `FAIL a --subject in an argv list split over lines is refused`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL an argv list broken between "pr" and "merge" is still a merge call`.
- Y5 close ends extent at 0 not -1: 82 of 84, `FAIL spelling: a JS template literal is still a merge call, refused at its line`, `FAIL a bracket closed before the call on its line opens nothing: a --subject after "(cd repo) &&" is refused`.
- Y6 calls.push deleted: 16 of 84, `FAIL both GitHub templates pass the merge-subject guard`, `FAIL a hand-written merge subject is refused (#2379, 5756f2b1)`, `FAIL a title-only merge subject is refused`, `FAIL a single-parent commit is not a merge`, `FAIL the runner's test merge at HEAD is skipped, and refused anywhere else`, `FAIL a merge call that passes --subject is refused`, `FAIL a subject GitHub's title template never writes is refused`, `FAIL null control: titles of the host shape pass, a parenthesis in the title included`, `FAIL a --subject on a shell continuation line is refused, at the call line`, `FAIL a --subject in an argv list split over lines is refused`, `FAIL runs of whitespace inside "gh pr merge" are still a merge call: a --subject on "gh  pr<TAB>merge" is refused`, `FAIL a shell continuation inside "gh pr merge" is still a merge call: its --subject is refused, at the call line`, `FAIL spelling: a continuation between "gh" and "pr" is still a merge call, refused at its line`, `FAIL spelling: a continuation with no space before it is still a merge call, refused at its line`, `FAIL spelling: a continuation in every gap is still a merge call, refused at its line`, `FAIL spelling: "merge" double-quoted is still a merge call, refused at its line`, `FAIL spelling: 'merge' single-quoted is still a merge call, refused at its line`, `FAIL spelling: "pr" double-quoted is still a merge call, refused at its line`, `FAIL spelling: "gh" double-quoted is still a merge call, refused at its line`, `FAIL spelling: an option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an option=value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an option before "pr" is still a merge call, refused at its line`, `FAIL spelling: the program in a variable is still a merge call, refused at its line`, `FAIL spelling: the program in a braced, quoted variable is still a merge call, refused at its line`, `FAIL spelling: the program on a path is still a merge call, refused at its line`, `FAIL spelling: inside a command substitution is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL spelling: whitespace before an argv comma is still a merge call, refused at its line`, `FAIL spelling: an argv option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: a shell option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv whose program is a variable is still a merge call, refused at its line`, `FAIL spelling: a tuple argv with no spaces is still a merge call, refused at its line`, `FAIL spelling: os.spawnlp-style separate arguments is still a merge call, refused at its line`, `FAIL spelling: asyncio.create_subprocess_exec arguments is still a merge call, refused at its line`, `FAIL spelling: a shell string in Python (shell=True, os.system, shlex.split) is still a merge call, refused at its line`, `FAIL spelling: JS execFileSync's argv is still a merge call, refused at its line`, `FAIL spelling: a JS template literal is still a merge call, refused at its line`, `FAIL spelling: --subject=value is still a merge call, refused at its line`, `FAIL spelling: -t with its value attached is still a merge call, refused at its line`, `FAIL spelling: -t clustered after the method flag is still a merge call, refused at its line`, `FAIL spelling: -b clustered after two boolean flags is still a merge call, refused at its line`, `FAIL spelling: -F clustered after the method flag is still a merge call, refused at its line`, `FAIL spelling: --body-file is still a merge call, refused at its line`, `FAIL spelling: the REST merge's commit_title is still a merge call, refused at its line`, `FAIL spelling: the GraphQL merge's commitHeadline is still a merge call, refused at its line`, `FAIL null control: a word that only begins with "merge" is not the merge command`, `FAIL null control: another pr subcommand, with -t of its own, is not a merge call`, `FAIL null control: a variable program running another pr subcommand is not a merge call`, `FAIL null control: a backslash before CRLF is no continuation in bash: the next line is another command`, `FAIL null control: a comment line after a continuation ends the command`, `FAIL null control: -A takes a value, so "-Amt" is no -t`, `FAIL null control: a program whose name only ends in "gh" is not gh`, `FAIL null control: the boolean flags alone set no subject`, `FAIL an argv list broken between "pr" and "merge" is still a merge call`, `FAIL null control: a sibling argv in the call's own table is not the call's`, `FAIL null control: a bracket in a quote, past an escaped quote, opens no command`, `FAIL a bracket closed before the call on its line opens nothing: a --subject after "(cd repo) &&" is refused`, `FAIL every merge call in a file is read: a --subject on the second is refused, at its line`, `FAIL null control: a quote opened in a comment ends with its line, so the next statement's flag is not the call's`, `FAIL a merge_pull_request call whose commit_title is on a later line is refused`, `FAIL null control: a split merge call with no subject passes, and a flag on the next command is not the call's`, `FAIL a merge call that passes commit_title is refused`, `FAIL a recarried branch's own `Merge origin/main into <branch>` is not judged`, `FAIL a hand subject on main is refused from a recarried branch, and only it`, `FAIL a hand subject is refused on main's own push run`, `FAIL with no origin/main ref the walk falls back to HEAD and refuses a hand subject there`.
- Y7 ls off: 81 of 84, `FAIL a --subject on a shell continuation line is refused, at the call line`, `FAIL spelling: the program in a variable is still a merge call, refused at its line`, `FAIL every merge call in a file is read: a --subject on the second is refused, at its line`.
- Y9 slice end exclusive at close: **survives, 84 of 84.**
- Y10 blank-line return removed only text tail: **survives, 84 of 84.**
- Y11 title space one -> any: 83 of 84, `FAIL a subject GitHub's title template never writes is refused`.
- Y12 title leading \S -> .: 83 of 84, `FAIL a subject GitHub's title template never writes is refused`.
- R1 QUOTE: double quote only: 80 of 84, `FAIL spelling: 'merge' single-quoted is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL spelling: JS execFileSync's argv is still a merge call, refused at its line`.
- R2 GAP: the \-newline continuation dropped: 80 of 84, `FAIL a shell continuation inside "gh pr merge" is still a merge call: its --subject is refused, at the call line`, `FAIL spelling: a continuation between "gh" and "pr" is still a merge call, refused at its line`, `FAIL spelling: a continuation with no space before it is still a merge call, refused at its line`, `FAIL spelling: a continuation in every gap is still a merge call, refused at its line`.
- R3 GAP: the argv comma dropped: 72 of 84, `FAIL a --subject in an argv list split over lines is refused`, `FAIL spelling: a single-quoted argv is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL spelling: whitespace before an argv comma is still a merge call, refused at its line`, `FAIL spelling: an argv option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv whose program is a variable is still a merge call, refused at its line`, `FAIL spelling: a tuple argv with no spaces is still a merge call, refused at its line`, `FAIL spelling: os.spawnlp-style separate arguments is still a merge call, refused at its line`, `FAIL spelling: asyncio.create_subprocess_exec arguments is still a merge call, refused at its line`, `FAIL spelling: JS execFileSync's argv is still a merge call, refused at its line`, `FAIL an argv list broken between "pr" and "merge" is still a merge call`.
- R4 word: the end-of-word lookahead dropped: 83 of 84, `FAIL null control: a word that only begins with "merge" is not the merge command`.
- R5 word: the opening quote dropped: 81 of 84, `FAIL spelling: "merge" double-quoted is still a merge call, refused at its line`, `FAIL spelling: 'merge' single-quoted is still a merge call, refused at its line`, `FAIL spelling: "pr" double-quoted is still a merge call, refused at its line`.
- R6 word: the closing quote dropped: 83 of 84, `FAIL spelling: "pr" double-quoted is still a merge call, refused at its line`.
- R7 OPTIONS: no option between words: 78 of 84, `FAIL spelling: an option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an option=value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an option before "pr" is still a merge call, refused at its line`, `FAIL spelling: an argv option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: a shell option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`.
- R8 OPTION: the separate value dropped: 79 of 84, `FAIL spelling: an option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an option before "pr" is still a merge call, refused at its line`, `FAIL spelling: an argv option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: a shell option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`.
- R9 OPTION: the =value dropped: 83 of 84, `FAIL spelling: an option=value between "pr" and "merge" is still a merge call, refused at its line`.
- R10 OPTION: long options only: 82 of 84, `FAIL spelling: an option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: a shell option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`.
- R11 OPTION: a value word may hold no quote mark: 82 of 84, `FAIL spelling: an argv option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: a shell option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`.
- R12 PROGRAM: the variable program dropped: 82 of 84, `FAIL spelling: the program in a variable is still a merge call, refused at its line`, `FAIL spelling: the program in a braced, quoted variable is still a merge call, refused at its line`.
- R13 PROGRAM: an unbraced variable only: 83 of 84, `FAIL spelling: the program in a braced, quoted variable is still a merge call, refused at its line`.
- R14 PROGRAM: the path dropped: 83 of 84, `FAIL spelling: the program on a path is still a merge call, refused at its line`.
- R15 PROGRAM: the lookbehind dropped: 83 of 84, `FAIL null control: a program whose name only ends in "gh" is not gh`.
- R16 PROGRAM: the closing quote dropped: 82 of 84, `FAIL spelling: "gh" double-quoted is still a merge call, refused at its line`, `FAIL spelling: the program in a braced, quoted variable is still a merge call, refused at its line`.
- R17 the quoted pr/merge arm dropped: 82 of 84, `FAIL spelling: an argv whose program is a variable is still a merge call, refused at its line`, `FAIL spelling: JS execFileSync's argv is still a merge call, refused at its line`.
- R18 merge_pull_request dropped: 82 of 84, `FAIL a merge_pull_request call whose commit_title is on a later line is refused`, `FAIL a merge call that passes commit_title is refused`.
- R19 mergePullRequest dropped: 83 of 84, `FAIL spelling: the GraphQL merge's commitHeadline is still a merge call, refused at its line`.
- R20 the REST merge path dropped: 83 of 84, `FAIL spelling: the REST merge's commit_title is still a merge call, refused at its line`.
- R21 SUBJECT_ARG: short flags alone, no cluster: 80 of 84, `FAIL spelling: -t with its value attached is still a merge call, refused at its line`, `FAIL spelling: -t clustered after the method flag is still a merge call, refused at its line`, `FAIL spelling: -b clustered after two boolean flags is still a merge call, refused at its line`, `FAIL spelling: -F clustered after the method flag is still a merge call, refused at its line`.
- R22 SUBJECT_ARG: -d not a cluster flag: 83 of 84, `FAIL spelling: -b clustered after two boolean flags is still a merge call, refused at its line`.
- R23 SUBJECT_ARG: -F dropped from the short flags: 83 of 84, `FAIL spelling: -F clustered after the method flag is still a merge call, refused at its line`.
- R24 SUBJECT_ARG: commitHeadline/commitBody dropped: 83 of 84, `FAIL spelling: the GraphQL merge's commitHeadline is still a merge call, refused at its line`.
- R25 GAP: whitespace narrowed to one literal space: 81 of 84, `FAIL runs of whitespace inside "gh pr merge" are still a merge call: a --subject on "gh  pr<TAB>merge" is refused`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL an argv list broken between "pr" and "merge" is still a merge call`.
- R26 GAP: one separator only, no run: 69 of 84, `FAIL a --subject in an argv list split over lines is refused`, `FAIL runs of whitespace inside "gh pr merge" are still a merge call: a --subject on "gh  pr<TAB>merge" is refused`, `FAIL a shell continuation inside "gh pr merge" is still a merge call: its --subject is refused, at the call line`, `FAIL spelling: a continuation between "gh" and "pr" is still a merge call, refused at its line`, `FAIL spelling: a continuation in every gap is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv is still a merge call, refused at its line`, `FAIL spelling: a single-quoted argv split over lines is still a merge call, refused at its line`, `FAIL spelling: whitespace before an argv comma is still a merge call, refused at its line`, `FAIL spelling: an argv option and value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv option with a quoted value between "pr" and "merge" is still a merge call, refused at its line`, `FAIL spelling: an argv whose program is a variable is still a merge call, refused at its line`, `FAIL spelling: os.spawnlp-style separate arguments is still a merge call, refused at its line`, `FAIL spelling: asyncio.create_subprocess_exec arguments is still a merge call, refused at its line`, `FAIL spelling: JS execFileSync's argv is still a merge call, refused at its line`, `FAIL an argv list broken between "pr" and "merge" is still a merge call`.

Failing test first, for this round: the reviewed head's production block (`// What a merge call may not carry` through `SUBJECT_ARG`, from `455d7c20`) swapped in under this head's probes gives `SELF-TEST 63 of 84 probes held`. The 21 FAILs are the `spelling:` probes for:
- the quoted words (4);
- the options between words (6, quoted values included);
- the variable programs (2);
- the single-quoted and comma-spaced argvs (3);
- JS `execFileSync`;
- the four short-cluster and attached-value spellings;
- the GraphQL merge.

Earlier rounds: Y8 held 39 of 39 at `96ad30e87`, and M12, M13 and X6 each held every probe at `b4dd11917`. Each now fails a probe.

## Null control

- Finding 1, on real history: over `git log --first-parent --merges --format=%s origin/main` (1048 subjects at `50af6174f`), the old arm accepts 15 and the new arm accepts 15. No subject is accepted by one and refused by the other. The title arm is unchanged since.
- Finding 1, synthetic: `null control: titles of the host shape pass, a parenthesis in the title included`.
- Findings 2 and 3, unperturbed tree: with `python3 -I tools/policy/agreement_py.py --run`, both base `4a00a3f05` and this head print `refused=0`. The head adds no false refusal on any of the 11 files the scan reads.
- Finding 3, the call count: per match, the census reads 55 calls at the reviewed head and 56 here. The one new call is `tools/audit/seat/merge_train.py:2874`, an error string naming `(mergePullRequest)`. It carries no flag and is not refused, the same standing as the existing `merge_pull_request` prose matches.
- Finding 3, synthetic: eight new `null control:` probes over the same parts (13 `null control:` probes in all). Each must pass:
  - a word that only begins with `merge` (`gh pr merged`);
  - another pr subcommand with a `-t` of its own (`gh pr view 9 --json title -t ...`);
  - a variable program running another subcommand;
  - a backslash before CRLF;
  - a comment line after a continuation;
  - `-Amt...`, where `-A` consumes the cluster;
  - the boolean flags alone;
  - a program whose name only ends in `gh` (`hgh`).
- The round-1 and round-2 writer null controls still hold: a split call with no subject, `--body` on the next command, a blank line, a sibling argv, and a quoted bracket.

## Figures

- Self-test: `node tools/policy/agreement.mjs --self-test` → `SELF-TEST 84 of 84 probes held`.
- The finder's harness at both ends: `PYTHON=seat-python3 bash dev/audit/harnesses/r10_merge_subject_plants.sh [origin/main]`. It runs `python3 -I tools/policy/agreement_py.py --run` unperturbed and under each plant, with the guard from the ref or the working tree.
  - Base (`origin/main`, `4a00a3f05`):
    - unperturbed: `52 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`;
    - the single-quoted rewrite of `merge_train.py:864`: `51 merge call(s)`, `refused=0`;
    - `gh pr "merge"`, `gh pr -R o/r merge` and `gh \`-newline-`pr merge`, each appended to `merge_pr.sh`: `52 merge call(s)`, `refused=0`;
    - a `-mt` cluster: `53 merge call(s)`, `refused=0`.
  - The reviewed head's guard (`455d7c20`, byte-identical to `757631fa4`): the same plants give `refused=0`, except the `gh \`-newline-`pr merge` plant, which gives `refused=1`.
  - This head:
    - unperturbed: `56 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`;
    - each of the five plants: `REFUSED merge-subject-pr writer` at the planted line (`merge_train.py:864`, or `merge_pr.sh:258`), `refused=1`.
- The same run at this head prints `pair merge-subject-pr: 4 readers, 1072 items, 0 divergent` and `271 first-parent commit(s) past 07a09406a`. Both grow with the commits on HEAD, so they describe this SHA only. The claim that holds across heads is `0 divergent`.
- The tree census: `node dev/audit/harnesses/r10_merge_subject_census.mjs <reviewed-head agreement.mjs>`, over the 287 files the guard scans.
  - `DIFF tools/audit/seat/merge_train.py:2874 old=0 new=1` and `TOTAL old=55 new=56`. Matches are counted, not lines. Base's own note counts 52, because it tested lines.
  - `UNCOVERED 60 of 95 line(s) holding both words`. I read each of the 60, and none is a merge call:
    - fake-gh case patterns and recorded-call strings in self-tests (`merge_pr.sh:186` `"pr merge "*)`, `merge_pr.sh:200`, `merge_train.py:3119`, `merge_train.py:3121`);
    - `refs/pull/<n>/merge` refs (`ci_probe.py`, `codescan_wait.py`, `local_alerts.py`);
    - log, prose and docstring lines naming a pull request and a merge;
    - dict keys (`"pr": ..., "kind": "merge"`);
    - the verdict string `Fix review: merge`.

    No line holds a program word (`gh`, a variable) followed by `pr` and `merge`, except inside a match.
- The class census, rule 1 (the title shape), re-run at this head: `git grep -n -F '\(#' -- 'tools/*.py' 'tools/*.mjs' 'tools/*.js' 'tools/*.sh' 'tests/*.py' '.github/*' '.claude/*'`, less `tools/audit/round*`. It returns:
  - `TEMPLATE_SUBJECT` and the discovery-registry key in `agreement.mjs`;
  - `tests/delivery_status.py`'s `SQUASH_SUBJECT` and its comment, `tools/release/stamp.py`'s `PR_RE` and `tools/policy/policy_lint.mjs`'s `MERGE_SUBJECT_RE`: PR-number readers that the `merge-subject-pr` pair holds to agreement;
  - `tools/policy/record-predicate/sweep.mjs`: a PR-number reader over record lines.

  None is a merge-subject shape guard beside `TEMPLATE_SUBJECT`.
- The class census, rule 2 (the call spellings): the census harness above, replacing round 2's literal grep.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` The one run is `tests/entities.py`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at `6e7a8b29e` (the guard and probes as at this head): `4 of 2425 ENTITY CHECKS FAILED`. All four are the heartbeat positive control: `hb:positive_control survives one hung py-spy sample ...`, `and a try whose sample misses the spin ... is retried`, `the control rests between tries ...` and `the control survives two hung samples ...`. These are timing and py-spy checks on a loaded box, and none reads `tools/policy/agreement.mjs`. The same four fail at base `73b69fe0a`, in a detached worktree in round 2: `4 of 2425 ENTITY CHECKS FAILED`. Main has moved since then only in policy, triage, `ref_privacy.py` and `roster_sync.py`, none of which the control reads. So these four belong to the environment, not to this diff. CI is the authority. The later commits add only `dev/audit/harnesses/` files and `tests/closures.json` lines, and `tests/harness_headers.py` passes at this head.
- run_always:
  - `python3 tests/env_drift.py --claims-only origin/main` → `claims hygiene: origin/main ok`;
  - `python3 tests/closure.py selftest` → `ALL 117 closure shrink pins PASSED`;
  - `python3 tests/layout.py` → `layout self-test: ok`;
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` → `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs` → `TOTAL: 0 error(s) across 50 policy file(s)`.
- `python3 -I tools/policy/agreement_py.py --run` → `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures or fast red predicted against 4a00a3f053c2 (a data-file read is not seen)`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`. No metric moved.

## Unpinned sites

Three, each dispositioned by written triage. `ci_predict.py` lists none. Every other row of the 55-row table (Mutation proof) is killed, each with its FAIL named. That covers every part of `MERGE_CALL` and `SUBJECT_ARG` (R1 to R26). Round 3 found that round 2's version of this sentence was false for the first continuation gap. That gap now shares the one `GAP` part with the others, and R2 kills it.

- `callExtent`'s `start + (open.length ? 1 : 0)` (X5 survives). Deleting the `+ 1` makes the extent run to the bracket enclosing the call's own group, which only adds refusals. The only probe that would kill it pins a writer miss as correct (`run(["gh", "pr", "merge", n], "--subject", s)`). That shape belongs to the argv-across-expressions seam below.
- The argv-across-expressions seam. A subject flag that joins the argv in another expression is outside the call's bracket group. `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` prints:
  - `run(["gh", "pr", "merge", n] + ["--subject", s])` → `[]` (missed);
  - `args = ["gh", "pr", "merge", n]` / `args += ["--subject", s]` / `run(args)` → `[]` (missed);
  - control `run(["gh", "pr", "merge", n, "--subject", s])` → `["f:1"]` (refused).

  Merges go only through `tools/audit/seat/merge_pr.sh` and `tools/audit/seat/merge_train.py`, and `grep -n -e '--subject'` over both returns nothing. Dismissed under Forward-carry, by the orchestrator's decision.
- The same limit, for the members of round 3's class that no lexical scan reads:
  - a word quoted or escaped inside itself (`gh pr m"erge"`, `g\h`);
  - a gh alias (`gh alias set m 'pr merge'`, then `gh m`);
  - `eval` of a built string;
  - a command or argv held in a variable and expanded later (`"${ARGS[@]}"`).

  Each is the argv-across-expressions case in another spelling. The same barrier holds, and the dismissal under Forward-carry names them.
- `callExtent`'s close `return text.slice(start, i + 1)` to `text.slice(start, i)` (Y9 survives, 84 of 84). It can only add refusals, never a writer miss. Rounds 2 and 3 of review agree.
- The blank-line test's `next < 0 ? text.length : next` to `next` (Y10 survives, 84 of 84). It changes only a file's single-character last line, which cannot hold a subject flag. Rounds 2 and 3 of review agree.

## Red checks

- `pr-contract / pr-contract` on the reviewed head `455d7c20` (job `120936964374`, 17:23Z): the step `python3 -I tools/ci/codescan_wait.py --pr "$PR_NUMBER" --base "$BASE_REF"` exited 1 before printing an alert list. Its other arms passed in the same log: `FIGURES: 22 resolved, 2 not verified, 0 refused`, `clean no refusal`, and `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted`. This is the run-id ordering race that `dev/audit/rca/R10-RCA-CODESCAN-WAIT.md` (topic `r10-rca-codescan-wait`) records: an edit run with the lower id waits for no code run, and `codescan_wait.py` fails at once. Its body counts 27 of 94 code-and-edit pairs ordered that way. It reads no file this diff touches. The cheaper detector question is answered there, not here: it is that RCA's countermeasure, and this PR's own checks cannot see it.
- `gate` on `455d7c20` (job `120937091704`): `FAIL run(s) [40115512480] at this head are still being judged; their gate decides`. That is the designed defer to the head's other run, not a failure of this diff.

## Forward-carry

- The argv-across-expressions seam and its in-word spellings, under Unpinned sites. Carry: dismissed: lexical writer scan cannot follow argv built across expressions, in-word quoting or escapes, gh aliases or eval (probe shapes under Unpinned sites); no such site on tree (census: 0 of 60 uncovered lines is a call), widening re-adds the gh_read.py sibling-argv false positive; merges go only through merge_pr.sh/merge_train.py, which never pass --subject
- Y9, `callExtent` dropping the closing bracket. Carry: dismissed: near-equivalent mutant that only widens refusal; no writer miss
- Y10, the blank-line test at end of file. Carry: dismissed: near-equivalent mutant at end of file only; no writer miss on any realistic input

## Friction

none.
