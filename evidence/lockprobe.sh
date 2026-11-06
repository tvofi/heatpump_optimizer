# confirm()'s acquisition loop, copied verbatim from bus.sh at 520550ce (lines 676-684)
lk=$1
until mkdir "$lk" 2>/dev/null; do
  holder=$(cat "$lk/pid" 2>/dev/null)
  if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then
    sleep 1
  else
    rm -rf "$lk"
  fi
done
printf '%s\n' "$$" > "$lk/pid"; echo ACQUIRED
