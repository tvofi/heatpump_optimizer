Fix review: blocked a771c0a0b7d664d24dab9caa3617c92d4593fcdf closures-under-scoped: closures is red again, UNDER-SCOPED tests/doc_claims.py really reads docs/site/docs.css, and closures-autofix printed skip-failed-recording, so the hand-merge of the Linux recording is owed

bus-nonce: 78cceb2f6baa48dc097017a5c28f5846

Round 3. PR #1864 (R9-WEB-3), head a771c0a0b7d664d24dab9caa3617c92d4593fcdf. I re-read the live head at 2026-10-02T22:54:30Z, after CI had finished, and it had not moved. The authored delta is 61ac08eb (tests/closures.json +3 lines, tests/doc_claims.py +7/-1). There is no new main merge. Evidence is in ev3/; HEAD.txt names the head.

## Owed (one line in tests/closures.json)

The inert_reads repair worked: the closures job (CI job id in ev3/check-runs3.json) no longer prints INERT READS UNDER-APPROXIMATED. In round 2, that check returned first and hid the next one. It now prints:

    UNDER-SCOPED: tests/doc_claims.py really reads 1 file(s) the committed closure does not list:
        docs/site/docs.css

An INERT read goes in both places. The recorder puts it in `files` as well as `inert_reads` (tests/closure.py:883-884). `docs/index.html` already sits in both doc_claims.py lists for the same reason.

closures-autofix printed `AUTOFIX: skip-failed-recording -- THE REPAIR DID NOT HAPPEN`. Under the dispatch's rule, the owed repair is therefore a hand-merge of the Linux recording.
- Add `docs/site/docs.css` to `tests/closures.json["tests/doc_claims.py"]`, keeping the round-3 inert_reads entry.
- The recording artifact is closure-recordings from run 37072797978.
- The `done` lines in the closures log all show exit 0, so I could not tell which recording carries the nonzero rc that the autofix keyed on. I did not download the artifact. The orchestrator may want that answered for the RCA-4 seat; it does not change this PR's repair.
- The body names `closures` already, so pr-contract is green. Its answer describes the round-2 cause and should add this half.

My round-2 verdict named only the inert_reads half. I could not see the second half then, because the check returns before it reaches the UNDER-SCOPED comparison.

## The new CSS patterns: proof is in, no hand pass owed

Four targeted mutants on the round-3 lines of `_site_css_external`, each run through `tests/doc_claims.py`. Baseline: `ALL 155 checks PASSED`.
- RESULT M1, `re.I` dropped from the url/@import regex: rc 1, `FAIL ... an uppercase URL() font is refused`
- RESULT M2, the image-set loop emptied: rc 1, `FAIL ... an image-set() string candidate is refused`
- RESULT M3, the image-set `findall` dropped: rc 1, the same FAIL
- RESULT M4, the external filter forced false: rc 1, the @import, URL() and image-set plants all FAIL

Each new pattern is pinned by its own planted control, so the fixer owes no separate hand pass for it.

## CI at this head

waitci: `DONE total=35`, NOTGREEN `closures`, `closures-autofix` and `nightly-status`. briefs, pr-contract, fast (3.14), coverage, coverage-ratchet and mutation are green. nightly-status is main's red, as before. CI ran harness_headers, deployment_shape, layout and structure, and none is red. I did not re-run them locally at this head; round 2's local layout, structure and policy_lint passes stand for the unchanged files.

Everything closed in round 2 is unchanged by this delta. The delta touches only `_site_css_external`, its controls and closures.json.
