Fix review: merge dae8e4195416218b58171a752ae18eb9264c5ada
bus-nonce: 17ad6d320d9a3a28beb37f0ea7e00e07

# Fix review -- PR #2891, triage batch 42 (P216)

Round 3. Reviewed head: dae8e4195416218b58171a752ae18eb9264c5ada, in a detached worktree at that
head, against origin/main b9e286254. `dev/governance/roles/` has no diff between the merge base and
origin/main. The head is authored code head `c36609f06` merged with main. The diff is
`s6-batch42.md` (+98) and its delivery row.

## Results

- Round-2 F1, the re-pricing, is answered. P216's `Cost:` now prices `CLAUDE.md` at its exact cap,
  and every figure re-derives at this head (`ev/claims.txt`):
  - `policy_lint.mjs --budgets` prints `CLAUDE.md 213 221 3605 3605 yes` and
    `proposal-triage.md 36 36 489 489`.
  - The estimator is `Math.round(r.bytes / 4) > tcap` at `policy_lint.mjs:1679`.
  - The drafted paragraph is 413 bytes on one line, so 414 with its newline, which is about 104
    tokens.
  - `CLAUDE.md` is 14,418 bytes, which rounds to 3,605. 14,421 bytes is the most the cap admits.
- Three routes are priced, and the verdict is re-ruled on that price:
  - A cap raise is rejected, because it needs `budget-raise-gate` and charges about 104 tokens to
    every session.
  - A role-file home is rejected.
  - An equal deletion is carried.
- The carry text itself states the equal-deletion requirement: "deletes at least 414 bytes of other
  `CLAUDE.md` text so the cap is unchanged", with no cap raise. If no cut is accepted, the carry
  closes unimplemented. With 3 bytes of headroom under the cap, a deletion of at least 414 bytes
  holds the cap even with the extra blank-line byte.
- Round-2 F2 is answered. The quote is verbatim. `dev/governance/roles/proposal-triage.md:32` reads
  "**You do not** implement, edit the roster or merge", and the ruling quotes exactly that in
  Instances and in the carry text.
- Destination: at roster tip `e3bc6128e`, `R10-ROUND-PLAYBOOK` is `not-started` and lists
  `CLAUDE.md` and `dev/audit/README.md`. It holds 7 carries, as the body says, and it is the only
  live group listing `CLAUDE.md`.
- Mutation proof re-run (`ev/mutation.txt`), with the op's `triage: ...#P216` cite prepended to the
  carry text:
  - `ruling_verdict` reads `Verdict: ACCEPT narrowed` as ACCEPT, and `triage_refusal` passes the
    carry.
  - Mutating the verdict to DEFER is refused, and so is renaming the heading ("no such entry").
  - The null control, a missing file, is refused.
- `git merge-tree --write-tree origin/main <head>` exits 0 (`ev/merge-tree.txt`). The packet refuses
  nothing. `carry_audit` routes 0 items, and the body's Forward-carry is `none`.
- Live checks at the head (`ev/check-runs.txt`): no failure, none pending at the final read.
  `VERSION`, the manifest and the notes heading are untouched.

## Findings

- F1 (non-blocking): "5 lines" for the drafted paragraph is an estimate. Wrapped at 80 columns, the
  file's prose width, it is 6 lines, so 7 with its blank line. That gives 213 + 7 = 220, still at or
  under the 221 cap, and the byte deletion the carry requires removes at least 5 lines in any case.
  Carry: dismissed: within cap at either count; the carry's byte rule binds
- F2 (non-blocking): the quoted carry text holds no `triage:` cite of its own. It depends on the op
  prepending `triage: dev/programme/triage/s6-batch42.md#P216`, as the ruling's lead-in says. Without
  the cite, `triage_refusal` passes the text unconditionally, because the text never names
  "proposal P<n>" or "triage P<n>". So the cite is load-bearing at the op. Carry: R10-ROUND-PLAYBOOK

## Check state at this head

Final read, at about 03:06Z (`ev/check-runs.txt`): 55 runs, 38 success, 17 skipped, 0 failure and 0
pending. `gate` and `pr-contract` concluded success.
