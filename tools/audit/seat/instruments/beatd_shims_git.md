# `beatd_shims/git`

- `beatd_shims/git` — the beat jobs' `git`, reached only through the `PATH`
  `beatd.py` builds (never `shims/`, which the sweep and `roster_queue.py`
  prepend). A `fetch` or `pull` failing on `cannot lock ref` is re-run at most
  `HPO_GIT_RETRIES` (default 2) more times, each retry a line of
  `HPO_GIT_SHIM_LOG`; anything else is `exec`'d unchanged. The real git is
  `HPO_REAL_GIT` when that is a regular executable file and not a shim, else
  the first such `git` on `PATH`, any copy recognised by its line-2 marker
  `# hpo-git-shim`. Refusal: no real git, `git shim: no real git on PATH`, rc
  127; it never execs itself. Tested by `beatd.py --self-test`, case (a)6.
