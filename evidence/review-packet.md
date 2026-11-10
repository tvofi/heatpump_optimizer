# Review packet #3408
head: 6d894955cfb79f65a64e445acacb8f159342b237
base: 0362916ac7c1daf994e042c41d79b7e4083414e3

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=129656191708 neutral
arch-score / arch-score id=129655949481 success
arm id=129655799377 skipped
budget-raise-gate / budget-raise-gate id=129655949433 success
cancel-superseded id=129655801729 success
codeql id=129655950336 skipped
codeql / Analyze (actions) id=129655939690 success
codeql / Analyze (javascript-typescript) id=129655939581 success
codeql / Analyze (python) id=129655939579 in_progress
gate id=129656403236 failure
governance id=129655951381 skipped
governance / delivery-status id=129655939851 success
governance / delivery-status-publish id=129655941715 skipped
governance / env-matrix id=129655939797 success
governance / instrument-self-tests id=129655939643 in_progress
governance / policy-docs id=129655939736 success
governance / record id=129655941739 skipped
governance / wave-script id=129655939691 success
hassfest id=129655950743 skipped
hassfest / hassfest id=129655939556 success
kernel-points id=129655950407 skipped
pr-contract id=129656404051 skipped
prelude id=129655801426 success
refresh id=129655801786 success
sweep-self id=129656630725 skipped
tests id=129655950330 skipped
tests / arch-instrument id=129656116825 in_progress
tests / briefs id=129655939597 success
tests / browser id=129656116863 success
tests / closure-scope id=129655939787 success
tests / closures id=129656116782 in_progress
tests / coverage id=129656116766 in_progress
tests / fast (3.14) id=129656116943 in_progress
tests / mutation id=129655939630 success
tests / mutation-autofix id=129656190846 skipped
tests / mutation-pins id=129656190194 skipped
tests / nightly-ha (2025.2.0) id=129656116895 success
tests / nightly-ha (stable) id=129656116958 success
tests / nightly-status id=129655939602 success
tests / replay id=129656119090 skipped
tests / typing id=129656116830 success
validate id=129655950962 skipped
validate / validate-hacs id=129655939539 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 6d894955cfb79f65a64e445acacb8f159342b237 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item f6661d6c: #201
NOTE body item 75a33120: #201
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/typing_ruler.py --mypy --emit <file>
             `tests/typing_ruler.py` is in the tree at this head
  ok         python tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff <merge base> HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         tests/closure.py select --diff <merge base>
             `tests/closure.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/dependabot.yml b/.github/dependabot.yml
index e3e057cb5..f2f2ded13 100644
--- a/.github/dependabot.yml
+++ b/.github/dependabot.yml
@@ -15,7 +15,11 @@
 version: 2
 updates:
   # Hash-locked (`pip install --require-hashes`): Dependabot rewrites the
-  # version line and every hash line of the package it bumps.
+  # version line and the hash lines of most packages it bumps, but not all:
+  # #3088 and #3323 each moved pins whose hash lines it left at the old
+  # version (the typing lock's overrides, and requirements-coverage.txt's
+  # coverage), which pip's hash-checking mode refuses. Such a pull request is
+  # re-applied on a branch through each lock header's compile, never edited.
   - package-ecosystem: "pip"
     directory: "/tests"
     schedule:
diff --git a/dev/programme/delivery/3408.md b/dev/programme/delivery/3408.md
new file mode 100644
index 000000000..63b5010ef
--- /dev/null
+++ b/dev/programme/delivery/3408.md
@@ -0,0 +1 @@
+- [#3408](https://github.com/tvofi/heatpump_optimizer/pull/3408) — **open**, deps(tests): the pip group's bumps from Dependabot #3323, re-applied with hashes that install, homeassistant-stubs, zeroconf and cronsim held (R10-DEPENDABOT-3323-COMPAT)
diff --git a/tests/requirements-build.txt b/tests/requirements-build.txt
index ad6d2d7f3..bc7e04188 100644
--- a/tests/requirements-build.txt
+++ b/tests/requirements-build.txt
@@ -22,46 +22,46 @@
 #     --generate-hashes --no-header --no-annotate -o <body>
 # and replace everything below the blank line that ends this header.
 
-cython==3.3.0 \
-    --hash=sha256:03056533fe4fdbc4f1d34a39178f9a4937ff35196f8bcdde2a67b5b5809c61fe \
-    --hash=sha256:03bc5333932f5dda3ba9315298ecdd21daa1b58410bb1f8ce04c78ec8337130a \
-    --hash=sha256:0507d9caf7dc35f1212627145d5d13dbc5dd7128529a6608ab72690472fa688e \
-    --hash=sha256:0deedc2e9a5a664e1adfa4c2d310aa7b54903e1a647c274b6c9213f77a02d637 \
-    --hash=sha256:11e437f086affee8051cec4bb531be3edb646ab66e325154aa6849377f365033 \
-    --hash=sha256:14e825253455e943ca765a95096b355745558436b0c46c24856de9269cc4dbd9 \
-    --hash=sha256:169e56fd411f4cd5bba51c82f8239421d547a846099db2b261e4aed48ba9f51f \
-    --hash=sha256:23942b0662642927a55676e4b26e6840fb166dd7d76436384685227e7e8619a4 \
-    --hash=sha256:26a5e536fc68e85a9de091a0b51c42c5ac834f8d00aaa43f227cbc3efa797ae5 \
-    --hash=sha256:29f38ebafdf23e3da2516f40c4d065da38bfe002181bf93e2b8cf1262449aba6 \
-    --hash=sha256:311a016369adfd1e0015c4f9819168fc0e518451d7efb4435c30d65a3a26d52b \
-    --hash=sha256:333449cc0350baedee5a6af27929eac8a71eac4ec59333c45ff476b33c6c660d \
-    --hash=sha256:428fafed98ea26927000a287b4dfc9ef07339f56656a5329a34eaa593f79a4f8 \
-    --hash=sha256:46072c0d404616b5e652a63882c79cc3f8a1d62635a8692f56ed0e416a4dfed8 \
-    --hash=sha256:4a36c34d1950845b8ac148653b07cdc62421a4b0d9abfcc849e69f1c4ff9919d \
-    --hash=sha256:51999fb834365721b6c7f689cf6e2ec7c8667aae783df9eb5e589c290a414d9c \
-    --hash=sha256:596e8df019372a2cd417805015022d42cb8ee4e1803ccdc11ed00e451625fb66 \
-    --hash=sha256:66d86b6a1548ae64851b211e3c3504535814b8c8e6c46ddcaf01062bf8d5fad2 \
-    --hash=sha256:75c4ae8a6d3a5ccf3cdaba8ab32e6a8d0cd38e3a476aa7ac12df8f8171a8d570 \
-    --hash=sha256:7e321ae700995a16dc3055ada06ffb8d61e1a7434e5d0e811547a45ac1015ebd \
-    --hash=sha256:82f94565b6001bab8e31bf52a0911672910b5735910612a2c0f772c719670006 \
-    --hash=sha256:843d7134e784e7b320ef387512e89f1b29af80c641e176dfa8eabd52aab61c3c \
-    --hash=sha256:8566ea804cfc265f5e9dda71d1b716aa24ee4c3423a5da4b28a248a78c33e3f9 \
-    --hash=sha256:90869072e50b7c8904fe1dd7810321ae901fd5637a6eec6646ed9c57f9eb1081 \
-    --hash=sha256:9b24b5c8cd536946b62086fcafee6d5509d3f549f72d553d2336af87ffbe0da1 \
-    --hash=sha256:ab24d1a4fb6aaf0b5b6fcd75a6d70255fbd3130fa78884c26991f8d5502616b5 \
-    --hash=sha256:b447f6906e0555f05dc4742ef1f99091b1e5d9aa9f16616e772fbf9ff6271616 \
-    --hash=sha256:b55c72e8eccdd508c8de3cf3bbc543aafbb3bf6a518e1ee20358d3241cd780ef \
-    --hash=sha256:b94fb5613b9fe34c27d13ec9972dc0dcd2a2155db2902e93921cadc162610a38 \
-    --hash=sha256:bc2f2a6b65a991666cfd35a35bab0cd88ffba4df2f601edb6e76cc8116de24b9 \
-    --hash=sha256:bf411da3ef1af8763781c219108860f7de33f1100038da35d6bf1b4d83fcb2c0 \
-    --hash=sha256:c4558ba85849ab65dc57e10fd0efb13fabd9d3c09981a2566e18dec7cf47586a \
-    --hash=sha256:dce56c26d388f00a19426371b6926bf2f77c5c03b71d5273e4556c68be98c2dd \
-    --hash=sha256:de883ec6764b61547c1e7674c0d8a8a875d398bd6bb684e46b93d83e4f13b260 \
-    --hash=sha256:e0d2713d2b292c826bc21dc8732bd9e47628103aa3764180c881e04b3fef95dc \
-    --hash=sha256:e6035b5231a9316edc19d6415f4296fd1d0370e2a165a714b3edc167b9ca00e1 \
-    --hash=sha256:ec09dbf73ff4f7be2b339b995fadae9c4bb517bbbed7ec11d6fe99c2092b48fd \
-    --hash=sha256:eda47eb7731c3b41180b58bb83de423f43aa58a677677e3390e8d332b003859e \
-    --hash=sha256:eed0d93fbca7087f143b42c34b05a825849bdf17f101572c2105acfa49aa88b8
+cython==3.3.1 \
+    --hash=sha256:08ef3dcd3070959983a15e82bbfd56edb13cbe75b14043665c76ee4425140eaf \
+    --hash=sha256:0ce9efd76bfbf7b67be0da80d450231e1c1bdd5e755d7a8dc10ffc2669fc5edf \
+    --hash=sha256:0f7d52979bf7730351cf9ca2e9257d4b80f729053b521159bab8666e6be7e3bd \
+    --hash=sha256:14bd1521a14d98bed4ae791ace5e830055ffc45a8cbb09f22adf90ee7dca3409 \
+    --hash=sha256:215669fd0ce792080cd4d0748db7e1e31f424b6706a6220d08339895e6a3a03a \
+    --hash=sha256:226d791808ce95f20ab1b3589082be604b5b5b31e670bf773ef9c312d2f0a8c2 \
+    --hash=sha256:26a28e0ca5dffe9c7d69d1e3a0f78cb74f41b2b6b40771f620262a5d04862a00 \
+    --hash=sha256:298d3e46d1d4e2f4405d2c934b51899482101a0b0dc43b1b13b2e38f87addf52 \
+    --hash=sha256:3370326802b82cc7cb7df65e605e1acfebdce193077e27ed5734b9bc3f7c6ad0 \
+    --hash=sha256:39a070cfd465ab44e4fc027f655df38e7d37c32d16262b254390a1015a0691e9 \
+    --hash=sha256:43b16388665cb829c265060705900db8e26e9c3c04cc91f28af38c905d12293f \
+    --hash=sha256:45dd533a87c9629d02d77c9a5b48cf399907a99e4bb556aebafd2ac4b68580d2 \
+    --hash=sha256:4d1f9d6fad7a8d9750b641a941cd841ec43740a375cb2fdb934329a17fa88b36 \
+    --hash=sha256:55102da0e7700c533cea2bec1456ee6169cc13ace6b9f6048c31f55cca76bc51 \
+    --hash=sha256:5f08b3eaa639005bea6ab119ebbd6e30656e448981e7a124d80b409760d06c15 \
+    --hash=sha256:5febfc8c52aced0cf9360e6f2304428a5fa0e66fd9aa7338d5c41f0ce26dd104 \
+    --hash=sha256:6156be528b46e820ba834449716690d5065049ff355f261a8600f7da6b436d96 \
+    --hash=sha256:61abc7feedd20dac6c4ff7ab3a30e17136a067b242ab9253e2b4a6d9a72c2b61 \
+    --hash=sha256:73f6f40f9308e77cbdb3259155d793ac189ead6687b9a432f1b4503170cb9a13 \
+    --hash=sha256:744bb804252cf204e6bc9b0fac06b3bad7bb14258cefb9f321c59c4c59e9bc17 \
+    --hash=sha256:747dade0373011034645ace4e7eb3a54102c52524fc0675dea76e655e9c1dcff \
+    --hash=sha256:76be39d20d064ad31ca55e124f5cb539e2baf933ccc321ef629ce162ab8b10d7 \
+    --hash=sha256:7a6c191617853f2e0d5936c73f5d5cd096548f4d9e0fa37612ef721591c42cb3 \
+    --hash=sha256:7bcc6de1603d8180667b40f4014be142d7d62cfc10af0184ad8d6a83847a2ced \
+    --hash=sha256:7c1f05344b32ecbb83e3bbd3586282ac1f4aedeb8025cc6e13f22a6d4e2b4222 \
+    --hash=sha256:801730e5714a40dbab8a373af36110de8ff161ec056c855a9627cf05fbc8a6d1 \
+    --hash=sha256:85be5442e8f465c7c5e80837ac2a85a2ce04034e616445113092e85b65d0ab94 \
+    --hash=sha256:8b4391d39260efedeff2e3914e958b9ed75cb2b40f10b62bb0e9ca002658563a \
+    --hash=sha256:a1bfd7511fe8d83f5e681876df22878efac5cd5b2c174f272e6bf018c8fd4a91 \
+    --hash=sha256:a2bdb50e9fe8974447b68edc5b0201573b06d2c5683f472a5fc08e1792051277 \
+    --hash=sha256:b0265a0e186af3c38339c561507e98e2e3a0d377cdb2b0427f980138ceddd4af \
+    --hash=sha256:b0eac1184dd57591a8f3d25691c7a6bf7db030f515b210691bd251772a7e70a4 \
+    --hash=sha256:bce8f37f50add0432ac802cfc34e5bd16395f2918ad1eaeb50b26d02c9001014 \
+    --hash=sha256:c4e4132b03a6c6c11541f7498441224f55a9e101c615d49494983d2b10dd7669 \
+    --hash=sha256:ccd7b6030b2f7705b928080f6c444a99a37f6058de8dab11d577499b64ea0f3a \
+    --hash=sha256:d0f2610ce850d264e29a87b3d9b8ec4f0f2dec5bc1dce0398294251f09b149df \
+    --hash=sha256:e0e45989e821bef6aa9ae15c7d583ab5e055f7406c4b3624e49e06d24e90375a \
+    --hash=sha256:fcb6c86dddaedd1da5d77ba2469c1a4bea52442e02d8f0653ff78667fbaaa8d9 \
+    --hash=sha256:fd81cfc6e94c43c5c0fe50439c11b90dc89cc6b323f92b37edc6a951d0a619d7
 packaging==26.3 \
     --hash=sha256:94edc256424af38762eb31306eed28beb9f0efc50a8837492c9d6fd6004aed79 \
     --hash=sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c
diff --git a/tests/requirements-ci.txt b/tests/requirements-ci.txt
index 075416b19..623bfb591 100644
--- a/tests/requirements-ci.txt
+++ b/tests/requirements-ci.txt
@@ -824,9 +824,9 @@ scipy==1.18.1 \
     --hash=sha256:f29633129f9fa7e88a3f0fca835de2d030bfc9643f7799e1a0c46cee24d38fc7 \
     --hash=sha256:f55fa87b6c612ecd6b058f167c53231b1d14e412efe361d3d6e38b3631c73218 \
     --hash=sha256:fdaf5ea890a6183d0565f51a61799d67081bd5b1cf03c5f4b3fd3732108625c9
-threadpoolctl==3.7.0 \
-    --hash=sha256:61348cfb77d53b9242e0017029244b559b810c142ced65b4e21eeca1843959a7 \
-    --hash=sha256:cd8b60b5641b45c67bbf73c64c843235fc2d8a480c87389f52f5dbee893b86be
+threadpoolctl==3.8.0 \
+    --hash=sha256:01080674ad7ac6182429c918a79de92da789bb448acc02fc0b620b1abd6b6137 \
+    --hash=sha256:f1b49c82704d50f13ffae019c727b0fa4f6791a58f48f06a09c45face1be66da
 voluptuous==0.16.0 \
     --hash=sha256:006535e22fed944aec17bef6e8725472476194743c87bd233e912eb463f8ff05 \
     --hash=sha256:ee342095263e1b5afbd4d418cb5adc92810eebfd07696bb033a261210df33db4
diff --git a/tests/requirements-coverage.txt b/tests/requirements-coverage.txt
index 2ec445729..a60a54b68 100644
--- a/tests/requirements-coverage.txt
+++ b/tests/requirements-coverage.txt
@@ -4,128 +4,128 @@
 # for every `fast` run -- the workflow step that installs this says so too.
 #
 # Regenerate:
-#   echo 'coverage==7.17.0' | uv pip compile - --python-version 3.13.15 \
+#   echo 'coverage==7.17.2' | uv pip compile - --python-version 3.13.15 \
 #     --python-platform x86_64-manylinux_2_28 --generate-hashes \
 #     --no-header --no-annotate -o <body>
 # and replace everything below the blank line that ends this header.
 
-coverage==7.17.0 \
-    --hash=sha256:032d4c2db4c677eb71d43f2f8b80bf64e9346f7a3f7b6ebb13f1782f3cc6c274 \
-    --hash=sha256:03baf0688e14a5a44ffd1eefa8928dfc92b14565e521174e072b31b971aa1657 \
-    --hash=sha256:045c1eeb19fb4eae949850a761102fffb3a5f638b97f977912f95843e54f6669 \
-    --hash=sha256:09e563b49c81cd0a33734e926d7a4a6ef1778d74304cde2dcc3aff8b30ea1036 \
-    --hash=sha256:0a9cb9a0fb58e6fff5442969af36094ecd6976f4907f179e33b27e15355d8f74 \
-    --hash=sha256:0b8bb651a4406fb6a983a905309fec1783443c65e1771b41e92740a0f4a1176b \
-    --hash=sha256:0cfdc938ca3319d873d1f1252e60620a39aee4ebf9dbd7cc58238109ebda9c51 \
-    --hash=sha256:0d0fac604a962ff546beb038cba9a5a09d88e6e3f01612fb46f7bd4fe5dc8dca \
-    --hash=sha256:0edeb6594f080c8de1263cccb239cb316ef77aeb959e2e0f38f2953fcc72a49e \
-    --hash=sha256:11f5f7fb2d97a0fe865f5e7bad4eb0619b957637f676bc088d13844adf26ba95 \
-    --hash=sha256:12961f738d717a046d4bf3f8d1727eb3ebe2ed5478ff96cd6233d4dfc39323d3 \
-    --hash=sha256:12cb8a20ad904a5811e6660d829a586b216e5254b9b34b76dde8a4d65d827dc6 \
-    --hash=sha256:194562ab1eff0d85aee8a17ce4c5c0bc1ebf70a629a7145257123156ad100fd6 \
-    --hash=sha256:1cabb31531002fef5197de5df3c84730aef01e750e25154b9813a2583435aba2 \
-    --hash=sha256:1ee0a982b0e1230b3edf768a7dd022bd2377303763895327ac62deb5efacee03 \
-    --hash=sha256:2bf3ee38a40c0570c316b9e7507c472469586906a20f289705898528c31aaea8 \
-    --hash=sha256:2c680e838ff9e68d491158625ca2c1ddb17d78d791bba96a31f8b839b4990438 \
-    --hash=sha256:2dc9233f39149b5a4f4aba17a4b6bc5cca22e52cfc4b06fdb07d014439b8b2ea \
-    --hash=sha256:2ed3097c6817bc1a7fc8ae0a6131db74aa1150d863cccc308237ff362d3226b2 \
-    --hash=sha256:3067608b4429629f640c1b23d2f69b05d2fd45e00ebb6ee9e8fad220a6c11722 \
-    --hash=sha256:30f5477aac9c9e4a0a641c55f8f8fddd7f3bd91176c912c50f40ffced96b4034 \
-    --hash=sha256:337f87e62e1c5f43c8198d879f677c342d152f84d3f157add12558853cbb8eaf \
-    --hash=sha256:3393209f6894713161ee82a9b0e673e58237e0f9733c6638e7a6c0c620ef0b33 \
-    --hash=sha256:34d65c9e8e257f48a654908005046fbf1bc48d9540ae3776ad08c0acd010e10c \
-    --hash=sha256:38c86e5d74bbfd88a393fa3f91257c1225c63aa6db6d5918de3e49ab04f91c6e \
-    --hash=sha256:3a4459b0f389dd1e51aac3dbfc4ca35b30cae7dc99caa3c0a086d1997a985709 \
-    --hash=sha256:42e6f170d1ac04b7eb3363310a6c41cdfd82c1fe6bf9ffbc4a86f380bdf091c7 \
-    --hash=sha256:4343a9378b964eb3cb80fa90406385de91c7e982a769ca9314d848f93bc0d3f2 \
-    --hash=sha256:460679f53893081edb94eeed011d26be37228ba649b853fd2aed7e4394fb1f35 \
-    --hash=sha256:4e153f0bd6509dbf837fd585f489b3328bfd98f2a718a0b15ae63032148b285c \
-    --hash=sha256:50678474e714c684b82c108e63fbb8f1bcf1266d8293a49980f1d08526f093b5 \
-    --hash=sha256:55939ea4c097fda2edabf80fac5e49bef15597b950a9f29fc56292a895245feb \
-    --hash=sha256:559f748446ee799803686b5784e3deb54c70d655ac386a860e06b11672504ba7 \
-    --hash=sha256:58a304efdf2253fb2ea03d45d0a04cc174a92a0cd5279c28c5bb893ce7410968 \
-    --hash=sha256:5900055351ec89fdffb34b27898815106529ded29a9496464c1ebd6313fd40fa \
-    --hash=sha256:5b7fa0997b8eba7378ac66f31ec7f70164490353ab79b9667d37c0d365e50177 \
-    --hash=sha256:5cc15faaf318ee5040d835a62c75bc6f122d837274f3b5efd47bf9fbd4ac5b85 \
-    --hash=sha256:5ebfbc87836529a31d25c2dec1262c38eea852ec1c46c0f690a515a7339d9c5b \
-    --hash=sha256:5ee9c8bd13a59e301dc2aefe7aa8384633406808de051b1982775667094eb673 \
-    --hash=sha256:600e121e412cd6bdb52ec105b95c6a04da0c9710d1534f6e64a42db667907802 \
-    --hash=sha256:6052e878b628abcd38fa5f2b64abebc686eed4e2267da42434017a9c6d24f241 \
-    --hash=sha256:61cde5222f1933d476647c5a25ed1a8678b7703098cb5a15f4a0aa39967d8c28 \
-    --hash=sha256:62bb77987d3f72a0aaa77c567ee7f9806bc2e748c8f46fafbe1fdb90dd148398 \
-    --hash=sha256:66efc0fb99cee34626fc17d3adac9c3cd816bfdad563bb1e983c3ef432f566d4 \
-    --hash=sha256:6a80a11b90c4a03df1502304cf24ff953255b6b5d076ef79066ecf88baaff31f \
-    --hash=sha256:6abfb6a4cf1cb1b67bc8fccdde177e2d2b781d0d34449e7078156547025140e5 \
-    --hash=sha256:6ae0453a3390e67f7bfbe34417bbdf5b4ebfc21db23fb446a0a41115eeeca6ca \
-    --hash=sha256:6b4593d2871c4c801656dd5861e759f8f5156febd6b6061b02f6a72d64618b7b \
-    --hash=sha256:6cc31f27240d4e080437e3b8229d92f1d809c9a4f233607385373b73974e183e \
-    --hash=sha256:6e09612b1b82c9df1d2b6c85dee88d5aad3e73d77a8ec0b16ac6a7322cbdf5d9 \
-    --hash=sha256:72edd4f9483ae30cd1ba4f230687840ef7b58a16afb1c9e81131fd6d64655f36 \
-    --hash=sha256:791f9ee09814dd30d9562b4f4eb037a371485ec1c830b53999d2320d20c4e764 \
-    --hash=sha256:79cf71e5f9a48877ccfed5baa2c72f45af4feeaa596249e23eb15b473134830e \
-    --hash=sha256:7b5abcae74750302ac4bc77351eaee87c450e4abd3b6225eacde3858e260f8b2 \
-    --hash=sha256:7c570293f001ea91598b90e90cb9b98fddee833e90bbede432cbd218331ccd8e \
-    --hash=sha256:7d6d9d396c8b7bcaf76d774a10140b218111484e54c73a5f2a1b75655381748e \
-    --hash=sha256:7fef12cec4b96f59e09761cbd4fc9bdf4788062d1ae435b920241fc16c8a9549 \
-    --hash=sha256:804fbaf81d09b34e2f8b1159d01e211a50713d743d32fd9b2ca6cf0ae507a66f \
-    --hash=sha256:84538c040f4e6214f663459d89372ce4e6b2bbdd9d397ef0dca7b3ecd56b8eb2 \
-    --hash=sha256:85682ca89bc4601125dcdff23fa70e6274e13c9ad502fba845e6c274ab2c6569 \
-    --hash=sha256:85932227e9dd38e62cd29c17fefdfecfb919eead6af1e3259522d03cf85de983 \
-    --hash=sha256:88a1a9fb0075b83389dd9b403bb3fce976031b3c2aa0e05e3e57143cf639de69 \
-    --hash=sha256:8d823d66afd59566030539c49c7a6acaf3083996682be2dda760c63555842094 \
-    --hash=sha256:8e8113d3852e9377421a61de1917df27b3abb25404a4ecf69f9e64612c4345b5 \
-    --hash=sha256:912a29f338798541d795e2e25903c6fe7a99dee70a40fe4706a9a124649b523e \
-    --hash=sha256:91e487ad07c511da77b574820141a7c2da09bc2a4b4090b5be2424295d100697 \
-    --hash=sha256:96151262832f3c230ebae23b2d6911ad549e1738465946c97004913ff06112ba \
-    --hash=sha256:968c5fb6e0c83cab752d79a70209648ce4d90cae815c60fa229b59e264601062 \
-    --hash=sha256:99a7b390cbccc6bf029ca4da3f0f607c218bb4085e9cd6b58a90d14ca12993c3 \
-    --hash=sha256:9a66074231799d8884d267234d49f60c90b43a945dfe069646b72f3058cd4e67 \
-    --hash=sha256:9c083e253e96fdeeaf48133fe836cac86ace2db215d235700e7f7532420a200c \
-    --hash=sha256:9d1fdf82c6fea57b5e9dada509f9ce9638c8334664e2c98c7f6f1ccf3d143ad2 \
-    --hash=sha256:a01ef92caeedfa4f2ad171a3a8e6fece4565de871d8bca428151bf9929f41048 \
-    --hash=sha256:a14e8d69464da9cbe1dc29e7116dbd37296d1d51a695327c478e250349085089 \
-    --hash=sha256:a1762e85cbbe3b5ff9c6dcbcc1b89d5c72320094292b7b9572bf882c85e428b7 \
-    --hash=sha256:a25cc5e8c23a590815c6a7aa43624234d25cb23b21b484adb8a0daed59860db5 \
-    --hash=sha256:a32ee5831b15ba239bef5d272ae586ca8acea4a661b5f2941f5a0d380e518b23 \
-    --hash=sha256:a3914e2c98c34b94c26d2add3d2a61ccfd3534fc4eaa879ee290bdbb5184ba6c \
-    --hash=sha256:a59c3b470ac3b2432af3598a996affbeb10236cd899a005c1c4e517fcff8b592 \
-    --hash=sha256:a5e2e0625dfc789af0b2e10acfc106b352f314fffbd19e6392a7961c8cbe5d9a \
-    --hash=sha256:acdb5f3c96046efff9dc6c572a6acb2b8d0da09372d7b9a9ed7249cf7d17434f \
-    --hash=sha256:adabc1079ba844b096799ba8638d8df434aca1613f95bb7d5791af320cf05559 \
-    --hash=sha256:adbf3450c0f3f2b2854e282a8758f2b3eddf787eeff24ec9c9bc2cbc38328cc1 \
-    --hash=sha256:aed06129a9f530a948928260d7d2d81c47261355b0127e3c782251b38958463c \
-    --hash=sha256:b2afebb96da9a1bbca142f8cc12320c14e5c215e0a49cded4f191f5a31506a28 \
-    --hash=sha256:b609df3d6d900464207532c5170a65c6ede8d2e0b91f151f90008a866395cd76 \
-    --hash=sha256:b88fb4d4d7608cbcebdc7ff7dbffc2115e3b81d6c33a79147cd79d54fcb080f4 \
-    --hash=sha256:bac487dce0d2aff28ddf1a533a916f771416eee0e493960f611e49037b878e9d \
-    --hash=sha256:bb5ca66937c55bc85d1a5e9c5900a3e4693a8edf2280a9b3672b7b2661a84b95 \
-    --hash=sha256:bd04fd23206be9ad3de13b0b39313094fafa66a1f6baf70f5471c004a9fac47d \
-    --hash=sha256:bd3e9eb493631ff1ca34bf5efac25b5c66724f837bf6182c4fc771c55946423d \
-    --hash=sha256:bfb6f868af552c0ceb2d19220b8cbcc2be096ca26163ac30e682a13041433429 \
-    --hash=sha256:c2c48a36bb970b7265b196032bfd4237c0b373f2b25ef7012d7e905b5b35c19c \
-    --hash=sha256:c3e11b81faafb1f063248735c3e2c5c4183fc1db2c7f46782170dd7760dffcbc \
-    --hash=sha256:c7c5672ecf1b497de7a0b37743bef40e3b58e3207e9fe2ed6682cb0420836a88 \
-    --hash=sha256:c86a39539d10d666bb819c16c94d7edfc1aa2e0531b937f7c549b83d15177c6e \
-    --hash=sha256:c8a58baa8eb6154c6645eadcc19b6c089deab78c24a612a83206f2a8a5992a7c \
-    --hash=sha256:c9ac886242bbd50fb35a2242ba79555a99891e657da33f98b7ca968e3488a350 \
-    --hash=sha256:cbf0b83ce927de6053279ba61342d9f8892afde1385fcba9144cd05d4023d109 \
-    --hash=sha256:cc010a0a7fbdd9bb8bdfd0d3f04a5151275860213cbd7e2b876b29778489c712 \
-    --hash=sha256:cd7397de6cc782f00fe5ac1d75e9b306bcfa49c8b6b8dd6ed1f7709393ad40b3 \
-    --hash=sha256:d45cdc495671fc99268ff3653e0da4244972e9fc0e1fc3ea9de18781ad28963a \
-    --hash=sha256:d472ee1c64868a917a47f02ffb4ac8c22b477f7589d57a3eb0c58b1ad4f0137c \
-    --hash=sha256:d523da3c2e4bca49417768bcdb1a443c5b359dc44b8b93a3102e118fce912c40 \
-    --hash=sha256:da94ec0484e84fce5c7bf8d0f54b97767a90d992653a129b35634699d516e0a5 \
-    --hash=sha256:db645c81cf4d6bcb392ea1894aad65d55d1588a8472c834b25ca575da3029a56 \
-    --hash=sha256:dc5936491e306f2f6f095bd5fba593de11eb0375cee787ca1f245c3a333a523a \
-    --hash=sha256:dfb12891a773cbc2132349c77c690a045a882fe3f98b4bda50dfabb01893f9bd \
-    --hash=sha256:e42a835271922fe7bf98c7a05c78d4032f4e52bf5b07fafa1eadfdfc2f0ad22f \
-    --hash=sha256:e4eaf11d6b0f2147f46cfbf06fe7edcca6f095d0120da00ddc2458995ee869fc \
-    --hash=sha256:e65a1e61a68493fbfbe44d8bec71b3231d81b9917f62d3dafe0e105072147e83 \
-    --hash=sha256:e8a72b26dc5c9a9422e45472b1d67ba5caf273c524c8668cc04b23062663755e \
-    --hash=sha256:e9494d9e99389d39e6a96227749af898d8924ff591cb63944f8a98e68582bf0e \
-    --hash=sha256:ef65e96f0fc1a7c8b7644c7011d47a8228555e7888ac4d6246f715a7f3d7c398 \
-    --hash=sha256:f1fc9a7cea899c51d8a53e66c2f082a3d9e461ece32418d3ef0a0b90c32bfd3d \
-    --hash=sha256:f6cdb47a9be2d3313829bed1d296086287682a3ee901ff987b3432b45705b771 \
-    --hash=sha256:f72640e02a470b57b15cd655820133f6892760209283a363a60e2df932d5f0fe \
-    --hash=sha256:f8bc2cd4c6aa58be1ca243fb8cddb6c3c42031fe4403991ad9cf2b3baed03d9f \
-    --hash=sha256:fb5745048ee20f796b0e3ab61831049e749acff188563e2af32f58ede957ac1b
+coverage==7.17.2 \
+    --hash=sha256:01303d9e68b6e6bdc5459b54e3bd0e3539c94c25b50ac7362b7cbcacbc815fbc \
+    --hash=sha256:0439f77deb5c023003533ae8909a9aa1e174c847d655327035b1e542c7c8a54e \
+    --hash=sha256:0712a43e39410aa567f2e85846490f8dd6c839820e7edef2142767c5c03162ba \
+    --hash=sha256:075566a44289afb634ceaafa7d8d377bb2667a5b4a90fbee2609efdcd015c66e \
+    --hash=sha256:091eba4248d31b03828fc657c96d14adfaa8754f5aec7b73298b82894858db06 \
+    --hash=sha256:0a623de5c57c5c3f3aed830c73a3a5aad91dbf76d53bc30ec161be758c8ca408 \
+    --hash=sha256:0d8a5dc709da9b90ad5cc859a9b88c9b801e65ca2fbf7cbdbed5b9cbf457fcc9 \
+    --hash=sha256:0fc17882975fe485cfc95fb2f20eed937e05e0c0d8ffa5048857cda3aa838e8a \
+    --hash=sha256:1682d98ded28524bc6853cc4e7c65175b3e917f38b2e2ddebb28cafd8ab4de74 \
+    --hash=sha256:189cdffb3ebc53d6133de67952dac7cc88d1fcaff5480623fb00ef0bf1cef918 \
+    --hash=sha256:1947bd9d82e405c892c50b0d8dc0c1dea5df2a962129ca238c500a6bcf887509 \
+    --hash=sha256:19d508b0611486f8e23e28abcba77795ee865ff0e0cd936349ba692c8d0d8ca4 \
+    --hash=sha256:1c3146ef9d14c011517422489784a7ac344477e9cdacb05d9529e912721cd5d8 \
+    --hash=sha256:1da1999e3c371edd669b48a1029c86dc0474cdc6ff152d58cb3f15cb3337af72 \
+    --hash=sha256:205f9e329d9d5e47c320f8712326a01620689edae50531cc8934511e2c5e8f7e \
+    --hash=sha256:20faaaf3a49601afbcd6d46c17a594b0ae62631498def44e5eed94789962ea18 \
+    --hash=sha256:248873a144c067f981742ff4bbfb48b57e281a8cb7a3821d4e293bdb50b47970 \
+    --hash=sha256:249c4b4eaac9ced6fb85e465027ca26348111c2760108fffc356a16be4f54cd9 \
+    --hash=sha256:27fc4384a1154f7df30d304ccddc05ef457368c065670ecbd392606279b3329a \
+    --hash=sha256:289a24443352713745f79c1b6aae4e99ced2f5ff3e86bb630c33c631d50f217c \
+    --hash=sha256:298849ca0e385767096995cb57f72059b469f43f9927b8393f29d134f7bb1062 \
+    --hash=sha256:2a6281011cf85699763bf88ab55e0774f6696f87b390f39152b14ecefadccb59 \
+    --hash=sha256:2ad189c65706306644399e48530ad1aea1dfb311bd21d988df1ace422d09f3f8 \
+    --hash=sha256:2b7fe217808239437b8509b869fde2e0cac48776a68c626bd6b15411b087e3de \
+    --hash=sha256:2c42c222939b8699e7bc0e453149627f211ebbbb2f74c1a04331b0cd9834e2c8 \
+    --hash=sha256:2cd1a7472a972fed01c89589b1560846e32e942f8329a515c4059d4521c6579a \
+    --hash=sha256:34e5c7a2da36804c6e6f10b368eae01ad56f5a4ac5ecce7297300a3d46fdef2a \
+    --hash=sha256:36248fb6c03341501169539bcab35eb3a59159100be1246fad3c14cb73c17685 \
+    --hash=sha256:36314997533266bde3d07765289674304d61bfe49165bb1b4fa9be12cb4ba0d1 \
+    --hash=sha256:3bd065e75c077d6de8cd3fe68699a8b47be3ec595af6b66e3629926839094609 \
+    --hash=sha256:3d3d9d79a2b6cdcdde5a1ab1ae89953faea5cb28c0eea17a413ad997bb3cc8a1 \
+    --hash=sha256:3dfefb1ec16ca1a01e5da40ba162e268ced8bd3624b9eba4e9384ebfa14af7ec \
+    --hash=sha256:3f219efbc3ec71c377e278dee201633e1d4ad0d2d9bdaddfd9489b2869d584c4 \
+    --hash=sha256:42133a2647982db7968db138c0f4a57f5836101d8d504600a87ef8ebfa22a4cf \
+    --hash=sha256:4274acd35aae5bbbd0908792260819b9720b171ccc099a8168f7c20ef5d6ab3a \
+    --hash=sha256:460ba2139866e758c3a8e9d9422fdc889942bcbc5ccaf710dc4fbd8707d14aa8 \
+    --hash=sha256:485b2ed9e13b7e9209276843d7147e2f1cd1c816582655650a64c8f922093c58 \
+    --hash=sha256:51c6a60e63ea993113ea5cd24a401cc2faddc54aa7acfddaffa5d3b8c0161b9d \
+    --hash=sha256:545ca42488c7f0e62324fb2621aa05737db843b75e84e65a271bbf976f496f66 \
+    --hash=sha256:555257578e20a46020c27b2af4ef99059cd906aa9b8e163baf9da9a5afb65a64 \
+    --hash=sha256:565f1f1a9632d82678525d668a10fe070a285603a9d3581505b0e1a66624ad50 \
+    --hash=sha256:5b71aeaa4440cbece5498acda30838685793d3bb960aff87ec97fbb546715a5f \
+    --hash=sha256:603140eeae3f9adc562f91b1b98d4d1fc491bd1f66c5082482c568d0b7891bb1 \
+    --hash=sha256:635337a96895f2ffcfe2aa7554468a988f468fb67a8007c1a65e95148c1855a9 \
+    --hash=sha256:674bcd023a3743666d4d7a15238e57a00c968553780a36c80d3779fc410b912c \
+    --hash=sha256:686b6f8f9e57afc3a44096b17ee8de7e11e0a12f2da819e25047af1eb3b0fc6f \
+    --hash=sha256:698ca1575135215be25ac9c5d14f0b5455135d29602b7ee81e511d64a0435c85 \
+    --hash=sha256:6bdf3821fd0740b5369b9ab58b4e9d0d68a2c5c75a7ee0cd3beb624f9f15e4fa \
+    --hash=sha256:6fd6f218e39a621a30dbaf9543831fa10fe713afc8a44b52fc42cfe277412609 \
+    --hash=sha256:70daa8e4b49541b51c0baeba0d802b0d14d3214daeebc071b3db0b0c7dc84646 \
+    --hash=sha256:74d91af590514dda16165d5d7cfa94183150c6a6a80a99f61068369ae3959455 \
+    --hash=sha256:7565c17092f2f4021abbe3f5007300c224f362364a388f5ddad9216dab44b611 \
+    --hash=sha256:7804a6022fcd5e1d4de4dc676e985d6aea0119249e88c041e943f3cd07953527 \
+    --hash=sha256:79cd2d9742419b6d1aaeb1f3fb77a8e6a01c09ebe5bd1b27011752410a5e3781 \
+    --hash=sha256:7a3984fb8c2407721f9bc05573fc9a770752efc756d55068ccbde1fe53e42233 \
+    --hash=sha256:7c123b6bbc183a14372036769f033098026aa75fc8fba37d028b0b772356e90b \
+    --hash=sha256:7c17f716c837db550a202e7732cdfaa726b8515cba88be42193616913970d223 \
+    --hash=sha256:7ce0acb27a823e8e5169282f538f0e182854cc8b472b88d45456f09b6fe364fd \
+    --hash=sha256:81a432793440edef268dbadd493393bd6f70fa4b87f76c58114f7f77f1ccfaea \
+    --hash=sha256:85bccf6fe19ea3747147387971465f6a06197d6b9f6b644a97ba90ca5b09c5cd \
+    --hash=sha256:87b30f3daa0bedda6b770b303410a6def007844772aaa143dc52675b3d95cd8a \
+    --hash=sha256:882cade9b6dc43b2bc819bb444c0a13e4ed1f669a50e0de74adeec54fce486f3 \
+    --hash=sha256:88d4dc83b6ad09a2134cad9d8ec780b274b17ac7dfba8c2c6e92e3bc468fe85d \
+    --hash=sha256:8d3626b9816f7eadd0993c3703a1d8ed124b579cebe5201b446f1c0d551fa245 \
+    --hash=sha256:8dc07ed34bcb206f69d5b54fd3874f7bf39ac941c9f7aec2b53b29874fcfd77a \
+    --hash=sha256:8dc17707fd463b4dfab53792e41d50a23316ac6b98539007aa2388a1d44a8535 \
+    --hash=sha256:8de787f533b13aeeea5d7139610eadb56f249cc739840b973603d1d18d0fb023 \
+    --hash=sha256:8eab0a5cff8dbc563d1416a6e079ba3c146712e47167c022a5df5ea01bd76df9 \
+    --hash=sha256:90c6c5f93606b8803bd7f8a0b2ae05df7e35da4504a1c53cfe9294a1731e1f49 \
+    --hash=sha256:95bd8dc5b356f78f10a967ec50f8902d56f24c623753ac9fce0aba9d6213d5c5 \
+    --hash=sha256:960e199965e506d78f62252355397a05c8cee8072ad2d82d932745517d566539 \
+    --hash=sha256:99b64a12fe6017c254a8027790e0eaa22eaeec201e7dfda5eaac176a6984ef27 \
+    --hash=sha256:a3f49ac9c9e5fd4b450677eb44f4b14ea9ab71950b2896888c9f6a22d5cd1773 \
+    --hash=sha256:a472e23a7514478e1c8124ea056424d681e3173975650b0a06b6181658f1009a \
+    --hash=sha256:a5565a9dd715a5a94ffcf9a0ad4b6b1501b5441fd67d660e78742adff5d37a0a \
+    --hash=sha256:a5909dd087006c70c128297312ba67d877123e871100645d9bd73ae021a4d01d \
+    --hash=sha256:a65faa1ee98e090a5fd7c116f6d3ab5c6a85fcc46849b8494835608715836399 \
+    --hash=sha256:a838a10afb5b60a6cc6315348b176badaf2409d821208a3e3cda1dc608129e23 \
+    --hash=sha256:afd81658f17b1a50bbc1d247a61fa435be0be471246136eb946f9cbfc437a4fa \
+    --hash=sha256:b0209fff1ca92f1e2e344d54b5b3def74efbdb46ba807cd81976a5e9e569cac3 \
+    --hash=sha256:b08ee3ef53e80e5a50c68b3d9764363e373acba540e1b58daee0a9a7f23fdfb2 \
+    --hash=sha256:b94c509e26603ba7f8cb1bf8bb63967c7be533493be5668d8442cd06ec853d76 \
+    --hash=sha256:ba45dc072bfbf1798e68ec81379b73473fc912174bff9f91924d77711a1d2b30 \
+    --hash=sha256:bac3c79c31f45274117ed64c65efeaed85665668aeba7d809c7c38801ada6ed4 \
+    --hash=sha256:bb74283661a239fdaf738ac0b07db4ed9b476c7532d3e713abf0f6a072781e60 \
+    --hash=sha256:be0fec33b69c40f845c76f67fb4495b62a84da8c31a579dc6e18c5a63fa6a1f3 \
+    --hash=sha256:be699e76b57fede8920a0f568eff23b270d9004414b7cf6744bdda851638be6e \
+    --hash=sha256:c10f2a2748dd084e44811bb9b26979763af9003115d9bf93c1da69011944719f \
+    --hash=sha256:c5a98aff9eb681312ed403ecb7beb5f15fd25d6e0acc2554b9ca4b4d6f0b6705 \
+    --hash=sha256:c68f64d96857749a215657c172f7144ed026063489686b901774f271997923c2 \
+    --hash=sha256:c9639c2ea019c948b52067a0f74485039eb84b7a2de828ba6d178e663fb2b8bd \
+    --hash=sha256:cbf751ae86ef0d80e719915c087b05776c8d9300141f6c3e56f536d78a62c301 \
+    --hash=sha256:cfe64d2501806a04507217852a3132a9a9076321435500bf3b11943a5c872732 \
+    --hash=sha256:d0332e2b27fc5cc761d6b8a33118b958e6a46be7f00fd30e03a5cf103350c0b3 \
+    --hash=sha256:d05a1bef52f4d7f1b484a1cf46a8929e50963f910e51396373f06cd3b6248f38 \
+    --hash=sha256:d14872ccef35972c4ac290f2432f43d0a7bb230cae2b5ed26871ab86221e8b5f \
+    --hash=sha256:d2742952851c7f88b1484385f68c42c6388153520efb40ff09fc852c3783aa5c \
+    --hash=sha256:d4004fce7b3a8ae5ef2af835670763f12723e9b9d74837697607b89a17f77312 \
+    --hash=sha256:d5024913651813801fd43b65b6409b0d50f8bae95316c8f1512dfbd8ca96cb1f \
+    --hash=sha256:d7a363c0788435ff5324d9582d37c63f215c75f974d755cfd6cfc9fbe0e64b04 \
+    --hash=sha256:d88fcc24470d73ed4360e910f8549718b913ba56fb8775d9ef929a647835dfea \
+    --hash=sha256:da4b0aef427eb96e422b444e5c2c3d38768fedb9141346294c38717a8b15b416 \
+    --hash=sha256:df0a34d445eea64f3766e9ca2ff57bcde600a89c7c0330434a7a37e8d6e2549f \
+    --hash=sha256:e09c37817768bb71fe3e70b6ce5e6ac1a0cd7398536c2f30a4460218c7b66e93 \
+    --hash=sha256:e269dddf5ebac20dfcc5a2a459528a9d221ab828cb31dfdf19c7cfacdbcee673 \
+    --hash=sha256:e2fd4e664a34854cae8db58ca6132fb7b5a7efc67b14233e797194bd0d63b6b0 \
+    --hash=sha256:e674027ceb6bfd959f1bb035000fd20fa8b717dc6765adaaf8bca347822c8c7d \
+    --hash=sha256:e6bf531deaebf8f69ba6015bba3fb817cab6694dfb69ac2a708889dc59a3926e \
+    --hash=sha256:e6c89d63d43738712ce1febddb7758ffeb56de08f1b2be68aeb9a9c7fee712c7 \
+    --hash=sha256:e72cf9556f799c3fce7597c1bd7dbfc9104befbd08088deb3b9ae9fd98117c02 \
+    --hash=sha256:e86a66f96d80c770daeed78394c1d4f6e8d03e5a3e08c5dab5275d56414f296a \
+    --hash=sha256:e8da5e158d13556457f69245deacf6d8401a2c9c31afaddd18bea691e849b5fd \
+    --hash=sha256:eca90e028932de597e2c50f454ad8cc631281e14d20b9f801a649ab555deb580 \
+    --hash=sha256:ee083412170118074bcc74361fcbc7104eb6d0b7c9c75eb3b84a4c324410c531 \
+    --hash=sha256:ef07aae0a666ef5edcab5bc1bb590468c6f4120a8cdad50a010d042a59ab6e77 \
+    --hash=sha256:f25209696631752468a25e5954fe119503468b3b29b6fa2c621ae766153c6f50 \
+    --hash=sha256:f5a875e92f10c6463027d8151459f2d92b4c13527402ed1301eaddabd79d8cf5 \
+    --hash=sha256:f94d465ee00ebe694ca866d66bbe45fa04618b1afcb377de934694f624fa7cf6 \
+    --hash=sha256:ffbaadf8612781358b3f949ad68dce26c5a35beaafcc48125fc231dbcce7d362
diff --git a/tests/requirements-nightly-ha.txt b/tests/requirements-nightly-ha.txt
index c03526457..8c43b0793 100644
--- a/tests/requirements-nightly-ha.txt
+++ b/tests/requirements-nightly-ha.txt
@@ -2,8 +2,8 @@
 # stages into the A15 heartbeat container to dump a stalled loop. Installed by
 # the nightly-ha job alone, beside tests/requirements-ci.txt; no other job
 # imports or runs it. The two Linux wheels only (the runner is x86_64): the
-# hashes are PyPI's published sha256 for py-spy 0.4.2's
+# hashes are PyPI's published sha256 for py-spy 0.4.3's
 # manylinux_2_5_x86_64 and manylinux_2_17_aarch64 wheels.
-py-spy==0.4.2 \
-    --hash=sha256:aeb0323409199c785f730645e9f4bb7a7b9ca2c481f2c331a55642b5d13fa52f \
-    --hash=sha256:142887e984a4e541071c99a4401ff8c3770f255d329dbd0f64e8c1dd51882cce
+py-spy==0.4.3 \
+    --hash=sha256:8a4277225f470d394a85cca0cdd944bef87f0097b6f20150a6dd3ac2e92806b8 \
+    --hash=sha256:bbcec46930d464b3bfc142d6d02ade4dd8ad5627823263b3eff0280e80c7c132
diff --git a/tests/requirements-typing.txt b/tests/requirements-typing.txt
index 54ed92646..9e4fa2a9b 100644
--- a/tests/requirements-typing.txt
+++ b/tests/requirements-typing.txt
@@ -21,14 +21,20 @@
 # <overrides> holds every pin this lock carries past an exact pin of the
 # package that requires it, which is the set `pip check` lists on the
 # installed lock: homeassistant==2026.10.4 (homeassistant-stubs 2026.9.3
-# pins 2026.9.3), cryptography==50.0.2, uv==0.13.6, pillow==13.0.0,
+# pins 2026.9.3), cryptography==50.0.2, uv==0.13.7, pillow==13.0.0,
 # astral==3.2, hass-nabucasa==2.8.1, orjson==3.13.0, python-slugify==9.1.3,
-# securetar==2026.10.0 and sqlalchemy==2.1.6 (homeassistant 2026.10.4 pins
-# each lower), acme==5.8.0 (hass-nabucasa 2.8.1 pins 5.7.0) and
-# python-dateutil==3.0.0 (botocore caps it below 3.0.0); plus
+# securetar==2026.10.0 and sqlalchemy==2.1.8 (homeassistant 2026.10.4 pins
+# each lower), acme==5.9.0 (hass-nabucasa 2.8.1 pins 5.7.0) and
+# python-dateutil==4.0.0 (botocore caps it below 3.0.0); plus
 # pyopenssl==26.4.0, whose 26.2.0 caps cryptography below 49. They are the
-# pip group's bumps (Dependabot #3088, re-applied 2026-11-01), and without
-# them the compile is unsatisfiable. homeassistant-stubs itself stays at
+# pip group's bumps (Dependabot #3088, re-applied 2026-11-01; #3323's moved
+# four of them), and without them the compile is unsatisfiable. A bump to a
+# package homeassistant 2026.10.4 pins exactly that is not already one of
+# these overrides is held at that pin rather than added as a new one
+# (zeroconf 0.151.5 and cronsim 2.7 against #3323's 0.153.0 and 2.8).
+# Dependabot rewrites only the version line of an overridden pin and keeps
+# the old hash lines, which pip's hash-checking mode refuses; re-apply such
+# a bump with the single-package route below. homeassistant-stubs itself stays at
 # 2026.9.3: 2026.10.0 is an empty release deprecating the package (Home
 # Assistant ships py.typed), and under it the ruler reads Home Assistant's
 # own annotations, a different measurement (70 errors at 2026-11-01). mypy executes none of these packages, so
@@ -45,9 +51,9 @@
 # `--print-requirements` re-resolves unpinned names and moved unrelated
 # packages when run on 2026-10-20.
 
-acme==5.8.0 \
-    --hash=sha256:44c4edb53acdd3fa8402cb29c78a6d1bd2005d777a4d2fcd12663bbc3c147b34 \
-    --hash=sha256:637501767248156545d85c23b806381ac346c5eac759f8e35052af85b7bb3933
+acme==5.9.0 \
+    --hash=sha256:a646011d6c7c843d89c91a901a2bf450752621f6431f19851bec1222c94446bd \
+    --hash=sha256:bbfd9cf42797b5378a05833c0fd917de9418b69e03cbdb39abb7e85e5532fe75
 aiodns==4.0.4 \
     --hash=sha256:c24dd605bac70a1676ce503f967a98483ff163507198557d8e9db16267e6cfd2 \
     --hash=sha256:cb10e0c0d2591636716ad2fe402e977c16d71bdaf76bb8cb49e8a6633596f736
@@ -263,9 +269,9 @@ annotatedyaml==1.0.2 \
     --hash=sha256:db1c3ca021bbd390354037ede5c255657afb2a7544b7cfa0e091b62b888aa462 \
     --hash=sha256:e53c74051a82c4cbd68db1371918a6399650f165579a2bf1f7e0a2ed58300564 \
     --hash=sha256:f9a49952994ef1952ca17d27bb6478342eb1189d2c28e4c0ddbbb32065471fb0
-anyio==4.15.1 \
-    --hash=sha256:6152fdbbf9a77fdec97731721bebf7c4c44f7c29b424b0065826173efc7ed101 \
-    --hash=sha256:9f28306018cbd6d329e64a36d58256edff76dd996fe423bc957326e578b82a94
+anyio==4.16.0 \
+    --hash=sha256:59bb03251907983d1603d27c3087ddb1e93299ea2163adcdba37899a4fb12ffb \
+    --hash=sha256:c66ae634e0b8228396b801741beb3294326d4b6102f7bba4041c0dfb58c29026
 ast-serialize==0.13.1 \
     --hash=sha256:02686b281ec9b8e9614f6f0db27e12e4cac515f336c5d05b678bc9eb73ff2af5 \
     --hash=sha256:032b09d86c785c3984e975378b7861f2a68ac44e22ba7b07b93a536b2524eeb8 \
@@ -531,12 +537,12 @@ bluetooth-data-tools==1.29.24 \
     --hash=sha256:f3cd96de927ddf3ec44813a829eea7ac1aea53592c0d1355866b4f5170026cd6 \
     --hash=sha256:f54ef148ad751eaf1686380b48847fec7f95c7a12c1593b8b062d92f38619e3d \
     --hash=sha256:fe6ef046b7182e7bc083f43835f8768c842d99f136cb6af1eeb9201928521608
-boto3==1.43.121 \
-    --hash=sha256:0599bdde7d0c03d914d9247b0a328ea48c15b0b3b5fb31a153857fa5bc7a4fd3 \
-    --hash=sha256:fc41ea80507416c30a3f7bdea3682124551ec0c36405c0d8149efaf65d9628e7
-botocore==1.43.121 \
-    --hash=sha256:39bfd17e69f3370350e6aac2072df64045d002f9878e09115e85b87c772bd473 \
-    --hash=sha256:69eb571c74ff140cc3a716aed3bc25d09eb7b12de4ea2f990c03785a634f9dcf
+boto3==1.43.124 \
+    --hash=sha256:62edd40fdeef6523ee2f73f4ccbe754fde79200ad0763bd86f4422e8125b2735 \
+    --hash=sha256:7f330e53e274a0b8e5982ed3dd4cec9e7e932cf48306c08db8b9e880d09c5c63
+botocore==1.43.124 \
+    --hash=sha256:4651bac68d1aef78d42c8aefb514a6cd86fda07971b8348652a9d24f21b07965 \
+    --hash=sha256:6df80235995e2926e0768e7ad270e774adcd6ff0307da7ab87ffb8c384edb578
 btsocket==0.3.0 \
     --hash=sha256:7ea495de0ff883f0d9f8eea59c72ca7fed492994df668fe476b84d814a147a0d \
     --hash=sha256:949821c1b580a88e73804ad610f5173d6ae258e7b4e389da4f94d614344f1a9c
@@ -1262,68 +1268,68 @@ greenlet==3.5.6 \
     --hash=sha256:fdacf26402389bdd89857ad3c045a26fe8f3314f9a8b28226f82f88463a65b77 \
     --hash=sha256:fe3170a69fe039b18ad18171e66faa9a75f6fe9d78f968fd9b54e09fbd714d81 \
     --hash=sha256:fea4427d1ffdb3b523d7daa6712038428a4c16c450b9777bdd1221cfee0eab49
-grpcio==1.85.0 \
-    --hash=sha256:0633c4ff112d2237d09ded3044b5acee4fb12de7b39ff4dcfb09b0f029c33992 \
-    --hash=sha256:087f297442a62e267f37df0cd03681159c225b8e73741b94d55c515e7a4df81e \
-    --hash=sha256:09ab4af4c4c74baa9b17f9a6fcdcef5be98357774417d624191ec41690df4bb3 \
-    --hash=sha256:17641f3a6ff3512c34e5c367805d2632a43a773d7990f1c4c55243df6bee8fbb \
-    --hash=sha256:1a8ee918b5b18c82be2e5f30978258269b858d7e16a36e8729c09d9654bac2f1 \
-    --hash=sha256:1a94f32df519cb7efe3822f7f3c2daee0b0e2f01a281e1db5dbfb0efd1635b6e \
-    --hash=sha256:25007d0e4657dcdafa9a80677895b71de8c1d6335afb7fa6a4b35330e2d3127a \
-    --hash=sha256:26147a7a3c9d1c865cc16b3f98e5c38e5606932aba236b7627ca7eb4378c5c7e \
-    --hash=sha256:27b024f8420c9d63f7df9f51d4c2d2e54fcf3b26c9963041f5fc75b83f35e87b \
-    --hash=sha256:299b13839203e82be15216ae4c3379801a3ad216feff05b165f14962f0939b0c \
-    --hash=sha256:2a04b67a146f1a95e2bd281614be89b662973535a94eac944135ea86b2e5a7ef \
-    --hash=sha256:2c6a55a4cb43fe9b14d4aae123ee655cdeb288d8810bec8f8c1adce0d4359d8e \
-    --hash=sha256:2dd69ec2998c2285c323bfa2e3acbd7f475881db97aa9359f2edcbf9ae284169 \
-    --hash=sha256:312939c9afac5d9d5e3b9e50c40a9ebfbe444ca35b28a99ce34903cc9279a5b5 \
-    --hash=sha256:372e9cbf91f74127652138b020cf15c6a44541a91aee89c50a5943d1996b44aa \
-    --hash=sha256:3b463b3b97f35149a3f69234de92eddfd7c94c9c19794e3b264ccba7b6b03fac \
-    --hash=sha256:3c49f03d8d74196ca6d1351b749aab3fb3362c850286f28aafcb7cd773134b04 \
-    --hash=sha256:3ec59a8175c0bcf51ac767c7baa9083ec369284e1055614bff246257349d4e19 \
-    --hash=sha256:426e41a32d10f841f41fc67e4e6d150af7e7c7c3433fe61fa3a0ca19a8dc9885 \
-    --hash=sha256:4c6c39eee05f6b98266315486a93f36d73a59adc4d34f8b63f1b5725f897d8ea \
-    --hash=sha256:4ddfe8b667889b9be5990ae674b13f0db0a9eb61972306038d0140a1da0f0b87 \
-    --hash=sha256:5427356333810631bfc3541da05fa57bcd4a0bf846728d8512c9e4bb1f97b261 \
-    --hash=sha256:55a1df9e50009d85fe674fbfe31710b6b3e83702c857114832449c498e78593f \
-    --hash=sha256:55cee7cfe71b29f6b377681936f9a5f35e59f5c941a4d84e2712cb309753e7a9 \
-    --hash=sha256:58c0ffd1eb2a0d7d216a0c8faefde999586fc017e735dfe9d1142a8481f7d0b6 \
-    --hash=sha256:6127bab580cc247c6c62f460485afeba10ec7b9e1b338eef8bde1344acfd9ab2 \
-    --hash=sha256:6248ed9a86c4191a0d8d7fe54eaea0511aadcadc2ec128daa995eaac91e42880 \
-    --hash=sha256:7a24e53259c2005c77b03c48272eec4b374eba027d077e84d0e99f9e30747439 \
-    --hash=sha256:8572f9d7282cded6b018fb0147d09bbe7e59177ba6c452f1903682a80dc0857e \
-    --hash=sha256:864607775e0166a4d3d6bd8276334d96f0b6e9e0a84f3964dc6005db07e9627b \
-    --hash=sha256:86bd1d2e197d3e4cde1c04136db48bf22a6fe873b7f55c83e9747d5b36f0cbb4 \
-    --hash=sha256:874af68625a2ff2585cb112e7583c19a7cb463ab638a7fe5b8a58f76e6d4e7c2 \
-    --hash=sha256:8aa2647afcbe5a87783e9626a2ece6277db33c6604c21690d19b5bd15609e36d \
-    --hash=sha256:8f1c7cb18d7beb81aa65666b739f8a43261df7f9529628e639b578b6d344cdf9 \
-    --hash=sha256:9c91ad19d92ff81600c087db4829c26b47f9dafd04ed0a26c35e21a05d20f671 \
-    --hash=sha256:9eb6e4149d2e8ea7fc56052eabd36f1bd52a3c0a53f1eeec74528654a895456a \
-    --hash=sha256:a03fee5e413938ddb71aa2fd7c52520e2fc3aec2e9602d50464272c75b274a54 \
-    --hash=sha256:a11c8c322a19d6d3cd6fb645127e8f1ca4e8041d05e41e9b24c7678ec7391021 \
-    --hash=sha256:a8dd5c3823194811c5e6932b454bcaa7b8e474a7690ed4ce6246bd502849a82c \
-    --hash=sha256:b016a4663ee8ec37b0e555a65fcc129598404bd5c14d8c00d03f8da551ce0e30 \
-    --hash=sha256:b10f0f0a34ce6b122dbf5dcf8226cbe41509c602af926b1e55113ad9e49cc5f7 \
-    --hash=sha256:b1ea46f63a7a9e19ce5cc09be0a6f9b347e0dcc14c4ab47b48488f6c093b8171 \
-    --hash=sha256:b2da79c303f23e66d08baaa0c78d8b8630c700e1562babb1f326ada0a97ee5d0 \
-    --hash=sha256:ba535a7b78d5049101a896efbb4ef9edd471c322ea4fc0cc8245545b184ff687 \
-    --hash=sha256:beb6ffcf5253f4247efa47837d876e42157969127657fad4a68be181830ddadd \
-    --hash=sha256:c02d956990c55730efcca487a4eac64f8e0fcb3af7e53c9e89cd02a985669709 \
-    --hash=sha256:c5f993fa6b3bf0af33ed7c2bc42f58d22f10964607cf614c2c08b67db80ced60 \
-    --hash=sha256:c8accda49358f99875057ff1ec6a79fead12dac41ac63c1c1e1757a2aab14c1d \
-    --hash=sha256:d115d1d4e31fa964a348e54445154cce1649da4204f07425028608982d056a2b \
-    --hash=sha256:d2ba969495b45ff5e0d10451898387427906b82e28c3c1cfae2dda006e25e18d \
-    --hash=sha256:d617b017395ff7a84fe0aa682890a366afcdd502f2610029052165cd3778b561 \
-    --hash=sha256:d6c43a06a059a95f03013aa5fce9106a6a2b6b78cfff4003a53e0eb410c0e1d7 \
-    --hash=sha256:dbd651df4cf258f2073f8a10f878cee9b8723986ca69206a0da67a2f1651ae86 \
-    --hash=sha256:dc726ae4f2f4e2215cb1b987b8ddd7f4f2f253d6ceb48cfbb9b88555d325e10a \
-    --hash=sha256:dd88a98073ebc0e6771ff8c2fd9451fbf887f575b0da9d30246ee1b2813f6b57 \
-    --hash=sha256:de5b49ab15a350170905b03c03f88f277f83e1910fa87e6f12c63f2da7480a4b \
-    --hash=sha256:e0b87fde3b80955343b37cf9b9deac52432e9e7a4b3e0f92abbd61fee0f7b184 \
-    --hash=sha256:e2f1c3089ed6ae75e24529a498a6b65941fdb6856c3416d62c88da944947fc88 \
-    --hash=sha256:ed8ca34cc644a82602097249bdd9af2526f2fe93c641439a19351f3ed2e91de3 \
-    --hash=sha256:fc1a478ce75e66ab9cbf7077bb12b2a31f75de091122d48845f281f8fd47a0d7 \
-    --hash=sha256:fc2865f523feeac453f35c762a2e4155df58565229d77069b211f2e21de2e79a
+grpcio==1.85.1 \
+    --hash=sha256:000999ea9bba80217b1625782d638e7a688790f6154e845e18826f7da859bfc7 \
+    --hash=sha256:016982ebd21d2b48e955aa808e9db8d628708a35c6eba852cd0e70765826ab06 \
+    --hash=sha256:07675c635a2da0c772e58ac736a7fb10c7c7c1613157766441e6866ad97d25b4 \
+    --hash=sha256:07bfef5df75875d8481d3403f864785e30096594162e8041c53a84fb11ee4f8e \
+    --hash=sha256:0bde4264ca71aaf3bc56c587380c426b1c959d1db0ab0a3f632bc66515f9726f \
+    --hash=sha256:0e07f477e1d1a05bdbe71d63add964c5457e7ab2e3f5fd32859639ed8ecb976e \
+    --hash=sha256:0fa3d7b8b95e8a609967991c3b0a302b2f9d510fe417efadfa7c7d2d044a99ba \
+    --hash=sha256:1a10d337967ec2be049c6a2345320f6a59f71bf9f54febfd80e5a966cffaa945 \
+    --hash=sha256:1f04e51dc65c82af420f6cd177ea76132a78c14dc7adc3044f549b419bc70487 \
+    --hash=sha256:1f3064e209167e5fcb75a72cbc18918c06027b92b29fa06eaff0126f9a2aab5a \
+    --hash=sha256:2198269c8b69cb1e9d5d20628029245e40b7227d5f6fc6f298a420701d8fb652 \
+    --hash=sha256:2670c03d154f6bec66a0fef97c607116761b032183187dfdfe229b5975820a4f \
+    --hash=sha256:27b519f6594da04cf2dda1378f46811b2b6160d60a01f88a0ec4de009bbbfa46 \
+    --hash=sha256:2a378eb60ea42996be5a8c7167302fb30d968fcfcf9edd7b3fa6c985906c4500 \
+    --hash=sha256:2b20ba567ca818b8393fd4668878b5688cab32a46e8e7a4d1a58641fc0072df9 \
+    --hash=sha256:33ec3a93446906157debed3333462cbcf7c52e16f86b6bbbcae992808f1bed93 \
+    --hash=sha256:39b1965266b579f3758db20d74f9075b130d1b1edcf0464cda316e403a15da9b \
+    --hash=sha256:3bbf7ae798e38eccb1b7abf169d9e228514418da6f68caec69a295fde899ec17 \
+    --hash=sha256:421925365f9a665830eded01b8053033abbc2fbabc9bb4e9c59c3b5b12acbab9 \
+    --hash=sha256:4c684af6972a6c22a049003830e2c78ee8c40623bc8d1106e4b4d2b955549bcd \
+    --hash=sha256:4fbe3213b60b8b40bb17f9997c1afc8ff9f61c4cec0d224d482bf799027f5fc8 \
+    --hash=sha256:5740aedf1e6acde538d7b80a2507eb6ee0b8983c577a36890d27a0e2b62cc1eb \
+    --hash=sha256:58b5ebe509da292bec5a1913c1e4c14d842a33f6cb330a87d3713c5089dd0f55 \
+    --hash=sha256:5f015600190124813032da0560ec950c13c257f77c1307abd77c393c0994f76f \
+    --hash=sha256:5f530287d5de5f7f66089ead81de44f6787162944dab3922efa65dfdff108a1d \
+    --hash=sha256:658a9d89c5736bf4aa3ef4ecbc79528e26d8e23c5e1c83417d2870a1a06063e5 \
+    --hash=sha256:6bb4bbb5cb46010687db552fd88852c405595814fb7d435b072124bd6b93f827 \
+    --hash=sha256:759f7df78954e3ac0ed4c87612eff9125021b9271be37be8c88167aa533e29ee \
+    --hash=sha256:7a09a7e89bbd8dba2bf5dee77bf6d0485120f4cffa209a89cb3dce5575d625b3 \
+    --hash=sha256:7b931335c163510fb054c30007fe3556ef3bf354a1c37b5da403f2e52c6bbd95 \
+    --hash=sha256:7bc5de50374416223bc35332aa8185567ec065f86190ff0ca6e13176ed39a3b4 \
+    --hash=sha256:7cd08bd5ad063ad9639dbebf95d3a6b8c8aa2c9d49049bc0e8f47e73ecf1c1a2 \
+    --hash=sha256:83aced2a1c05648cee0de34e531351118b14c58238f0a61b43559ac8851647a8 \
+    --hash=sha256:83b09ca3f9602caf4f1b4295b4bb002b10477789ff9797feeedc811b9a6be0b7 \
+    --hash=sha256:843aa281a48188621f50880496d35defed51298bcb66d5345d5f282fd3f87354 \
+    --hash=sha256:8a921a98ed6142a29651b4a6f4c7b8e051d115f1e78c31655a9642dcf6356dd9 \
+    --hash=sha256:8ee487b0fff73b2619c08ff09b9d55e8221ce5247984b450d51170705ceedc28 \
+    --hash=sha256:90a7e0f26de39d15f5c741b8848bb2065c9ab7351c57d4fc973ff5cbda0cb9c7 \
+    --hash=sha256:9885436e83eab92dd0d476642baf08a17c55ef2b1db430adcba3e89bb6938a5d \
+    --hash=sha256:9998f03ac0dfed226eead6e93cee1b547d7a32e47e1915dee94eff0e113b167e \
+    --hash=sha256:9db68bebb101a1dc77e21b06ee1f9a1ccc64d108f2b9a38c1716738b7786082c \
+    --hash=sha256:a1a72d19c0ab84b4b73b6c47eeaade76d84b1973a51593ff1160a73df33d03d9 \
+    --hash=sha256:aa41e010b528bc596fc7c3020640a84987a8f3d3c239a93336faa86ca41756a0 \
+    --hash=sha256:b2846c70ed58c8e149e8e5d867af40805a13b151d84157d8272952d711a77c5c \
+    --hash=sha256:b32f39c56d22d2e8722eececd4376074d94e01595a29f4f944ae0b6cea1caa70 \
+    --hash=sha256:b364bc3daa601eb1cb0023e90b1309cbf6da0de6ca40a19f2d5a31edeb9990e3 \
+    --hash=sha256:b3722f4e01820f4d2422679a567fe33f31b6f14eba4352657a1078f4b4ed323e \
+    --hash=sha256:bbc678a2b8d10e0dea666d948f36237e681be3686079564937df689bac386bc5 \
+    --hash=sha256:c17d61af28b322c48ab3881c685e5f6e7e367c56844cf589ee7707be9477b969 \
+    --hash=sha256:c5a914b3a3052d841766946ecd1c6ebdacc8bf166d89a42c83fda70ae8f53aeb \
+    --hash=sha256:c6efed2139eb7e6b7e6724ad1d1e5402a11dc12ae948a0e1f98d5cbbf3a8fbd1 \
+    --hash=sha256:c9a4a4e504bd914e10c0d6190ffac59b9e21f1c962366b72293075ade097793d \
+    --hash=sha256:cfa9bf4daed57dd5bd5fac4be3276f5dc1703f41abf4df0737f4e7952705cbc6 \
+    --hash=sha256:d2a776b113e7bd6d139e679f5da281193d6410cce361e4180c9da0d553e01927 \
+    --hash=sha256:de520b1555ae445cdc4f8f1cc7ccba12a19992bfafa7c292ebe7fe1fe5da6c53 \
+    --hash=sha256:e0e6d5829b50a2ffcfcd2dbf08d02ac0d6919051a2e97c2ee27c99bc9916a245 \
+    --hash=sha256:e117b074d707d418ff411e0ad6fc86e97e83047b742488b41d7a5b7a62953cd3 \
+    --hash=sha256:e768556a2346d1d2921f511f3145e2462e4fe68095c31e4db407558bcd3f1d4f \
+    --hash=sha256:e909e0f9145a555d3968dd2a448616b0d3cb58748b9e2053de3e7974b3e429bc \
+    --hash=sha256:eaad7e6aa9ac3aded4f6bc86a18bf2cff3de356f972bf32a5558df9788085b85 \
+    --hash=sha256:f0ebfbd8ba42497e0ff7229c8c5e166e07c2b348462c1481dbd90faa978ad8af
 h11==0.16.0 \
     --hash=sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1 \
     --hash=sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
@@ -2019,9 +2025,9 @@ mypy==2.4.1 \
     --hash=sha256:ef8d5be90032261197ac388d945d8ff4f476c95880798a1911760af64ddfe71f \
     --hash=sha256:f44dd4c5ab22df21206dd926c98381ebdbf5bfd696df37dd38ded2d23143fcb6 \
     --hash=sha256:f9118a3f50de264b614861bb11814833a742138ac3c8e2e49a860b6977fb2704
-mypy-extensions==1.1.0 \
-    --hash=sha256:1be4cccdb0f2482337c4743e60421de3a356cd97508abadd57d47403e94f5505 \
-    --hash=sha256:52e68efc3284861e772bbcd66823fde5ae21fd2fdb51c62a211403730b916558
+mypy-extensions==1.2.0 \
+    --hash=sha256:993e7a20aa5671eb41a7132cf555af30062da99729601601b9a8382b11cae768 \
+    --hash=sha256:c6e275a07f1c2fc096b62940452d0eaa3f3af7de45d704787866240a7c6d5a51
 numpy==2.5.4 \
     --hash=sha256:067374eb538c34c745436365cf7b0112595c1d326f21ce4ff340f61230239fbb \
     --hash=sha256:0b4724a19de67bea8cfc4970798efa78bcbbe2ac2613cfac16721a42d44de2a5 \
@@ -2555,9 +2561,9 @@ pyrfc3339==2.1.1 \
     --hash=sha256:b144d63819bd4c1ebf9cb57e12f4cba567fcf23d6e8f2f829ba9c7810ea4b951
 pyric==0.1.6.3 \
     --hash=sha256:b539b01cafebd2406c00097f94525ea0f8ecd1dd92f7731f43eac0ef16c2ccc9
-python-dateutil==3.0.0 \
-    --hash=sha256:3c79630202e4152c6add678446984236efe4f57e84d8e892aab0637bab82e9fd \
-    --hash=sha256:7ebcb3c29a92f3ceafe79a7a48a5c45677e9e004bbeec5742ac0bbb00560b7a2
+python-dateutil==4.0.0 \
+    --hash=sha256:a5e246f79eb80475e691bf93862cead98decd8a498cf53ba0516fcdc0f50dc1c \
+    --hash=sha256:d7295ff14fdc0f92f662100bfb6c551d160ca090f2939f1ec5b9794265c03f06
 python-slugify==9.1.3 \
     --hash=sha256:90e997f2e0987239ce95e12f700086eb18e1d1d3ee22624fbbdbd095afca42b6 \
     --hash=sha256:9aced0670e54c5603e2335c0fa9a4011ad4bc41ecb3c46e8097294c46fd60ed4
@@ -2790,79 +2796,79 @@ six==1.17.0 \
 snitun==0.47.0 \
     --hash=sha256:264975472011b7a211e44880c614d5534f6fe953c125e0cec365bae3a169c578 \
     --hash=sha256:57eb4710f13a03360c07527c8e2d442b8c90e8ff7b94c71228cde5da8dbb755a
-sqlalchemy==2.1.6 \
-    --hash=sha256:015bd7b0687b5feaecb9988bc2f36ecb39daca83bd806b094b43b19ea503b0a9 \
-    --hash=sha256:048d1beb9bfd7ca1afbcfdb8da9519712827df6cccc80a225715ce387d37bb3b \
-    --hash=sha256:0534d3f41295a74d9fe2e0838e06ce6329a0855b2965df5f5d1c4d3f6f1406d0 \
-    --hash=sha256:0bada6bd29ae58a0581bf6977c0a43dfd67388fd09129f1475c37eca370cccd8 \
-    --hash=sha256:0d0424a4189f95886c78b48bb500a1dd7ae6dbae76deb552b15813dc298d9c8f \
-    --hash=sha256:106878cf3795cd3d357e2e858609f9e44f20f19b2d8e48a3532bef3f90b03fbe \
-    --hash=sha256:10a4fe106adbb46c9452f750d8a5d4013d9a7e9752f63631c3b255c062b748d0 \
-    --hash=sha256:17bc5f508f5e5cee2722a5a14af0a48768b40e1fc5d1bfc92abf6ac587636bd7 \
-    --hash=sha256:1927eabf26265ed962627e7a64626d9058da29cc0faea341091302ec108ce305 \
-    --hash=sha256:1b5885ad1226c8eeea6aeabb4c4036e43202e1bd70cc7a50ece98bcd6ebe5566 \
-    --hash=sha256:1e12763cb2a400879c6dfe34995a032f707de635c8cad14d6ba777a1250be90b \
-    --hash=sha256:1ff897d13de613768123dee68474956a51fe641c42bba7af6cb7776716a8dbcb \
-    --hash=sha256:231d0fd85866f847c34c915116c386c83e677ab6f79a94c835b7ae7313b86095 \
-    --hash=sha256:35348ffcbf686055ea7fd02ba4eb76060ed76761648720c63170c5c8bccd85de \
-    --hash=sha256:3974e33fc322b645eedeac8a3dea93022466fee41a6385c744a6656aba293cd4 \
-    --hash=sha256:39ca3a128260fb3aa1c33554f1993bc5ddf3f82375697028c49e7b411ab80b84 \
-    --hash=sha256:3d877b2c46298825e8f32059e8d912d0d100af0e9fefe31fb2abb52192817afb \
-    --hash=sha256:499eae5c9051efe96cb9a73ec2fbde8ffa4186f102b9094ebab8fcc9d3b99f52 \
-    --hash=sha256:5a9b4cbc5f5cda3c9429e1ac503a57f3b95c59886f26af6ffb44e2e7628b7df8 \
-    --hash=sha256:5f9400b1234555b9ae78450123dec7aaf045d8d978a1e94967437ebe561ae120 \
-    --hash=sha256:61dc3fa488208a2f03e0e25ad32950dc024545291acc7348f2e550ea1bc5abb4 \
-    --hash=sha256:641a3742dac4b8f325667b585097de0f1d20eb3498506c92d5f04c20b3a6c823 \
-    --hash=sha256:650f97996a4c529f4930969f3ba11bcdb57ff160ed1cb87ea0174393bf4f5f73 \
-    --hash=sha256:654192c9f192459ee5f63e6606cc6dd8c50681c28e0689d2a494fc9522b357c1 \
-    --hash=sha256:69eeb530ce74be5e202a98ce35aa58b0776c24e64923c4873c25fa56f8e423bc \
-    --hash=sha256:70b435f719d7156623f49ac6539f30dd8471500b5acf399f3b318c1c17f6fa7f \
-    --hash=sha256:73aa8d2f911a54d1310e8258a752207e2d7624f4db46e2320d734fe7218320a1 \
-    --hash=sha256:79c1c20dffd4d8d7e669f096c88f261da8ba3646939cd3eb6faeccb92bae99c3 \
-    --hash=sha256:7ea80b33e57f918509eb91cd074324bff0f9aae40d238121cdc369f449c20649 \
-    --hash=sha256:80009748a5ce0c51a9947542935f9709a1c48b65c69f4a1e56d3072f99e750f2 \
-    --hash=sha256:84033cab9fec2a515a62d76a7b4acafa83339917db9ea911b65b017928ae7dd8 \
-    --hash=sha256:84b359a458611d40061f536b1363733b0af7a71425e4b17d0abb7e543d00e979 \
-    --hash=sha256:89d05a1ef531a1fee86d68e731c428b773bd37aabf743bf63dc3709c86f7254d \
-    --hash=sha256:8de444335e3723959913f6635d579276a3517b8c19cbdfaefb04e73b5480e88b \
-    --hash=sha256:8f9d12a8be271c7a83ded1cb7d85921f1b7f65c655c8dae972130a190211bb57 \
-    --hash=sha256:9245bcbcc3056d440f82e43fb34f94c15361c86b62e14cd9d7880c8e0cf370f6 \
-    --hash=sha256:96ace18758136905f8d5588ec35d6ae4fdc29ce4e4902518263ca33abf10de04 \
-    --hash=sha256:96f5fcdfb7e89b6d895e2ddc165f67b3126a585dfdf2a95b0c1f3fcf3380d7d4 \
-    --hash=sha256:991fa7c6756505e3dc5aad678db5fb0110d9816c2185bc3e2c520de46cfc8c5d \
-    --hash=sha256:9b197f5d2bcd61b939d2f04b77e86ef24bda266518f3e1526bf666deb20d3ddd \
-    --hash=sha256:9b6b5fdcdb6891025117f76f48d7d0f89245d66fab6519f3b856294bab317387 \
-    --hash=sha256:9bd573f8da863781ace89950d57a959397d5048b1cf69931c29b2b4ce1405bd7 \
-    --hash=sha256:9db8bacb2a69b4b5388bc1439463170af28f4cc710933085b81d1658d931d2c2 \
-    --hash=sha256:a053a9d9c9ccc9b72d90ecdcbabcbe57446defc7e8c52fc9978188f78742ac19 \
-    --hash=sha256:a4e4782514c16753f8bce3dd925cd37d26c847bead06e179af6fa4993ce83e88 \
-    --hash=sha256:a909a8eb82ce5a2f1566ebd685a79f3cfd9e049d57e3a0d3e24d56da04913e73 \
-    --hash=sha256:b16a8960ad9cdc923b90dbf431a4739fc81a07b53374ff74b7bdad3be31ce189 \
-    --hash=sha256:b25199a1b499da643de52ab73e972eb07e55e2a95bb99eaa491846098fa2214c \
-    --hash=sha256:b7ddb305126d34fda64c3fe4632a43fb9b724da6cc7d1dedd8434e6c783b285b \
-    --hash=sha256:b9f0b92b4a88b630f1e67df816b43cb017bb583479917dd100541d4f490a9517 \
-    --hash=sha256:bc495d00f235c3df6f376187a4ef48a56e162fdcc0a113ee34518332aa1aa2df \
-    --hash=sha256:bc8b805fb04472e0f9cb3bc6aad90f24b202afc274b7b8bbd48042130e82997a \
-    --hash=sha256:bf883ae772971bc6155cb64cdfb9e31c50a2099f3b7c8b51b0401bf608a9fe8e \
-    --hash=sha256:bf937348d4052eac6cfa93c809ad214be75b1f057e3fc0dd2e374a814a23a16b \
-    --hash=sha256:c314bf9026d865c2b2f67f3b853b4e2edcbe7ed46b67ef11b4a40f0af6aa17b8 \
-    --hash=sha256:c390f76f2fe408aa1a3121f3ca3d5c15698e14d913197417355fe3dc016f787d \
-    --hash=sha256:c757e13b63a25d59a2566c9b2e77adf14d969207a375ca82a9b4fa1a04b37845 \
-    --hash=sha256:cc60fffea328f38187a4fce43f99c6bbf930de2b87b78251f43f2ba64a1af622 \
-    --hash=sha256:d106c2191a3a0dea6873c96ab909f31c13978913714a25023f492e9ccc8ffcc7 \
-    --hash=sha256:d5e4b4dcf85d7f289def0e3167f15aaad101b7744a065fb2019476edf306712c \
-    --hash=sha256:d6e1a9ae71366164800942c477e663b31f3accef55d2e039cb7919fdb54b0086 \
-    --hash=sha256:d8c34c200a124a1a5769671613b3fc05a21d0a50f7ad942cf0ee12d4390a112c \
-    --hash=sha256:d96186af967d7ae3f76d1e9a8fb70b5beb0f0dbdacfd3b418a946fffbb8781ff \
-    --hash=sha256:da21b36d60f47dd04042e9372ffb3d1ededf5c60a76d43f8c3592221fb2d41cd \
-    --hash=sha256:e269c68ec200538ae3fa7f9e8d8ed2b4b34d974c25945286ccc2a488438acf32 \
-    --hash=sha256:e4e4a43cde0dcdff974304ddb48246d6a094e618b6ee9642827ddbfe9fbebadb \
-    --hash=sha256:ea5f3dd7450669acbfee7813d3a2a13876806b1d9e4c1626a7bf587c33c68472 \
-    --hash=sha256:eafb738fbcba39d12543730eacb65e2d5d627965959b3cc6bd6f797b2d52cc0f \
-    --hash=sha256:ed6596fb63c574fd3dc4d9ea58a7b9c6e7235dc3d74a0bd3791559d5a618e947 \
-    --hash=sha256:f0f22627d6436bd120c6dde0936b12fe75498d1e2e9214ec9863be17f9b80997 \
-    --hash=sha256:f1e78019147ff7e08afaffb88fc3a0aa795171b147eacfc7ff873ce7a0d37dff \
-    --hash=sha256:fd1154c6394892e727ff234273f5eb2b4319e5714917b016602435d77add8dcb
+sqlalchemy==2.1.8 \
+    --hash=sha256:06ba41b90d1cf018cbe9a5474958dbdd2a72ec946ace8d314021d24e42ae2f39 \
+    --hash=sha256:06e30b673ec8a89b398e95052c2c42d9e0bc0163940cdb7d32f36a79c0d12f3b \
+    --hash=sha256:08634599ccbeee6528b645f08516d1781a009422b22723a27b3331e26955d95f \
+    --hash=sha256:09a78681468ecae9b3e65de8afe20e74f36bf5c5d63c4c26ffc28b05858e3bdf \
+    --hash=sha256:09d190d37a002bd2984e3ebdbaf81f7530bb848736860bbd22e81cf417b067bd \
+    --hash=sha256:0aace49c6d0fc854bf600037df099ddc375ac2673747b6b0f29cdc6a3f96f37d \
+    --hash=sha256:0b239d72e4a6b35d5ddb7e6f3442e4c350def6165b1adabef65b8fa9a025cb6d \
+    --hash=sha256:0b63166df937ad4948a4a35ba67106a73b529c132e46a0ffbe82076abb0bbe57 \
+    --hash=sha256:0bf96e2ef5b5395adc7120de938a457d820fd27bcd9cdb300964140906e6777f \
+    --hash=sha256:105a13be11045347a78e1599adbcdad895c32067696bca9ba02754ac32f82699 \
+    --hash=sha256:10a62fe79b1f4861760e50aa968be71348b6a0ec6914e20221a2d8c506925280 \
+    --hash=sha256:141f4bb653b9acadd33edd2c524ab85ec97cf5d781eea0e6f6c4fb8b517203a5 \
+    --hash=sha256:1da7b54a7b3da71abbee002c0854f843f43452d778026db7cd65ff6432806540 \
+    --hash=sha256:1fc68555af5ccfe5c6637e84a556319a82ff21d9150d3208533722bf3108db17 \
+    --hash=sha256:205dfb38f3d8bac38dedec30110160db0331d71c7f04e6180e5b4e07d1debf0d \
+    --hash=sha256:28876f64e7a5458acc972013e5366e0e53c59ba04c6a4a4fdeece58318aaeeaa \
+    --hash=sha256:2895f18e332143a70f4e226d789beaa6ddb6e6b5fb9568e5d9afc3a6dcad7d03 \
+    --hash=sha256:2b4fb02b7cb4e7c76de89e13824b30bff45b2fbbc585a468b9a9a1588e5ef744 \
+    --hash=sha256:2feca3677281ed655a68b64aee68262cb867675cae8ef5066edd065a7fac4106 \
+    --hash=sha256:3418927e5f2a5bab86ea7ceec378fe7760feb736d200f0027d22660c5720c5b0 \
+    --hash=sha256:35e930696d2add7671e4ef7738e90a54d7cbc31fa0da8efe3c4a76a684c25cfa \
+    --hash=sha256:36e3192f86fbb32d7267af6a05e36d1ad4c5ede3d7c17165bddb6a7585b3ddad \
+    --hash=sha256:399082c1cc5ec4ed117b46501194ad3c99ac89902679916caed0047018e2ceac \
+    --hash=sha256:4523d270fcbf771ab3e25942485530b0209567e3368036ebd6c5a6636f6856aa \
+    --hash=sha256:47e2bbdc32e7bb26ecb796a60bacfe5fa673f01d0a6f1f06377c201495159a6b \
+    --hash=sha256:4b8c3559fb4382136a45b12a9546055781bcc5898a6b223ae8bd9d873c210df1 \
+    --hash=sha256:5af2275f5607c10bfbf69de4339ecc98d17a8ae5ae67f6686c30d6a6cc52e5b7 \
+    --hash=sha256:656bc82cf54f90c2e3909c5f9416710a46475deac462607bf7ee2ef9f47900af \
+    --hash=sha256:68eeca1191731d101bae85e3dbc6447c66ea6768d1f49bae104e2875e9e24814 \
+    --hash=sha256:69aea77b5d8a64e95d01fd7ec54985c84b4a8ef3cac3108e9271145441400c1b \
+    --hash=sha256:6b9844ecf59d389648cf3ce2b387475f81b02c2d32f16b95a554ca535a68ba13 \
+    --hash=sha256:7508d657d624d88508fa5e6d05487073edafed57a222d4a8bddbe8a7aead3fbb \
+    --hash=sha256:862af4d5858840f2f444821d86c38c75d13288fc18ab114f0f876644620fd3ac \
+    --hash=sha256:8a76bd79630e18b1defd176b889dd16cd88a44c73a3660a29594ff110dc626d9 \
+    --hash=sha256:8af07d4dc094fb81d218c05176bba00e3c75d67fbe813b47b8b3593a27add533 \
+    --hash=sha256:8b710c896f3e3c59cb70b5bf73c8e28e13e7c60a2e28ea478bc182198efc6725 \
+    --hash=sha256:8bc4081dd7c17c073f2384ad0f5ee968e63b43507b2e024a3523c000a06d70da \
+    --hash=sha256:8dd7ae94cbbb6e58d1c03de044b8029d571f445feafb6fafc1c8a21598706f8a \
+    --hash=sha256:92604cdd92b62ea56e8b04d6ce40a939a18a75c87b7a74e86cd4c562178afccb \
+    --hash=sha256:92810a47ed62fc17088e3d7f3c8bde407b53bcd1c113a50e2d9433631bb3c230 \
+    --hash=sha256:92f87e53ded137e29231e05409eae97fcec0d0289378e98e26d0d327a1a1bf03 \
+    --hash=sha256:9587623885c13b7c53354fa39a5edc7cf5388dec708e4e6d04e7b6868941a2c6 \
+    --hash=sha256:99577caccafc97b712f250c0e251546e97e6e64676213cf6085a63386fa48595 \
+    --hash=sha256:9e08e91fbb02d7d659586d8f778fbc4d388c02e2592d245cc98b454ad9169d42 \
+    --hash=sha256:a092e37949aec29964e3692a40b40380604fa7dc0186aeae372f64a072e9049f \
+    --hash=sha256:a4fec84bfe7a466ce29d2c01740b29217ec6a64c7da10975475649bf1e1a6513 \
+    --hash=sha256:a6dcab1a7200ef01f9b01cfc351673973c0c856264dd396ba71570c58916339c \
+    --hash=sha256:aaf1e9adb18645bec3eeedf89342d2970103399207123b096284c3741b64217a \
+    --hash=sha256:abec8d471bb08ecae25b08b24284e11439b215ec9d09ffbbddb23f9b3a8b425a \
+    --hash=sha256:acc8de93461dd9259c5e5eb42c26199a94ea2631f49a11d659d00e375294d48f \
+    --hash=sha256:aea7192a4a21d0b6999a4ebdab76af6d31d8c2d7397b2ef1008301c63e31ab78 \
+    --hash=sha256:b1a12d2b8411bee0cd8d6b3aea3282ecef1dcc61f0aafb094b9849ad559f7301 \
+    --hash=sha256:b592cd60907988c30186d6a1ab157ac5692d2fc505d4e7f872c56acf69835149 \
+    --hash=sha256:b85a44c87df33eed672d062d43eb9f01c7162a755cee5bce11c995c4fceba2ee \
+    --hash=sha256:bbc66d47ac0ccfc73f99980533502077a95c3252c1a8fa4da446ad597ddb2ba7 \
+    --hash=sha256:befc454b74ef9584e4c06471a6caaf20ef2b43659e152b50f5c3d61832073f50 \
+    --hash=sha256:bf31d4e8f8dc964d7a314a26b5d7f5cda245f9acab0145fd4fb19b7605803e94 \
+    --hash=sha256:ce0e9058f3819cd0b7db8191941dd19ae82dc1b97dc0617e9df25984d00ee61c \
+    --hash=sha256:ce7c1e3a45ce6d64ec3ed06ec6c0e288711482f1990115c9b4cbe4da2626a424 \
+    --hash=sha256:cfd71226e277e4f54bec6b27652c04c5498aa9a913cddaf32d17126ce058ac90 \
+    --hash=sha256:d1dcb218893c207ea8faf8729f4f3a3c5d1641c5a9f11134ededc8a06daf647a \
+    --hash=sha256:d2dc85ccb5e224f0c5be165d70a1d04a3a754afb53fffddc4c410509fabae430 \
+    --hash=sha256:d63dfd83282891c91f1dce85ce211cccb5c06573830a60f8d1a747164975ed4b \
+    --hash=sha256:db7777f7ae23175aaef0778d718d5d6f5005bc8979fc3b9b494455a0556cc050 \
+    --hash=sha256:dc1ab4740247b7601ad44a992a9571389bc5e5e4a8807fa23485767c3fd5a08d \
+    --hash=sha256:deaa7d41f95e085e4962d5d65f97a13e47c51c631f7e4c080c332c5c5c0da786 \
+    --hash=sha256:e0ade636fb77c4e4156edd584292d2b1d2033fe544da8288590561257c99bd03 \
+    --hash=sha256:e1e7515eca2f4dfc48385edb61964c96bfb7b8efc2e6a2421da3ac07e29d82cd \
+    --hash=sha256:e25fc1e5df892b800bb1cf5d9e5f7005620976f02ecde90859decea1aa85a1e9 \
+    --hash=sha256:e4e2bfa6ce7916776afd3db02006c56d90a7362ed72774afd9071ffe03cd8188 \
+    --hash=sha256:f50e34ebdf4ad7c96d89cfb05418e11ed23d3ac46f1f59f3d2e1d8da8091a0eb \
+    --hash=sha256:ffe69b75459d90529f603d9594255c41d6a503f69220740510373374198735f6
 standard-aifc==3.13.0 \
     --hash=sha256:64e249c7cb4b3daf2fdba4e95721f811bde8bdfc43ad9f936589b7bb2fae2e43 \
     --hash=sha256:f7ae09cc57de1224a0dd8e3eb8f73830be7c3d0bc485de4c1f82b4a7f645ac66
@@ -2875,9 +2881,9 @@ standard-telnetlib==3.13.0 \
 text-unidecode==1.3 \
     --hash=sha256:1311f10e8b895935241623731c2ba64f4c455287888b18189350b67134a822e8 \
     --hash=sha256:bad6603bb14d279193107714b288be206cac565dfa49aa5b105294dd5c4aab93
-threadpoolctl==3.7.0 \
-    --hash=sha256:61348cfb77d53b9242e0017029244b559b810c142ced65b4e21eeca1843959a7 \
-    --hash=sha256:cd8b60b5641b45c67bbf73c64c843235fc2d8a480c87389f52f5dbee893b86be
+threadpoolctl==3.8.0 \
+    --hash=sha256:01080674ad7ac6182429c918a79de92da789bb448acc02fc0b620b1abd6b6137 \
+    --hash=sha256:f1b49c82704d50f13ffae019c727b0fa4f6791a58f48f06a09c45face1be66da
 typing-extensions==4.16.0 \
     --hash=sha256:481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8 \
     --hash=sha256:dc983d19a509c94dba722ee6abd33940f7c05a89e243c47e907eb4db6f1a43e5
@@ -2941,26 +2947,26 @@ urllib3==2.8.0 \
 usb-devices==0.5.1 \
     --hash=sha256:8ef45c401490391a3651b3ba748eb213a654ac165be10a0786ab963668c49cc3 \
     --hash=sha256:e77e7972b5ac6a883b3778b0273d9582c5b8ae847ac78fba3d080dd4a4cc69ad
-uv==0.13.6 \
-    --hash=sha256:1cd4b0a35fa599b83da5437748150319ae0917c522da60898327645382942faa \
-    --hash=sha256:22759b8895e1103578de6fb4cd27e94b4399d021023378d29f01333717751fba \
-    --hash=sha256:29135609166960c74539abdaf4264f9819a0381be18b224125418356d67dd208 \
-    --hash=sha256:2e9a99100abe4f99605366974c4f9fe27f236615e05de8e78c0f357e38f09f97 \
-    --hash=sha256:46c2ef1f744f20007be0cdd66db3022bb1ddcac477c754efda875e401a48d810 \
-    --hash=sha256:4d20de8a3ed6c3d39b4e2f8f7d0411cd13a3959f5191b2b5d0209344034ed056 \
-    --hash=sha256:51361029b7cf91185d0092c4b356d110b4ad629e9cb11593f1e006ac72a72ca9 \
-    --hash=sha256:710c68ea4853aaf70ab2d0ccf2e147dee59449f035a1f8fe7759f087a31cdbf5 \
-    --hash=sha256:722c7f96803f115e53918b8ee8858d1680ea6077c614b6db750747d709ab8d9a \
-    --hash=sha256:7c9bc35ccb65932d8dc10a0669f9c805eaa3c9827ce18ecbecb1bd67944b2cdf \
-    --hash=sha256:7ec5486476d67a4214c460b5492393ee2300d84e1de17b293100a019b413568b \
-    --hash=sha256:8542dcf118ce8a7cf2e4ba1fea7f5cc1638bc02b5b30dab1ead7e9034dc62fd3 \
-    --hash=sha256:95f042b95e67ef8c3d3569bb6e9d895e592002c5e871cf3f1afe407c9d77a294 \
-    --hash=sha256:b2d25a49d135a441f688a6869d6d8062fb6f0a2e3e32e18b72c9de1d0eb9521e \
-    --hash=sha256:b9f57153fc98b7aa41dd6720e3de7578747f60b7bff22f50b76dcc47205bdde3 \
-    --hash=sha256:d1efed1d15102ffdbf5e0fd49a440643dda2d921a2ad856792ae42ccd43c253f \
-    --hash=sha256:d4d7026c7327dd11fc2c0d4bae4735ff6944293d370644f35d2e6e917cdcae04 \
-    --hash=sha256:d762215478854f6cf20c3faed8f1eb30c8101d568e7bc32a3abafc063929d5c5 \
-    --hash=sha256:feb0f1d555798f68f28719cab437ab1dfb5d918db86ab4554215cbf9d940f63b
+uv==0.13.7 \
+    --hash=sha256:08f16fd463926786b702b497473511deae4b3e17a2fa6d22180950d6059a120d \
+    --hash=sha256:158953b8669bee6f4bc2babdd997e34ff9f0d57170093cfe907f64448292b7c3 \
+    --hash=sha256:1bc8543d930464bbb22ac01bb1a660a448235e558014914de1e1cd5b993361b8 \
+    --hash=sha256:2835e2ab397d0db86323b9975dce75ecd76aa9cfa0d6a2aea84734aae7f8c9b3 \
+    --hash=sha256:2c9bdc4a872b60a93c5f26c0791089ea11585a4f9d3b3c017d78eb8487505e25 \
+    --hash=sha256:55e741a380a98008fc4985cf069855f36bc50242ef438e21a466786f5bc84da8 \
+    --hash=sha256:57ff66891d9a738ec087c23fdde842ac8e5eb63189ffed6ee95caee1b82ceb54 \
+    --hash=sha256:5e766791cb825d7a07e2ef9e622d307b48754fb682a31ba7bc5f272fab9ea395 \
+    --hash=sha256:5f37cc4d4660e4aee8a24d0dc179a0b0ce99506259c6796d37fa69bca9543a03 \
+    --hash=sha256:89df450624dec8c48b8b5a7adb654928cc50e95753f869c70cd65ef8333f2197 \
+    --hash=sha256:8b8ac028ae4ebb2a3f9d04907c61794f2cf8d7a7002bfbb4019a3dee28351fb2 \
+    --hash=sha256:8fc6019740794df995085f7b278d99dc11ccacffad9c63957278d3a6e272280b \
+    --hash=sha256:917733990ebc178318af0321d6873823ed5da707e1c4b1e5060ac2065a81f1f3 \
+    --hash=sha256:94f65a8ac5826dff76a93cb3cafbaad15def1788c63da2ce5ce09e0bd1303e7a \
+    --hash=sha256:952dcae9b1a7742f2fab28e82391fbfabe8807e4e9363f674b0f6be1053b8dd4 \
+    --hash=sha256:a90f5d95716ab83091f0f73a8e7ec64e557abf2a28537fcd719b2ac88e6f725a \
+    --hash=sha256:d30cafb7070901ba35353ec64cf228ae46caf79ac0f6fae329f95468b1482531 \
+    --hash=sha256:f91a229093163eefca89ea1b220a221d64c3beade05d03519a6584d1797a5a5f \
+    --hash=sha256:fd04bf01ba5f2829f4f94ca8f0c24a743f21e73d75045613ed6fc2fd66fc7bda
 voluptuous==0.16.0 \
     --hash=sha256:006535e22fed944aec17bef6e8725472476194743c87bd233e912eb463f8ff05 \
     --hash=sha256:ee342095263e1b5afbd4d418cb5adc92810eebfd07696bb033a261210df33db4

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
