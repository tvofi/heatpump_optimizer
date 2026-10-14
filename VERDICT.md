Fix review: merge 490bd805da7d3ca75b169bbe07e4397cff3f5604
bus-nonce: 4182e69742636353e684f22e644065be
reviewer: r10-d15-checker-reviewer; round 1; measured head 490bd805da7d3ca75b169bbe07e4397cff3f5604 from a detached worktree; roles/ diff vs origin/main empty.

RESULT checker head (main's drivers) rc=0 180 passed 0 failed; pending: D15; bundle pins "not declared"
RESULT checker head + #2209 overlay (audit-find.js, scopes/rotation/finding.schema, D15.md from origin/fix/r10-d15; #2209's grader files byte-identical to this head) rc=0 180/0; pending: none; bundle armed D15-s2,s3,s1
RESULT main's checker (554e2ecfa) on head tree rc=1: worktree lists agree FAIL (ISOLATED_DIMS has D15, ISOLATED not) -- the defect this PR fixes
RESULT main's checker on #2209 overlay rc=1: both D15-s1 negative controls FAIL under #2209's schema -- confirms the D16-s1 move
RESULT own mutants (#2209 overlay): A unfinished-text KILLED(bundle pin), B bundle-path-dropped KILLED, G2 export-path-dropped KILLED, C bundle-leaked-to-all KILLED(null control), D abs-path-throw-removed KILLED(pin 3), E D15-off-ISOLATED KILLED(2), F D15-off-ISOLATED_DIMS KILLED(2)
RESULT own mutants (head, pending tolerance): H known=filter(isolated) KILLED(new pending pin), I known=baseline KILLED(2), K known=[] KILLED(2) -- the tolerance cannot hide a briefed or declared dimension
RESULT survivor J: known=filter(dims) only (briefs disjunct dropped) 180/0 -- equivalent: a briefed-not-declared dimension is already refused by "briefs/Dn.md has no DIMS entry"
RESULT survivor G: renaming BUNDLE_DIMS in audit-find.js disarms all three bundle pins silently (180/0) -- same declared-constant arming as ROUND_DIR/CURRENT (precedent); non-blocking; could arm on D15's brief existing once #2209 lands
RESULT prepare_baseline --wall/--strip/--copy-self-test rc=0 each (python 3.14.7)
RESULT policy/ownership: tools/policy/*.mjs and tools/audit/*.sh are pinned (restored from base, governance.yml), not in CODEOWNERS, not POLICY_GLOBS (.md-only) -- not policy, not code-owned
RESULT check-runs at head: 45; one failure nightly-status (main's nightly, diff does not reach it; body answers it); same single red at 29c14042b; pr-contract re-ran 23:04:47Z success; graders-head-copy success
RESULT PR body on GitHub: 4422 chars, non-empty; names head 490bd805da7d3ca75b169bbe07e4397cff3f5604. Minor: says "two files" -- the record commit adds a third (delivery/2214.md)
RESULT VERSION/manifest/notes untouched; class: no other D15/D0-14-bounded grader in tools/tests/.claude (git grep)
