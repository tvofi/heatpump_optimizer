# BLOCKED: r11-pre-machinery-limiter, conflict resolution with origin/main

Head: 2986495e9cc46e911d37945166c18dd13c60d89a (handoff/r11-pre-machinery-limiter)
origin/main: e30408f7881cd5602a2c4d7ea9517b0d765652f6
Conflict (git merge-tree --write-tree origin/main HEAD): dev/governance/roles/proposal-triage.md only; all other files auto-merge.

The conflicting hunk is the **Machinery** paragraph's last sentence. Both sides
rewrote the same base sentence (the `severity` `low`/`normal` rule) into the same
card-P2 rule, in different words:

- this PR: "code (outside `custom_components/`) meets both (over 20% to add) at any
  / roster `severity`; only a red required check on main or a blocked production
  / pull request skips them (owner card P2), as do a root-cause
  / countermeasure, closeout and an owner directive."
- main (#3626/#3566): "... at any / severity; a red required check on `main`, a
  blocked production pull request, a / root-cause countermeasure, closeout or an
  owner directive skips them (tvofi, 2026-11-13, card P2)."

Both continue the shared line ending "at any", so a verbatim union of the two
line sets leaves one side starting mid-sentence ("severity; ...") and states the
same rule twice in a role contract. No verbatim union reads as one sentence.

Question: may the resolution take main's three lines alone (they carry every
element of this PR's three: any severity, red required check on main, blocked
production PR, root-cause countermeasure, closeout, owner directive, card P2),
instead of the verbatim union of both sides the brief names?
