# `owner_only.py`

- `owner_only.py` — the only way a session of an owner-only audit dimension
  starts, and the probe that refuses one able to publish. A dimension whose
  `dev/audit/config/scopes.json` entry carries `owner_only: true` publishes
  nothing; the closure is that no process of its run holds a credential that
  writes, which a second OS account (the seat account) gives and an
  instruction cannot. The owner runs, as that account:

        python3 -I tools/audit/seat/owner_only.py launch --private-root <abs dir, mode 700> \
          --owner-identity <the directory the App keys live in> [--deploy-key <file>]... \
          --model-env <the model credential's variable> --token-fd 3 -- <session command> 3< <read token file>

  It builds the session's environment from an allow-list under the private
  root, runs `corpus_mirror.py` first with the read credential on the
  descriptor, and starts the session only between two green probes.
  `--skip-mirror` reuses a corpus already there.
  - **`probe --private-root <dir>`** exits 0 only when the running account can
    read no owner identity directory or deploy key, gets no password from
    `git credential fill`, holds no agent socket, private key or
    credential-named variable (`CREDENTIAL_WORD`; the one model credential
    `launch` recorded in `probe.json` apart), reaches no logged-in `gh`,
    resolves `gh` to the seat shim in its owner-only mode, has a private root
    of mode 700 outside every work tree, and is no cloud session. It refuses
    an owner path that does not exist, and every question left unanswered:
    each of the three commands it runs passes only on that command's stated
    no (git: exit 128 naming no repository, or no username or password to
    read; `gh auth status`: exit 1 saying it is logged into no host), so a
    command that cannot be run, does not return, is killed, or exits any
    other way refuses. The work-tree question is asked with none of git's
    own variables in the environment (`GIT_DIR` and
    `GIT_CEILING_DIRECTORIES` cannot hide a tree), then as the session's git
    is configured. A credential-named variable is a segment ending with a
    word of `CREDENTIAL_WORD`, singular or plural; the rule errs to
    refusing (`MONKEY` ends with `KEY`). A line names a path or a variable,
    never a content. Both workflow drivers run it again in Prepare.
  - What the probe cannot see is in the script's docstring: a credential in
    a file it is not told of, one in a variable whose name says nothing of
    it, an owner path mistyped below a directory the account cannot enter,
    and, on a host with one account, the two-account property itself.
  `--self-test`: the probe over a fixture view of an account and over the
  real `Host` with the real git, the allow-list, the launch order, and one
  mutant per predicate.
