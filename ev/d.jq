($a[0].groups|map({key:.group,value:.})|from_entries) as $A | (.groups|map({key:.group,value:.})|from_entries) as $B |
{new: ([$B|keys[]]-[$A|keys[]]), removed: ([$A|keys[]]-[$B|keys[]]),
 stage: [$B|to_entries[]|select($A[.key]!=null and $A[.key].resume.stage!=.value.resume.stage)|"\(.key): \($A[.key].resume.stage)->\(.value.resume.stage)"],
 carry: [$B|to_entries[]|select($A[.key]!=null and (($A[.key].carry//[])!=(.value.carry//[])))|"\(.key): \($A[.key].carry|length)->\(.value.carry|length)"]}
