import sys
sys.path.insert(0, "tools/audit/seat")
import ref_privacy as rp
U="Users"; H="home"
fid = rp.Identity.made({f"/{U}/exampleuser"}, {"exampleuser"}, 4242)
cases = [  # (kind, text, as_ref)
 ("slug Users-x",            f"wip-sync/{U}-exampleuser-proj", True),
 ("slug users-x lowercase",  f"wip-sync/users-exampleuser-proj", True),
 ("slug other host Users-",  f"wip-sync/{U}-someone-proj", True),
 ("slug other host users- lc",f"wip-sync/private-tmp-x--users-someone-proj", True),
 ("ref claude-uid no tmp",   "wip-sync/claude-4242-x", True),
 ("ref other uid no tmp",    "wip-sync/claude-999-x", True),
 ("ref tmp-claude-otheruid", "wip-sync/private-tmp-claude-999-x", True),
 ("ref mixed-case name",     "wip-sync/ExampleUser-wt", True),
 ("ref name_underscore",     "wip-sync/exampleuser_wt", True),
 ("ref name glued",          "wip-sync/exampleuserwt", True),
 ("ref URL-escaped",         f"wip-sync/%2F{U}%2Fexampleuser", True),
 ("msg URL-escaped %2F",     f"see %2F{U}%2Fexampleuser%2Fproj", False),
 ("msg URL-escaped %2f",     f"see %2f{U}%2fsomeone%2fproj", False),
 ("msg file:// URL",         f"file:///{U}/someone/x", False),
 ("msg /home/someone",       f"/{H}/someone/wt", False),
 ("msg /HOME/someone upper", f"/HOME/someone/wt", False),
 ("msg /USERS/someone upper",f"/USERS/someone/wt", False),
 ("msg other-host bare name","by someone", False),
 ("msg ~exampleuser",        "~exampleuser/proj", False),
 ("msg email local-part",    "exampleuser@box.local", False),
 ("msg backslash windows",   f"C:\\{U}\\someone\\proj", False),
 ("msg /home/claude cloud",  f"/{H}/claude/wt", False),
 ("msg /private/var/folders",f"/private/var/folders/ab/xyz/T/", False),
 ("msg /var/folders bare",   "var/folders/ab/T", False),
 ("msg json-escaped slash",  f"\\/{U}\\/someone\\/x", False),
 ("msg tilde-expansion $HOME literal", "$HOME/proj", False),
 ("null: /home/runner",      f"/{H}/runner/work", False),
 ("null: Users guide",       "Users can pick a zone", False),
 ("null: PR #4242",          "PR #4242", False),
]
for kind, text, as_ref in cases:
    r = rp.refusal(text, (), fid) if as_ref else rp.refusal("fix/x", (("the message", text),), fid)
    print(f"{'REFUSED' if r else 'passed '}  {kind:34s} {r or ''}")
