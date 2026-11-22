import sys
hdr, body, out = sys.argv[1], sys.argv[2], sys.argv[3]
extra = sys.argv[4] if len(sys.argv) > 4 else ""
pre = open('/root/pgen/preamble.py').read()
open(out, 'w').write("#!/usr/bin/env python3\n" + open(hdr).read() + pre + "\n" + extra.replace("\\n", "\n") + "\n" + open(body).read())
