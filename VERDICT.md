Fix review: blocked ea459c0b5f6b4d753394935dfb49e5386480fd40 class-open: tests/gate_lock.py mark_unleased/_unleased torn write destroyed as unparseable

bus-nonce: 4264d0dad8305e369491518f2576b6b8

Round 1 of review. Measured head `ea459c0b5f6b4d753394935dfb49e5386480fd40` (still the branch head at verdict time); role files on main unchanged since the merge base.

## Block

The class this fix names is "a non-atomic write whose torn, empty file a reader parses as unparseable and destroys" (RCA section 4: "The slot pool was the only path where an unreadable file is destroyed"). That rule, run over `tests/gate_lock.py`, returns a seam the diff does not touch and the body does not disposition: `mark_unleased` writes its marker with `path.write_text` (create/truncate, then write), and `_unleased` (read by `slots_status`) does `int(_fields(path.read_text()).get("pid", ""))`, so an empty marker raises `ValueError` and is unlinked. A concurrent `slots_status` therefore deletes the witness of a live unleased run, which is the visibility `mark_unleased`'s docstring says a failed take owes. Reviewer-built probe (`ev/unleased_probe.py`, my own instrument, not the finder's): a writer calling `mark_unleased` 4000 times beside a polling `_unleased` found the marker gone right after the write 1522, 1618 and 1542 times in three runs, and an empty marker is deleted by a single `_unleased` call (`ev/unleased-probe.txt`). Fix (same shape as `Owner.write`: temp file + `os.replace`), or disposition it in the body/RCA with a reason.

## Findings

- Surviving mutant M4: removing `finally: tmp.unlink(missing_ok=True)` from `Owner.create` leaves every acceptance check green, so every successful create could leak a `.create-*` hard link into the pool directory unpinned. A case asserting the pool directory holds only slot/ticket/flock files after a take would kill it. Carry: rca-gate-lease-flake
- RCA section 4 states "Ticket files (`_enqueue`) are also written non-atomically"; at this head `_enqueue` writes `_ticket_tmp` then `os.link`/`os.replace`, which is atomic. The statement is wrong and should be corrected in `dev/audit/rca/R10-RCA-GATE-LEASE-FLAKE.md`. Carry: rca-gate-lease-flake

## Evidence

- Mutation proof (`ev/mutants.txt`): `Owner.write` reverted kills `torn_write` (torn reads 22588 and 18135; the body's 3745/6067/5300 are a thread-timing count, not reproducible to the digit, same order); `Owner.create` reverted and `link` swapped for `replace` both kill `torn_create` with `winners=['rival', 'a']`. Unmutated head: `ALL 31 gate lock acceptance checks PASSED` three times (`ev/head-accept.txt`), matching the body's null control and count of 31 (30 with the create case absent is consistent).
- Finder's harness: the finding's detector is the committed `one_winner` case; the RCA states it was not re-triggered under load, and neither did I. The two new deterministic cases are the fixer's own and are disclosed as such in the RCA.
- Merge: `git merge-tree --write-tree origin/main <head>` exit 0, tree 743da297f84d6d179f219a49c2fedc6fa44ad630 (`ev/merge-tree.txt`); no claim file touched, so no driver run.
- VERSION, manifest version and RELEASE_NOTES heading untouched (`ev/version-untouched.txt`; CI's version-edit step agrees).
- Body head line names `ea459c0b5…`, the head measured.
- CI at this head (check-runs API, 13:44Z): `pr-contract / pr-contract` failure at the code-scanning wait step while `codeql / Analyze (python)` was still in progress; `gate` failure with "run(s) [40099071689] at this head are still being judged". `tests / fast (3.14)`, `tests / coverage`, `tests / closures`, `governance / instrument-self-tests` were in progress. The head's workflows had not all concluded, so no root-cause verdict on those reds is taken here; the block above does not depend on them.
- Figures: body `## Figures` says none; the preflight figures check listed "1 of 30", "3745 of 4000", "1 of 31" as figures to answer (preflight reported no refusal).
