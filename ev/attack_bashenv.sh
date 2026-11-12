exec() { if [ "${1:-}" = /usr/bin/env ]; then echo "re-exec shadowed via BASH_ENV: $*" >> "/tmp/tmp.wHyZjY816P/demo/shadow-bashenv.log"; return 0; fi; builtin exec "$@"; }
