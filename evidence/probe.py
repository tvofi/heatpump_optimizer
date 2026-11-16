import sys; sys.path.insert(0,"tools/audit/seat"); import shell_hazard as s
for t in ['[ "$a" = b ] && [ "$(wc -l <f)" = 3 ]',
          '[ "$a" = b ] && [ "$(wc -l <f)" -eq 3 ]',
          '[ "$(wc -l <f)" = 3 ] && [ "$(wc -l <g)" = 4 ]',
          'test "$(wc -l <f)" = 3',
          '[ "$(wc -l <f)" -eq 3 -a "$x" = y ]',
          '[[ "$(wc -l <f)" -eq 3 && $x == y ]]',
          '[ "$(wc -l <f)"x = 3x ]',
          'if [ "$(wc -l < f)" = "3" ]; then',
          "st $(wc -l <f) 0 m",
          ]:
    print(repr(t), [r for _,r,_ in s.hazards(t+"\n")])
