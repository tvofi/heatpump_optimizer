# Proposal triage, session s7, batch 64 (P293)

The rolling batch (V182) after batch 63 (#2974, merge verdict at `ddd88d3ed`, not yet merged).
Facts were read at origin/main `043b111d0` and on the remote `verdict/<pr>` refs.

## P293: carry_audit's evidence arm flags a reviewer's measurements as unrouted findings

Verdict: ACCEPT, narrowed, as one carry on R10-FLY-CARRY-DISPOSITION, which owns
`tools/audit/carry_audit.py`'s item classifier (its P-G carry, lead inheritance in `items()`). Two
of the three over-fire classes measured below are accepted. The proposal's first arm is rejected:
counting an `## Evidence` item as a finding only when LEAD leads it. That would drop two classes
the arm exists to catch, both pinned in the self-test today:
- "a defect left in place, not blocking, under the Evidence heading is a finding (#2465's shape)";
- "a deferral under the Evidence heading is a finding".

The second arm is accepted for a check's state only. Freeing every clause that calls something
"not this PR's" would free a pre-existing defect a reviewer found and left in place, which is a
finding that owes a route.

Source: the orchestrator's triage-queue line of 2026-10-30T00:33Z. The train parked #2969 (item
`c21695db`) and #2955 (item `158ad202`) on `## Evidence` items that are a reviewer's
measurements. The proposal: an evidence item counts only when LEAD leads it; the NONBLOCK
exemption covers any clause that calls a check not required or not this PR's; measure the
over-fire rate on the last 30 merge verdicts.

Instances. The sample is the 30 highest-numbered `verdict/<pr>` refs whose `VERDICT.md` opens
`Fix review: merge`, #2936 to #2974. Each was run through `carry_audit.items(text, True)` at
`043b111d0`.
- **Rate.** 9 items flagged in all. 7 of them are in `## Evidence` (`why` = `evidence`), in 5 of
  the 30 verdicts (#2937, #2939, #2955, #2959, #2969). On a read of each, none of the 7 is a
  finding. All 7 are measurements.
- **Class A: a red check that is not the PR's. 4 items.**
  - #2937 `19d896fa`: "the packet's red-unanswered refusal on it does not block here".
  - #2939 `f76b3ac3`: "nightly-status is not a required context and does not block: `gate`
    concluded green". The carve-out refuses to free it because of its `(?!\s*:)` guard.
  - #2955 `158ad202`: "it is NOT one of the required contexts on main-protect and does not block
    a merge".
  - #2959 `dde38e84`: "It is not this pull request's and does not block".
  The tripping word in each is NONBLOCK's `does not block`. `NOT_REQUIRED` frees only the exact
  shape `not (a )required (context|check)[,] [and] does not block`.
- **Class C: a NONBLOCK word inside a code span. 1 item.** #2969 `c21695db`: the CLI flag
  `` `--bump minor` ``, written twice, matches `\bminor\b`.
- **Class B: the review packet's own "advisory" label. 2 items.**
  - #2939 `3c055bc1`: "Its one advisory is hot-file: ...".
  - #2959 `50a530e7`: "The packet advisory `HPO_BUS_TRAIN_STATE is unset` ...".

Cost: S. All of it is in `items()` and `NOT_REQUIRED` in `tools/audit/carry_audit.py`, plus self-test
rows. `carry_audit.py` has no `policy_lint.mjs --budgets` row, and the `--budgets` output at
`043b111d0` names it 0 times. Benefit, measured: 5 of the 7 over-fires clear, and with them every
flagged item of #2937, #2955 and #2969. #2939 and #2959 keep one class-B item each. Each
over-fire costs a park and a dismissal line, or a body patch.

Binding: R10-FLY-CARRY-DISPOSITION is not started, and its other carries are larger. This carry
touches only the classifier (`items()` and `NOT_REQUIRED`), so the orchestrator may dispatch it on
its own ahead of the group's `landed` / `land-ops` carries, on the same file. Until it lands, the
workaround is unchanged: `Carry: dismissed (item <id>)`.

The carry:
1. **Code spans.** In a verdict's `## Evidence` arm, LEAD, DEFERRED and NONBLOCK read the item
   with code spans removed, using the module's own `CODE_SPAN`. A code span is a literal (a flag,
   a path, a check name), not the reviewer's prose. Fixture: #2969's `c21695db` text goes from
   flagged to clear.
2. **A check's state.** The `NOT_REQUIRED` carve-out also frees the clause in three shapes:
   - "not one of the required contexts" or "not a required context" followed by up to a few
     words (`on main-protect`), then `and does not block`, with an optional `a merge`;
   - "not this pull request's" or "not this PR's", joined by `and` to `does not block`, but only
     in an item that names a red check (a backticked `<job>` or `<caller> / <job>`, or the words
     `red` / `failure`);
   - the same clause ending in `:` when what follows names the gate's state (`gate` passed or
     green).
   Fixtures: #2937 `19d896fa`, #2939 `f76b3ac3`, #2955 `158ad202` and #2959 `dde38e84` go from
   flagged to clear.
3. **Null controls, each still a finding:**
   - the existing #2465-shape row (a defect left in place, not blocking);
   - the existing deferral row;
   - a new row, "a pre-existing defect in the parser is not this pull request's and does not
     block", which names no check;
   - "`minor` drift, noted for a later tightening", where DEFERRED reads outside the span.
4. **Mutation.** Each of the two arms has its own mutant: dropping the code-span strip re-flags
   `c21695db`, and dropping the new shapes re-flags the four class-A items.
5. **Declined: class B.** The two class-B items keep costing a dismissal each. Freeing "advisory"
   by context is the word-level second classifier the P-G carry declined (s4 P-G, carried
   verbatim on this group). An advisory a reviewer reports can be a real note, so it is not
   freed. Re-measure on the next 30 merge verdicts after the fix lands. If class B is still the
   only over-fire left and runs above 2 in 30, the lever is `review_packet.py` naming its
   environment advisories as such, not a carry_audit word list.
