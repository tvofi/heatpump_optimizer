#!/bin/bash
# Reviewer's own instrument (not the fixer's arms): run the real loop (not --once)
# for ~14 s at --interval 2 with a stub relay that sleeps 9 s; count board writes,
# banners, relay starts, max concurrent relays, and whether every started relay finished.
# usage: rev_harness.sh <tick_loop.sh> <label> [relay_sleep]
L=$1; lab=$2; S=${3:-9}
t=$(mktemp -d)
cat > "$t/relay.sh" <<R
#!/bin/bash
n=\$(ls $t/run.* 2>/dev/null | wc -l); echo \$n >> $t/conc
touch $t/run.\$\$; echo start >> $t/starts; sleep $S; rm -f $t/run.\$\$; echo done >> $t/dones
R
printf '#!/bin/bash\ndate +%%s.%%N >> %s/ticks; echo BOARD\n' "$t" > "$t/tick.sh"
HPO_TICK_RELAY_WAIT=1 HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" \
  bash "$L" --interval 2 --out "$t/b.txt" > "$t/out" 2>&1 & lp=$!; sleep 14; kill $lp; wait $lp 2>/dev/null
sleep $((S+3))
ticks=$(wc -l < "$t/ticks" 2>/dev/null || echo 0)
starts=$(grep -c start "$t/starts" 2>/dev/null || echo 0)
dones=$(grep -c done "$t/dones" 2>/dev/null || echo 0)
maxc=$(sort -n "$t/conc" 2>/dev/null | tail -1)
running=$(grep -c 'relay=running' "$t/out")
late=$(grep -c '^TICK-RELAY' "$t/out")
echo "RESULT $lab relay_sleep=$S ticks_in_14s=$ticks banners=$(grep -c '^TICK-PASS' "$t/out") relay_running=$running tick_relay_lines=$late relay_starts=$starts relay_dones=$dones max_other_relays_at_start=${maxc:-none}"
