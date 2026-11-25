# BLOCKED: r11-owner-flowcap

Question: The dispatch at c995ee8f asks a fixer to build approved design fa8cd134 (R11-OWNER-FLOWCAP) from base d9100de7, but that base already contains it: PR #3866 merged as d2128054 (2026-11-25 17:14 +0100), and custom_components/heatpump_optimizer/flow_limit.py is on main. Is there a remaining piece of fa8cd134 this seat should build, or is the dispatch stale and the roster stage due to move past "a fixer seat is building"?

Evidence:
- `git merge-base --is-ancestor origin/fix/r11-owner-flowcap-pr d9100de` succeeds (PR head 086341d6 is in the base).
- `git log --grep=3866 d9100de` names d2128054 "Merge pull request #3866 from tvofi/fix/r11-owner-flowcap-pr".
- The comms inbox held no command at this fire.

No code was written and no other ref was touched.
