import sys,os
sys.path.insert(0,os.path.join(sys.argv[1],'tests'))
import harness_headers as H
k='dev/audit/rounds/round4/D7/sysid_estimator_frontier.py'
H.CPU_LIMIT_OVERRIDES_S[k]=160
sys.exit(H.main())
