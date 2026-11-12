import sys, re
name, path = sys.argv[1], sys.argv[2]
s = open(path, encoding="utf8").read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (name, a, s.count(a))
    s = s.replace(a, b)
M = {
 "M1":  lambda: rep("margin-top: 6px; width: fit-content; min-height: 40px }", "margin-top: 6px; width: fit-content }"),
 "M1b": lambda: rep("margin-left: auto; padding: 11px 14px;", "margin-left: auto; padding: 9px 14px;"),
 "M1c": lambda: rep('<a style="padding-block:11px" href="https://my.home', '<a style="padding-block:9px" href="https://my.home'),
 "M2a": lambda: rep(".progress { display: none }", ".progress { display: block }"),
 "M2b": lambda: rep("  .progress { display: block; position: fixed;", "  body{margin:9px!important}\n  .progress { display: block; position: fixed;"),
 "M3":  lambda: (rep('id="limits"', 'id="XX"'), rep('id="ai"', 'id="limits"'), rep('id="XX"', 'id="ai"')),
 "M3b": lambda: rep('<section class="band" id="limits"', '<section hidden class="band" id="limits"'),
 "M4a": lambda: rep('<button class="iconbtn" id="theme"', '<button tabindex="-1" class="iconbtn" id="theme"'),
 "M4b": lambda: rep(":focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; border-radius: 4px }", ":focus-visible { outline: 0 solid var(--accent); outline-offset: 2px; border-radius: 4px }"),
 "M5a": lambda: rep("@supports not selector(:has(*)) { .cp .pph { display: block } }", ""),
 "M5b": lambda: rep("@supports not selector(:has(*)) { .cp .pp { display: grid; margin-top: 8px } }", ""),
 # reviewer's own
 "R1":  lambda: rep("nav.links a { display: block; padding: 9px 11px;", "nav.links a { display: block; padding: 7px 11px;"),
 "R2":  lambda: rep("white-space: nowrap; min-height: 40px }", "white-space: nowrap }"),
 "R3":  lambda: rep("footer a { padding-block: 9px }\n", ""),
 "R4":  lambda: rep(".progress { display: none }", ".progress { display: none }\n.hero-art { animation: grow linear both; animation-timeline: scroll(root) }"),
 "R5":  lambda: rep(".bmc:hover {", ".bmc:focus-visible { outline: none }\n.bmc:hover {"),
 "R6":  lambda: rep('<a class="next"', '<a tabindex="-1" class="next"'),
 "R7":  lambda: rep(".cp:has(#cp1:checked) .p1, .cp:has(#cp2:checked) .p2, .cp:has(#cp3:checked) .p3, .cp:has(#cp0:checked) .p0 { display: grid }", ".cp:has(#cp1:checked) .p1, .cp:has(#cp2:checked) .p2, .cp:has(#cp3:checked) .p3, .cp:has(#cp0:checked) .p0 { display: grid }\n.cp .p3 { display: none !important }"),
 "NULL": lambda: None,
}
M[name]()
open(path, "w", encoding="utf8").write(s)
