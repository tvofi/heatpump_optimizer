Fix review: merge 90bab078d19dd6aebba140fa360576b7780a560a

This is a markers-only re-issue of the earlier verdict at this exact head, routing its items. Re-check only: head unchanged (PR head and fetched ref both 90bab078d19dd6aebba140fa360576b7780a560a); `git merge-tree --write-tree origin/main 90bab078d19dd6aebba140fa360576b7780a560a` is clean (exit 0); check-runs on this head: 32 success, 16 skipped, 1 failure (`nightly-status`, a scheduled-status row and not a PR gate; nothing else red, none pending). The code was not re-reviewed; the earlier merge verdict stands.

Carry: dismissed: observation only, nothing owed by this PR (item b579380b)

bus-nonce: c2c5075c4ebcb40ffb1e164a8ee4f777
