#!/bin/bash
# Reviewer's probe (builder: the reviewer, not the finder): two topics' refusals measured at once
# share <cache>/tree. usage: race.sh <pr_args.sh at head> <scratch>
set -u
LIB=$1; T=$2; rm -rf "$T"; mkdir -p "$T/stub"
o=$T/o; git init -q -b main "$o"; git -C "$o" config user.email r@r; git -C "$o" config user.name r
mkdir -p "$o/tools/pr"; cat > "$o/tools/pr/prepr.sh" <<'STUB'
#!/bin/bash
[ "${1:-}" = --self-test ] || exit 0
sleep "${STUB_SLEEP:-0}"
r=0
[ ! -e "$STUB_DIR/hostfail" ] || { echo "  FAIL a tool this host lacks (got 127, wanted 0)"; r=2; }
for f in README.md tools/pr/prepr.sh; do [ -r "$f" ] || { echo "  FAIL $f cannot be read"; r=2; }; done
while read -r f; do [ "$(tail -n 1 "$f")" != "# BROKEN" ] || { echo "  FAIL $f reads broken"; r=2; }; done < <(git ls-files 2>/dev/null)
exit $r
STUB
printf 'a\n' > "$o/README.md"; git -C "$o" add -A; git -C "$o" commit -q -m main; M=$(git -C "$o" rev-parse HEAD)
mk() { git -C "$o" checkout -q --detach "$M"; printf '%s\n' "$2" >> "$o/$1"; git -C "$o" add -A; git -C "$o" commit -q -m "$1 $2"; git -C "$o" rev-parse HEAD; }
A=$(mk README.md "topic a"); B=$(mk README.md "topic b"); X=$(mk README.md "# BROKEN")
printf '  REFUSE   self-test              1 failed   FAIL x\napp_push: REFUSE: the body did not pass tools/pr/prepr.sh\n' > "$T/st.log"
touch "$T/stub/hostfail"
hr() { STUB_SLEEP=${SL:-0} STUB_DIR=$T/stub bash -c '. "$1"; pr_host_refusal "$2" "$3" "$4" "$5" "$6"' _ "$LIB" "$o" "$T/st.log" "$1" "$M" "$T/cache" </dev/null; echo $?; }
echo "RESULT sequential: clean head A -> $(hr $A) (0 = host's), clean head B -> $(hr $B), broken head X -> $(hr $X) (1 = head's)"
for trial in 1 2 3; do
  rm -rf "$T/cache"
  (SL=3 hr $A > "$T/ra") & sleep 1; (SL=3 hr $B > "$T/rb") & wait
  echo "RESULT concurrent trial $trial, cold cache, both true host refusals: A -> $(cat $T/ra), B -> $(cat $T/rb); cached main sig: $(tr '\n' '|' < "$T/cache/$M.sig" 2>/dev/null || echo none)"
done
rm -rf "$T/cache"; hr $A >/dev/null   # warm cache, honest
for trial in 1 2 3; do
  (SL=3 hr $A > "$T/ra") & sleep 1; (SL=3 hr $X > "$T/rb") & wait
  echo "RESULT concurrent trial $trial, warm cache: clean A -> $(cat $T/ra) (want 0), broken X -> $(cat $T/rb) (want 1)"
done
for trial in 1 2 3; do
  (SL=3 hr $X > "$T/ra") & sleep 1; (SL=3 hr $A > "$T/rb") & wait
  echo "RESULT concurrent trial $trial, warm cache, X first: broken X -> $(cat $T/ra) (want 1), clean A -> $(cat $T/rb) (want 0)"
done
for trial in 1 2 3; do
  rm -rf "$T/cache"
  (SL=3 hr $A > "$T/ra") & sleep 1; (SL=3 hr $X > "$T/rb") & wait
  echo "RESULT concurrent trial $trial, COLD cache: clean A -> $(cat $T/ra) (want 0), head-broken X -> $(cat $T/rb) (want 1; 0 = the head's own break called the host's)"
done
echo "RESULT after that overlap, alone, cache as the overlap left it ($(tr '\n' '|' < "$T/cache/$M.sig")): clean A -> $(hr $A) (want 0), clean B -> $(hr $B) (want 0), broken X -> $(hr $X) (want 1)"
