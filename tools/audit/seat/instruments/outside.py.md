# `outside.py`

- `outside.py` (tools/pr/) — the outside-contributor contract (decision
  0017): whether a pull request is an allowlisted contributor's fork one,
  which class each path it changes is (F free, R refused, O owner-read;
  default deny), and whether its class-O read is the owner's.
  `check --repo O/R --pr N [--ref REF]` is the whole contract at the live
  head: rc 0 admitted, 1 refused (one `REFUSE:` line per reason), 3 not an
  outside pull request; `--early` (pr-contract) prints a class-O read still
  owed as `PENDING:` instead of refusing, and with `--pull-json FILE` judges
  the pull request from that file with no token and no API call (so it reads
  neither the reviews nor the other pull requests at the head). `classify --pr N PATH...` prints
  each path's class. `cross --repo O/R --pr N` answers whether the head is
  cross-repository (rc 0 yes, 3 ours, 1 unread), the one definition
  (`cross_repository`) the train and `merge_pr.sh` call. `approve --repo O/R --pr N --head SHA --mandate ID`
  posts the one mandated class-O approval, through the reviews API with
  `commit_id` the head read, and reads it back. When: `bus.sh adopt` runs
  main's copy as the gate; our class-O read seat returns through `approve`;
  the merge train reads `check` again at the landing head (part 2). Refusal:
  any unread fact (the allowlist, CODEOWNERS, the pull request, the review
  list, the mandate) refuses; `approve` refuses, posting nothing, without
  `--mandate`, under a mandate not in force now with scope all, on a head
  that moved, on a diff with a class-R path or no class-O one, under a `gh`
  account that is not the owner's, and over the owner's own change request.
  It executes, checks out and imports nothing of the head. The programs it
  reads the rules from (`policy_lint.mjs`'s policy set, `closure.py`'s gate
  files, `budget_raise_gate.py`'s owner, patterns and mandate reading) are
  its own tree's; the allowlist and CODEOWNERS are read with `git show` at
  `--ref`. **No tool of ours pushes a fork's head to a branch of origin**:
  `app_approve.sh --carry` reads a branch tip of origin as a head of ours.
