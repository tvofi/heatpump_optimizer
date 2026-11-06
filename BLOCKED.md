body_push for r10-train-merge-loop-2 is refused at head 66d34a57e355 by review_packet: `hot-file: #3256 holds an unboarded merge verdict and shares tools/audit/seat/pr_args.sh`.
Carry 16's self-test arms live in pr_args.sh (the brief names them there), so the overlap cannot be removed. All other packet refusals (carry naming) are answered; prepr.sh rc=0 at this head; origin/main unmoved (198b8f7ed).
Code is at handoff/r10-train-merge-loop-2 (66d34a57e). Body is kept at handoff-wip/r10-train-merge-loop-2-body.
Question for the orchestrator: board #3256's verdict (or merge it), then rerun `bash tools/audit/seat/body_push.sh r10-train-merge-loop-2 <body>` after merging origin/main and rerunning prepr.sh.
