R10-TRAIN-STALE-VERDICT-GUARD: the merge train refuses a merge verdict when a blocked verdict at the same head was dispatched later (triage batch 127, P393).

The defect, as the triage found it: the train admitted the newest posted `verdict/<pr>` tip. A stale reviewer seat can post its merge verdict after a later-dispatched reviewer has already blocked the same head, and the train admitted it. PR 3232 at `bba5b4d4` is the instance:
- the merge verdict's nonce `2a9f4501` is recorded as dispatched at 2026-11-06T20:50:26Z;
- the blocked verdict's nonce `cc3bfb99` is recorded as dispatched at 22:13:28Z.

Those two times are the triage's record. Both logs that hold them are host-local, so this seat could not re-read them.

The fix, in tools/audit/seat/merge_train.py:
- `Train.posted_verdict` makes one more read after it reads a `merge` verdict: `Train.stale_verdict(n, tip, head)`. Both admission paths share `posted_verdict`: the queue builder (`admit_verdict`, so `queue`, `sweep` and `ready_batch`) and `admit_add`'s `verdict` rule (and through it bus.sh's `add --auto`).
- `stale_verdict` fetches `verdict/<n>` and reads its history from the tip (`git log --format=%H%x00%s`). Every older commit whose subject parses (`proof_watch.parse_verdict`) as `blocked <head>`, at the merge verdict's head, is a finding at that head. If the fetch or the log fails, the merge is refused. A failed read is never taken to mean there is no blocked verdict.
- Nonces: each verdict commit carries its review tree, so the nonce is read from that commit's VERDICT.md by `proof_watch.verdict_nonce`. That function is new: it is the one Python reader of the line bus.sh's `verdict_nonce` reads, the first whole `^bus-nonce: <32 hex>$` line.
- Dispatch times: `dispatch_order` reads them from bus.sh's worker registry, `$HPO_BUS_STATE/dispatched` (else `~/.zcode/bus/dispatched`), which is the source the brief names. It takes the nonce's first record for that PR and head (its mint). It validates the time with `strptime` against bus.sh's `date -u +%FT%TZ`. A same-second pair is ordered by append order.
- `stale_merge` is the rule:
  - same nonce: admitted;
  - the merge verdict's dispatch is before the blocked verdict's: refused, `stale merge verdict: ...`;
  - either time is missing: refused, `stale merge verdict undecidable: ...`, naming which. Missing means no record, a time-less record from before R10-ORCH-DISPATCH-REG (also not dated by a later `--nonce` re-record), a malformed time, no registry file, or no nonce line;
  - later dispatch: admitted.

The seam choice. I put the check on the `posted_verdict` read, not in a new `merge_train.py admit` subcommand. The brief rules that a subcommand is not to be added only to match the carry wording. `posted_verdict` is the one read both admissions share, so one call site covers both. Two alternatives lost:
- `admit_add` alone: the queue builder and the sweep would stay open;
- the events log: the brief rules it out because it keeps only 8 nonce characters.

Design choices:
- An undecidable case refuses rather than admits, as the carry text says. On the orchestrator's host this should cost nothing live. The registry has had its utc field since de66f00bd (R10-ORCH-DISPATCH-REG, 2026-10-26), and the triage records every open PR's dispatches inside that window.
- The guard needs the registry, which lives only on the host where bus.sh dispatches. The instrument entry says to run the train there.

Beyond merge_train.py:
- tools/audit/seat/proof_watch.py, tools/audit/seat/cloud_dispatch.py: the agreement lane refused my first cut. It had copied `^bus-nonce: ([0-9a-f]{32})$`, a grammar cloud_dispatch already wrote twice inline, without registering it. I did not register the copy, because CI grades with the base's `SHARED_GRAMMARS` (#3100). Instead, `proof_watch.py` now holds the grammar (`NONCE_LINE`, `verdict_nonce`), and cloud_dispatch's two inline copies call it.
  - cloud_dispatch's self-test reads 129 checks, 0 failed at main 661d26a5d both before and after this change.
  - Importing `review_strength.NONCE_RE` lost: it would add a file outside `agreement_py.py`'s restore closure (`UNRESTORED tools/audit/seat/review_strength.py`), and its rule is looser (`\s*`, no `$`) than bus.sh's.
  - The registry timestamp regex, which gh_calls.py also writes, became a `strptime` parse. That parse also refuses a time that is not a real time.
- tools/audit/seat/instruments/merge_train.py.md: the instrument entry.
- dev/audit/harnesses/r10_triage_p393.py, the finder's harness:
  - a `guard` arm drives the production `Train.stale_verdict` over every historical instance;
  - its nonce reader now imports `proof_watch.verdict_nonce`.

A defect in the harness, found here and fixed in it. Its unanchored `bus-nonce:\s*([0-9a-f]{8})` read the nonce that PR 2465's merge verdict quotes in a finding's prose (round 2's `bus-nonce: 0f1f8919...`) as that verdict's own nonce. The verdict's own trailer is `f8b99351`. So the triage's "4 same" counts one false SAME. At the same bus snapshot, the base harness prints `same=4` and the head harness prints `same=3`.

## Head

`fb39908639d83652b8d469da87d90891edac7da8`. It merges origin/main `19865e5a866ce066eaa52f7167a7d901fd1d5968` into `0c1bfeef8`, with no conflict and touching no file this diff changes. The branch was cut from `17e621f08c4feec724478573741fbd8b596ceaba`, the base I was given, and merged main three times. Each merge was made because main had moved since the last `prepr.sh` run, and each was followed by a re-run:
- `a41d9f110` merged `661d26a5d2e655f32391048605db5970d133db1d`;
- `0c1bfeef8` merged `fdc8d21adaa50a7feee534f08ee5edde9bda81ed`;
- this head merged `19865e5a8`.

What was taken where:
- The self-tests, the scope and the final `prepr.sh` run are at this head. The hand mutants are at `962aad515`, which has the same production lines. The prepr run's start, end and origin/main at the start are in `## Figures`.
- The harness figures are at `a41d9f110`. The merges since then brought in no file the harness or `stale_verdict` reads; main's cloud_dispatch.py changes are the only overlap with this diff, and its self-test is green.
- The diff-mutant run is at `a41d9f110`. Since then the branch added one test line (962aad515), whose own survivor is killed by hand below.

## Mutation proof

Failing first, at b9a510304 (the self-test only, before the fix): `python3 tools/audit/seat/merge_train.py --self-test` printed `merge_train self-test: 576 checks, 9 failed`. That run was before later arms were added. The failing checks were:
- `stale verdict: STALE -- ...`;
- the six `stale verdict: a missing dispatch time is refused with its reason (...)` cases that existed then;
- `stale verdict: a same-second tie is ordered by the registry's append order (...)`;
- `stale verdict: an unreadable verdict/<pr> history is refused ...`.

The hand mutants were re-taken at the pre-merge tree of this head (`962aad515`, the same production lines). Each was one single-occurrence replacement in the file, then `python3 tools/audit/seat/merge_train.py --self-test`, then a restore. Afterwards, `cmp` against the saved copies printed nothing.
- Baseline: `579 checks, 0 failed`.
- M1, the comparison dropped (`if mt < bt:` -> `if False:`): `3 failed`:
  - `stale verdict: STALE -- ...`;
  - `stale verdict: a same-second tie ...`;
  - `stale verdict: the dispatch time decides, not the registry's line order ...`.
- M2, the same-nonce admission dropped (`if merge is not None and b == merge:` -> `if False:`): `1 failed`, `stale verdict: SAME (null control) -- ...`.
- M3, proof_watch's `NONCE_LINE` unanchored (`^bus-nonce: ...$` -> `bus-nonce: ...`): `5 failed`, among them STALE and LATER. The fixture's VERDICT.md quotes the other verdict's nonce in prose, in PR 2465's shape.
- M4, a time-less mint dated by a later re-record (`return None` -> `continue` in `dispatch_order`): `1 failed`, `... (a mint before the utc field is not dated by a later --nonce re-record)`.
- S1, `return f[4], i` -> `return f[5], i`: `1 failed`, `... the dispatch time decides, not the registry's line order ...`.
- S5380, the fixture's `calls.append(argv)` dropped: `1 failed`, `stale verdict: a blocked verdict at another head is not this head's finding (admitted, no nonce read)`.
- Killed at b8a801aea by the same method:
  - the fetch guard off (`if False:`): `1 failed`;
  - the fetch guard's `[0]` -> `[1]`: `6 failed`;
  - the no-blocked early exit off: `1 failed`.

Diff mutants: `prepr.sh` step 6d at `a41d9f110`, with `MUTANT_CMD` set to the merge_train, proof_watch and cloud_dispatch self-tests, printed `6 survivor(s) on the diff's added lines`. Each is answered under `## Unpinned sites`. The same step at `e53b46eda` had printed 11. The 5 killed since are S1, the fetch guard's GUARD_OFF, CONST_SWAP and RETURN_DEL, and the early-exit GUARD_OFF and RETURN_DEL, killed by the tests in b8a801aea.

## Null control

- The two arms the rule must admit:
  - `stale verdict: LATER (null control)`: the merge verdict dispatched after the blocked one is admitted, by `posted_verdict` and by `admit_add`;
  - `stale verdict: SAME (null control)`: one nonce posted both verdicts, with an empty registry, and it is admitted.
- `stale verdict: a blocked verdict at another head is not this head's finding`: admitted with no registry file. The check also asserts that the history read ran, so it is not vacuous, and that no nonce was read.
- The unmodified tree: at the base, the guard arm admits every one of the 64 historical instances (`guard=absent admitted=64`; `## Figures`). That is the defect.
- The existing fixtures pass unchanged: merge_train `579 checks, 0 failed`, against `564` at main. Their stubs answer `git log` with nothing, so no verdict in them has a blocked predecessor.
- proof_watch prints `47 checks, 0 failed` and cloud_dispatch `131 checks, 0 failed` at this head. The same scripts at main `fdc8d21ad` print 47 and 131; main added cloud_dispatch's two extra checks since 661d26a5d, where it printed 129 both with and without this diff.

## Figures

- Self-tests at the head:
  - `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 579 checks, 0 failed`. At main it prints `564 checks, 0 failed`; this diff adds 15 checks in `_stale_verdict_self_test`.
  - `python3 -I tools/audit/seat/proof_watch.py --self-test` prints `proof_watch self-test: 47 checks, 0 failed`.
  - `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` prints `cloud_dispatch self-test: 131 checks, 0 failed`.
- The finder's harness at both ends.
  - Setup:
    - The base copy is dev/audit/harnesses/r10_triage_p393.py at main 661d26a5d (unchanged since 17e621f08), sha1 aad12c7b1a754c181fa49ae348840676ea9e04e4. The head copy has sha1 040151ecdc06d0f7cdf45cbb7e0311056b9353de.
    - The runs were taken back to back, 2026-11-08T22:36:22Z to 22:36:42Z, over one fetch of every `verdict/*` and `review/*` ref. The bus moves (703, 704 and 705 refs across this session's runs), so a later run re-derives its own counts.
    - The `stale` arm's events log is host-local and absent here, so it was given an empty file. That is why the brief's `1 stale, 21 later` cannot be re-taken here: STALE and LATER need a time, and SAME does not.
  - `python3 -I dev/audit/harnesses/r10_triage_p393.py stale <empty events.tsv>`:
    - base: `verdict refs=705 instances=64 stale=0 later=0 same=4 unknown=60`;
    - head: `verdict refs=705 instances=64 stale=0 later=0 same=3 unknown=61`.
    - `diff` of the two outputs differs only on PR 2465's line (`SAME ... merge=0f1f8919` -> `UNKNOWN ... merge=f8b99351`) and on the tally.
  - `python3 -I dev/audit/harnesses/r10_triage_p393.py guard <state dir>`, with the head harness copied beside the base tree's merge_train (removed afterwards):
    - base merge_train, empty state dir: `guard=absent admitted=64 refused-stale=0 refused-undecidable=0`.
    - head, empty state dir (no registry): `guard=yes admitted=3 refused-stale=0 refused-undecidable=61`. The 3 admitted are exactly the head `stale` arm's 3 SAME: PR 2323, 2329 and 3045.
    - head, with a registry of PR 3232's two dispatches only, at the triage's recorded times, with full nonces read from that PR's verdict commits b09e48026 and 8000a4f5d: `admitted=3 refused-stale=1 refused-undecidable=60`. The refusal line is `refused-stale pr=3232 head=bba5b4d4 merge=b09e4802 stale merge verdict: its nonce 2a9f4501 was dispatched at 2026-11-06T20:50:26Z, before the blocked verdict's cc3bfb99 at 2026-11-06T22:13:28Z`.
    - null control, the same registry with the merge dispatch moved after the blocked one (23:50:26Z): `admitted=4 refused-stale=0 refused-undecidable=60`, PR 3232 admitted.
    - base merge_train with the PR 3232 registry: `admitted=64`, so the base admits the stale verdict.
  - The real 1/21 split needs the host registry. The reviewer or orchestrator runs `python3 -I dev/audit/harnesses/r10_triage_p393.py guard ~/.zcode/bus` on the host where bus.sh dispatches.
- Class enumeration. The rule: `git grep -n -E 'parse_verdict\(|posted_verdict\(|VERDICT_MERGE' -- tools`, less self-test lines. Every seam it returns, and its disposition:
  - `merge_train.py` `admit_verdict` -> `posted_verdict` (queue, sweep, ready_batch): closed in this diff.
  - `merge_train.py` `add_verdict` -> `posted_verdict` (`admit_add`, and bus.sh's `add --auto` at post time): closed in this diff.
  - `merge_train.py` `stale_verdict`'s own `parse_verdict` call: this diff.
  - `orchestrator_tick.py` `MERGE-READY` and `REVIEW STALLED`: unchanged on purpose. These are report lines that merge nothing, and a stale verdict flagged MERGE-READY is still refused at the train's admission.
  - `review_packet.py` `verdict_merge_head`: not an admission. It names the reviewed head for a carry.
  - `proof_watch.py`: the grammar's definition, not a reader.
  - tools/pr/app_approve.sh's evidence gate: the rule does not return it. It runs only after the train has admitted the entry, and the train now refuses the stale case first.
- Scoped gate at the head: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and names tests/entities.py.
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `ALL 2668 ENTITY CHECKS PASSED`, rc 0, at a314a05fb.
  - prepr's `closures` step re-records and checks it at every run: `scoped recordings are covered; left to CI: tests/harness_headers.py`.
- run_always lines, at cc7dc09ff:
  - `tests/env_drift.py --claims-only` printed `claims hygiene: 17e621f... ok`;
  - `tests/closure.py selftest` printed `ALL 118 closure shrink pins PASSED`;
  - `tests/layout.py` printed `layout self-test: ok`;
  - `tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`.
- Structure: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Agreement: `python3 -I tools/policy/agreement_py.py --out <f>` then `node tools/policy/agreement.mjs --py-json <f>` prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`. The restore line reads `18 closure file(s), 18 covered`.
- Architecture: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD` printed `Architecture score: dS +0.0000 NULL` at cc7dc09ff.
- prepr at this head: `bash tools/pr/prepr.sh <this body>` prints `PRE-PR: fb39908639d83652b8d469da87d90891edac7da8 000000000000000000000000000`, rc 0. It ran 2026-11-09T00:13:24Z to 00:34:34Z, with origin/main at `19865e5a8` at its start and still there at its end, so no merge or second run was owed. Its `diff mutants` step was skipped (MUTANT_CMD unset); that step's figures are the `a41d9f110` run under `## Mutation proof`, with the same production lines. Its `closures` step printed `scoped recordings are covered; left to CI: tests/harness_headers.py`.

## Architecture score

`dS +0.0000 NULL`. No metric moved.

## Unpinned sites

The six survivors from `prepr.sh` step 6d at `a41d9f110`. Each is equivalent; none is a skipped test.
- `tools/audit/seat/merge_train.py:1224 RETURN_DEL`, the closing `return None` of `dispatch_order`: falling off the end returns None. Carry: dismissed: equivalent mutant, an implicit return is None
- `tools/audit/seat/merge_train.py:1243 CMP_BOUND` (`mt < bt` -> `mt <= bt`): `mt` and `bt` are `(utc, line index)` pairs for two different nonces, so they never share a line index and are never equal. Carry: dismissed: equivalent mutant, two dispatch records never share a registry line
- `tools/audit/seat/merge_train.py:1246 RETURN_DEL`, the closing `return None` of `stale_merge`: equivalent for the same reason as 1224. Carry: dismissed: equivalent mutant, an implicit return is None
- `tools/audit/seat/merge_train.py:5357 CALL_DEL`, the `_stale_verdict_self_test(check)` call in `_self_test`: deleting a self-test's call deletes its checks, which no self-test can detect in itself. Carry: dismissed: a self-test's own dispatch line, not a production site
- `tools/audit/seat/merge_train.py:5368 CALL_DEL`, the test's `sys.modules.setdefault("merge_train", ...)`: `_queue_self_test`, which runs before it, already set it, so the call is a no-op in that order. It is kept so the arm holds when run on its own. Carry: dismissed: equivalent mutant under the self-test's call order
- `tools/audit/seat/merge_train.py:5380 CALL_DEL`, the fixture's `calls.append(argv)`: killed at 962aad515 by S5380 above. The no-nonce-read null now asserts that the history read was recorded. Carry: dismissed: killed by 962aad515, the step ran before it

## Red checks

none. This head's CI starts at the handoff push. Every local check this diff reaches is green: the prepr run at `e53b46eda` refused `agreement lane` and `closures` only before those were repaired, and no PR exists yet.

## Forward-carry

- The triage record's figure "4 same" (dev/programme/triage/s6-batch127.md, P393) is one too high. The harness's unanchored nonce regex read a nonce quoted in PR 2465's verdict prose as the verdict's own. The harness is fixed in this diff, and the triage text is a measurement record, so it stays as written. Carry: dismissed: the instrument is fixed here and the record recounts, so no later stage's work changes
- review_strength.py's `NONCE_RE` (`^bus-nonce:\s*([0-9a-f]{32})`, no `$`) is a looser sibling reader of the same line. The agreement lane does not pair it, because its normalised source differs. The two diverge only on a verdict file that has a line-start `bus-nonce:` line other than the exact one ahead of the exact line. This seat did not enumerate the verdict refs for one, and this diff does not touch that reader. Carry: dismissed: a sibling reader outside this group's files, named here so the owner of review_strength.py can pair it in agreement.mjs

## Friction

none
