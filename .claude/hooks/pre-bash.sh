#!/bin/bash
# PreToolUse on Bash.
#
# WHAT IT REFUSES: a process killed by NAME at command position -- `pkill`,
# `killall`, or `kill` fed by `pgrep`. The seat preamble says "kill only by
# PID" and nothing enforced it at the moment it was broken: a seat ran
# `pkill -f` with an empty pattern while restarting its watch loop, and on
# 2026-10-15 a fixer's `pkill -f tests/entities.py` killed every seat's run of
# that script on the shared host. The rule lived in process state only.
# `kill 1234`, `kill $!` and `kill $(cat run.pid)` stay allowed: that is the
# rule's own alternative.
#
# AT COMMAND POSITION means the word runs: at the start, or after `;` `&&` `||`
# `|` `&` `(` `$(` a backtick, a newline, and past `sudo`, `xargs`, `env` and
# the like. The same words inside a quoted argument (`echo "never pkill"`),
# a comment, a heredoc body or an argument of `grep` do not run and are not read.
# `bash -c '...'` and `eval` bodies are read, because they do run. Both arms
# read the commands this one parser finds (HPO_PRE_BASH_PARSE_PY).
#
# KNOWN GAPS, by design: a name held in a variable (`$K x`), a wrapper option
# that takes a value (`sudo -u root pkill x`) and a pid list built on an earlier
# statement (`p=$(pgrep x); kill $p`) are not seen. A name-matching hook that
# guessed at those would refuse ordinary commands.
#
# IT FAILS OPEN, as pre-edit.sh does. A payload this script cannot parse exits
# 0. Exit 2 is reserved for a command it has positively identified.
#
#   .claude/hooks/pre-bash.sh --self-test
#
set -uo pipefail

SELF_TEST=0
[ "${1:-}" = "--self-test" ] && SELF_TEST=1

# HPO_PRE_BASH_PARSE_PY
# # THE ONE COMMAND-POSITION PARSER, shared by both arms: `decide` prepends this
# # block to each arm's block, so neither arm splits a command on its own.
# import json, re, sys
# try:
#     payload = json.loads(sys.argv[1])
# except Exception:
#     sys.exit(0)                          # unparseable -- fail open
# ti = payload.get("tool_input") if isinstance(payload, dict) else None
# cmd = ti.get("command") if isinstance(ti, dict) else None
# if not isinstance(cmd, str) or not cmd:
#     sys.exit(0)
#
# # Heredoc bodies are data, not commands: drop the lines between a `<<WORD`
# # line and the line that is WORD. `<<<` is a here-string, not a heredoc.
# lines, out, ends = cmd.split("\n"), [], []
# for ln in lines:
#     if ends:
#         if ln.strip() == ends[0]:
#             ends.pop(0)
#         continue
#     out.append(ln)
#     for m in re.finditer(r"(?<!<)<<-?\s*(['\"]?)([A-Za-z_][\w]*)\1", ln):
#         ends.append(m.group(2))
# text = "\n".join(out)
#
# WRAP = {"sudo", "doas", "xargs", "env", "nohup", "exec", "time", "command",
#         "nice", "stdbuf", "setsid", "timeout", "builtin", "!"}
# RESERVED = {"if", "then", "else", "elif", "do", "while", "until", "{"}   # compound-command words: the next word is still a command
# SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
# SEP = " \t\n;&|()"
# cmds = []                                # (statement id, command word, argv), in the order run
# stmt = 0
#
# def parse(s, i, close):
#     """Scan s from i; record every simple command at command position. Returns the index past `close`."""
#     global stmt
#     n, at, prev, shellc = len(s), True, None, False
#     argv, body = None, None              # this scan's open command; the words of an eval
#     def end():                           # a separator closes the open command
#         nonlocal argv, body
#         if body:
#             parse(" ".join(body), 0, None)   # the body of eval runs
#         argv = body = None
#     while i < n:
#         c = s[i]
#         if close == ")" and c == ")":
#             end(); return i + 1
#         if close == "`" and c == "`":
#             end(); return i + 1
#         if c in " \t":
#             i += 1; continue
#         if c in ";\n":
#             end(); stmt += 1; at = True; i += 1; continue
#         if c == "&":
#             end(); i += 2 if s[i:i+2] == "&&" else 1
#             stmt += 1; at = True; continue
#         if c == "|":
#             end()
#             if s[i:i+2] == "||":
#                 i += 2; stmt += 1
#             else:
#                 i += 1
#             at = True; continue
#         if c == "(":
#             end(); at = True; i += 1; continue
#         if c == ")":
#             end(); at = True; i += 1; continue
#         if c == "#":
#             while i < n and s[i] != "\n":
#                 i += 1
#             continue
#         w, quoted_sub = "", False
#         while i < n:
#             ch = s[i]
#             if close == "`" and ch == "`":
#                 break
#             if close == ")" and ch == ")":
#                 break
#             if ch in SEP and not (ch == "&" and w[-1:] in ("<", ">")):
#                 break
#             if ch == "\\" and i + 1 < n:
#                 w += s[i+1]; i += 2
#             elif ch == "'":
#                 j = s.find("'", i + 1)
#                 j = n if j < 0 else j
#                 w += s[i+1:j]; i = j + 1
#             elif ch == '"':
#                 i += 1
#                 while i < n and s[i] != '"':
#                     if s[i] == "\\" and i + 1 < n:
#                         w += s[i+1]; i += 2
#                     elif s[i:i+2] == "$(":
#                         i = parse(s, i + 2, ")"); quoted_sub = True
#                     elif s[i] == "`":
#                         i = parse(s, i + 1, "`"); quoted_sub = True
#                     else:
#                         w += s[i]; i += 1
#                 i += 1
#             elif s[i:i+2] == "$(":
#                 i = parse(s, i + 2, ")"); quoted_sub = True
#             elif ch == "`":
#                 i = parse(s, i + 1, "`"); quoted_sub = True
#             else:
#                 w += ch; i += 1
#         if shellc:
#             shellc = False
#             parse(w, 0, None)            # the body of bash -c runs
#         if at:
#             base = w.rsplit("/", 1)[-1]
#             if re.fullmatch(r"\w+=.*", w) or base in WRAP or w in RESERVED or (w.startswith("-") and prev in WRAP):
#                 pass                     # still at command position
#             else:
#                 at = False
#                 if base:
#                     argv = [w]
#                     cmds.append((stmt, base, argv))
#                     if base == "eval":
#                         body = []
#         else:
#             if w == "-c" and prev in SHELLS:
#                 shellc = True
#             if w and argv is not None:
#                 argv.append(w)
#             if w and body is not None:
#                 body.append(w)
#         if at or w:
#             prev = w.rsplit("/", 1)[-1]
#     end()
#     return i
#
# try:
#     parse(text, 0, None)
# except Exception:
#     sys.exit(0)                          # anything unforeseen -- fail open
# HPO_PRE_BASH_PARSE_PY_END

# HPO_PRE_BASH_PY
# # First arm: a kill by name, over the parse block's `cmds`.
# feeds = {s for s, b, _ in cmds if b == "pgrep"}
# for s, b, _ in cmds:
#     if b in ("pkill", "killall") or (b == "kill" and s in feeds):
#         what = "kill fed by pgrep" if b == "kill" else b
#         print(f"`{what}` kills processes by name or pattern, and on a shared host "
#               "that reaches other seats' runs (the 2026-10-15 `pkill -f tests/entities.py` "
#               "killed every seat's run of that script). The preamble rule is: kill only "
#               "by PID. Start the process with `&`, keep `$!` or write a pidfile, and "
#               "`kill \"$pid\"`.")
#         sys.exit(1)
# HPO_PRE_BASH_PY_END

# HPO_PRE_BASH_GUARD_PY
# import os, subprocess
# # Second arm: the orchestrator's checkout is what beatd, tick_loop.sh and
# # cloud_relay.sh run their scripts from, and bash reads a script
# # incrementally, so a command that moves its HEAD or working tree corrupts
# # them (2026-10-31, gap 4 of R10-FLY-STANDING-CONTRACTS). It reads the parse
# # block's `cmds` -- so `bash -c`, `eval`, `( )` and `$( )` bodies are seen --
# # following `cd` and `pushd` in the order the commands appear (a `cd` inside a subshell is
# # carried past its close, which can only refuse more). INERT unless
# # $HPO_STATE_DIR/orch-checkout names a directory; fails open on anything odd.
# MOVERS = {"checkout", "switch", "reset", "pull", "merge", "rebase", "stash", "clean", "restore"}
# try:
#     state = os.environ.get("HPO_STATE_DIR", "")
#     marker = open(os.path.join(state, "orch-checkout")).read().strip() if state else ""
#     if not marker or not os.path.isdir(marker):
#         sys.exit(0)
#     guarded = os.path.realpath(marker)
#     def toplevel(d):
#         r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
#         return os.path.realpath(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else ""
#     def under(d, p):
#         return os.path.realpath(os.path.join(d, os.path.expandvars(os.path.expanduser(p))))
#     cur = payload.get("cwd") or os.getcwd()
#     for _, b, w in cmds:
#         if b in ("cd", "pushd"):
#             to = [a for a in w[1:] if not a.startswith("-")]
#             if to:
#                 cur = under(cur, to[0])
#             continue
#         if b != "git":
#             continue
#         d, i = cur, 1
#         while i < len(w) and w[i].startswith("-"):
#             if w[i] == "-C" and i + 1 < len(w):
#                 d = under(d, w[i + 1]); i += 2
#             elif w[i] in ("-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(w):
#                 i += 2
#             else:
#                 i += 1
#         sub = w[i] if i < len(w) else ""
#         if sub in MOVERS and os.path.isdir(d) and toplevel(d) == guarded:
#             print(f"`git {sub}` would move HEAD or the working tree of the orchestrator checkout "
#                   "($HPO_STATE_DIR/orch-checkout), which beatd, tick_loop.sh and cloud_relay.sh run their "
#                   "scripts from; bash reads a script incrementally, so the move corrupts them. Read main with "
#                   "`git -C <checkout> show origin/main:<path>` or work in a worktree of your own.")
#             sys.exit(1)
# except SystemExit:
#     raise
# except Exception:
#     sys.exit(0)                          # anything unforeseen -- fail open
# HPO_PRE_BASH_GUARD_PY_END

extract() { # $1 the marker name; stdout: that block as a python program
  sed -n "/^# $1\$/,/^# $1_END\$/{
    /^# $1\$/d
    /^# $1_END\$/d
    s/^# //
    s/^#\$//
    p
  }" "$0"
}

arm() { # $1 an arm's marker, $2 the payload: the shared parser, then that arm
  { extract HPO_PRE_BASH_PARSE_PY; extract "$1"; } | python3 - "$2"
}

decide() { # $1 the raw payload; stdout: a refusal message, or nothing
  # Prefilter: no `kill` anywhere in the payload means the first arm cannot
  # match, and a bash `case` costs about 3 ms where a python start costs about
  # 26. The second arm needs `git` in the payload AND a marker file.
  case "$1" in
    *kill*) arm HPO_PRE_BASH_PY "$1" ;;
  esac
  case "$1" in
    *git*) [ -n "${HPO_STATE_DIR:-}" ] && [ -f "$HPO_STATE_DIR/orch-checkout" ] \
             && arm HPO_PRE_BASH_GUARD_PY "$1" ;;
  esac
  return 0
}

if [ "$SELF_TEST" = 1 ]; then
  pass=0; fail=0
  st() { # want(refuse|allow), command, label
    local payload out got
    payload=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","tool_input":{"command":sys.argv[1]}}))' "$2")
    out=$(decide "$payload")
    got=allow; [ -n "$out" ] && got=refuse
    if [ "$got" = "$1" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$3"
    else fail=$((fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$3" "$got" "$1"; fi
  }
  st refuse 'pkill -f ""'                          "pkill with an empty pattern is refused"
  st refuse 'pkill -f tests/entities.py'           "pkill -f on a script path is refused"
  st refuse 'pkill python3'                        "pkill by name is refused"
  st refuse 'killall python3'                      "killall is refused"
  st refuse 'kill $(pgrep -f x)'                   "kill fed by pgrep in a substitution is refused"
  st refuse 'pgrep -f x | xargs kill'              "pgrep piped to xargs kill is refused"
  st refuse 'cd /tmp && pkill -f x'                "pkill after && is refused"
  st refuse 'sudo pkill x'                         "pkill behind sudo is refused"
  st refuse 'true; echo hi
pkill x'                                           "pkill on a later line is refused"
  st refuse 'bash -c "pkill -f x"'                 "pkill inside bash -c is refused"
  st refuse 'kill `pgrep -f x`'                    "kill fed by pgrep in backticks is refused"
  st allow  'kill 1234'                            "kill by literal PID is allowed (null control)"
  st allow  'kill $!'                              "kill of the last background PID is allowed (null control)"
  st allow  'kill $(cat run.pid)'                  "kill from a pidfile is allowed (null control)"
  st allow  'kill -9 1234; pgrep -f x'             "pgrep in another statement than kill is allowed (null control)"
  st allow  'grep -n pkill file'                   "pkill as an argument of grep is allowed (null control)"
  st allow  'git log --grep=killall'               "killall inside an option is allowed (null control)"
  st allow  'echo "never pkill"'                   "pkill inside quoted echo text is allowed (null control)"
  st allow  "echo 'killall x' | cat"               "killall inside single quotes is allowed (null control)"
  st allow  'cat <<EOF
pkill -f x
EOF'                                               "a heredoc body holding pkill is allowed (null control)"
  st allow  'echo hi # pkill x'                    "pkill in a comment is allowed (null control)"
  st refuse 'if true; then pkill x; fi'            "pkill after a then is refused"
  st allow  'echo then pkill x'                    "then as an echo argument is allowed (null control)"
  st allow  'git status'                           "a command without the substring kill takes the prefilter path"
  # SECOND ARM: the orchestrator-checkout guard, over a throwaway repository
  # and state directory (HPO_STATE_DIR/orch-checkout names the repository).
  gtmp=$(mktemp -d); mkdir -p "$gtmp/state" "$gtmp/orch" "$gtmp/other"
  . "$(dirname "$0")/../../tests/throwaway_git.sh"
  throwaway_git_init "$gtmp/orch" -q; throwaway_git_init "$gtmp/other" -q
  printf '%s\n' "$gtmp/orch" > "$gtmp/state/orch-checkout"
  gst() { # want(refuse|allow), command, cwd, label, [state dir]
    local payload out got
    payload=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","cwd":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$2" "$3")
    out=$(HPO_STATE_DIR="${5-$gtmp/state}" decide "$payload")
    got=allow; [ -n "$out" ] && got=refuse
    if [ "$got" = "$1" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$4"
    else fail=$((fail+1)); printf '  FAIL %s (got %s, wanted %s)\n' "$4" "$got" "$1"; fi
  }
  gst refuse 'git pull'                         "$gtmp/orch"  "guard: git pull in the orchestrator checkout is refused"
  gst refuse "git -C $gtmp/orch checkout main"  "$gtmp/other" "guard: git -C into the checkout is refused"
  gst refuse "cd $gtmp/orch && git reset --hard" "$gtmp/other" "guard: cd then reset is refused"
  gst refuse 'git -c x=y merge origin/main'     "$gtmp/orch"  "guard: git -c before the subcommand is read past"
  # the fix review's five probes (verdict/3294): bodies the shared parser reads
  gst refuse "bash -c 'git pull'"               "$gtmp/orch"  "guard: a bash -c body is read"
  gst refuse 'eval git pull'                    "$gtmp/orch"  "guard: an eval body is read"
  gst refuse "(cd $gtmp/orch && git pull)"      "$gtmp/other" "guard: a subshell's cd is followed"
  gst refuse "echo x \$(git -C $gtmp/orch checkout main)" "$gtmp/other" "guard: a \$( ) substitution is read"
  gst refuse "sh -c 'cd $gtmp/orch; git reset --hard'" "$gtmp/other" "guard: a cd inside sh -c is followed"
  # the second review's compound-command and pushd probes (verdict 6718280627)
  gst refuse "if true; then git -C $gtmp/orch pull; fi" "$gtmp/other" "guard: a then body is read"
  gst refuse "pushd $gtmp/orch >/dev/null; git reset --hard" "$gtmp/other" "guard: pushd is followed like cd"
  gst allow  "echo then git pull"               "$gtmp/orch"  "guard: then as an echo argument is allowed (null control)"
  gst allow  "echo 'git pull' > notes.txt"      "$gtmp/orch"  "guard: git pull as quoted echo text is allowed (null control)"
  gst allow  'git status'                       "$gtmp/orch"  "guard: a read-only git command is allowed (null control)"
  gst allow  "git -C $gtmp/orch show origin/main:README.md" "$gtmp/other" "guard: show of main is allowed (null control)"
  gst allow  'git pull'                         "$gtmp/other" "guard: pull in another repository is allowed (null control)"
  gst allow  'git pull'                         "$gtmp/orch"  "guard: inert without HPO_STATE_DIR (null control)" ""
  rm -f "$gtmp/state/orch-checkout"
  gst allow  'git pull'                         "$gtmp/orch"  "guard: inert without the marker file (null control)"
  rm -rf "$gtmp"
  # AND THE SCRIPT ITSELF, end to end over its real stdin: every case above
  # drives `decide`, none of them the wrapper that reads the payload and turns a
  # message into an exit status -- where pre-edit.sh was inert once.
  e2e() { # want-rc, payload, label
    printf '%s' "$2" | bash "$0" >/dev/null 2>&1
    local got=$?
    if [ "$got" -eq "$1" ]; then pass=$((pass+1)); printf '  ok   %s\n' "$3"
    else fail=$((fail+1)); printf '  FAIL %s (rc %s, wanted %s)\n' "$3" "$got" "$1"; fi
  }
  e2e 2 '{"tool_name":"Bash","tool_input":{"command":"pkill -f x"}}' "END TO END: pkill exits 2"
  e2e 0 '{"tool_name":"Bash","tool_input":{"command":"kill 1234"}}'  "END TO END: kill by PID exits 0 (null control)"
  e2e 0 'not json at all with kill in it'                            "END TO END: an unparseable payload fails OPEN"
  e2e 0 '{"tool_name":"Bash","tool_input":[]}'                       "END TO END: a tool_input that is not an object fails OPEN"
  printf '\n%s passed, %s failed\n' "$pass" "$fail"
  [ "$fail" -eq 0 ] || exit 2
  exit 0
fi

PAYLOAD=$(cat)
# The verdict is the OUTPUT, not decide's status (the lesson pre-edit.sh paid
# for): a crash produces no output, which is the fail-open path.
MSG=$(decide "$PAYLOAD")
if [ -n "$MSG" ]; then
  printf 'pre-bash: %s\n' "$MSG" >&2
  exit 2
fi
exit 0
