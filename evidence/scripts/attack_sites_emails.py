import sys; sys.path.insert(0,"tools/audit/seat"); import ref_privacy as rp
P="tools/x/p"
cases=[
 ('"$GIT" push -q origin "$c:refs/heads/x/$s"', ".sh"), ('$GIT push origin HEAD:refs/heads/x', ".sh"),
 ('$git push origin x', ".sh"), ('"$GIT_CMD" push origin x', ".sh"), ('${GIT:-git} push origin x', ".sh"),
 ('gh api repos/$R/git/refs -f ref=refs/heads/$slug -f sha=$c', ".sh"),
 ('gh api -X PATCH repos/$R/git/refs/heads/$slug -f sha=$c', ".sh"),
 ('gh api --method=POST repos/$R/git/refs --input body.json', ".sh"),
 ('subprocess.run(["gh","api",f"repos/{r}/git/refs","-f",f"ref={ref}"])', ".py"),
 ('gh api repos/$R/git/refs \\', ".sh"),
 ('gh api graphql -F query=@create_ref.graphql', ".sh"),
 ('gh api repos/$R/releases -f tag_name=$t -f target_commitish=$c', ".sh"),
 ('gh release create "$tag" --target "$sha"', ".sh"),
 ('gh api repos/$R/contents/notes/$slug.md -X PUT -f message="$m" -f content=$b', ".sh"),
 ('git send-pack origin "$c:refs/heads/$s"', ".sh"),
 ('gh api -X DELETE repos/$R/git/refs/heads/$b', ".sh"),
 ('gh api repos/$R/git/refs/heads/$b --jq .object.sha', ".sh"),
]
print("== site rule")
for i,(line,ext) in enumerate(cases):
    print(f"{'found ' if rp.sites([(f'{P}{i}{ext}',1,line)]) else 'MISSED'}  {line}")
fid = rp.Identity.made({"/Users/exampleuser"}, {"exampleuser"}, 4242, {"example-mbp.local"})
print("== email_leaks (synthetic identity, host example-mbp.local)")
for e in ["t@example-mbp.local","t@EXAMPLE-MBP","t@example-mbp.fritz.box","t@192.168.1.5","t@[10.0.0.2]","t@example-mbp.lan",
          "exampleuser@gmail.com","t@seat.home.arpa","t@box.localdomain","123+x@users.noreply.github.com","noreply@anthropic.com",
          "t@corp.example.com","t@localhost","t@(none)"]:
    print(f"{'REFUSED' if rp.email_leaks(e,fid) else 'passed '}  {e}")
