!create ss : SignalState
!set ss.currentState := 'r'
!create sa : SafetyAgent
!create mn : MasNode
!create pa : PlanningAgent
!set mn.planningAgent := pa
!set mn.safetyAgent := sa
!set sa.signalState := ss
!insert (mn,pa) into masNodeContainsPlanningAgent
!insert (mn,sa) into masNodeContainsSafetyAgent
!insert (sa,ss) into safetyAgentContainsSignalState

!set ss.minimumGreenTime := 3
!set ss.minimumYellowTime := 2
!set ss.minimumRedTime := 1
!set ss.currentStateMinimumTime := 1
!set ss.ageOfCurrentState := 0
