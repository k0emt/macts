__author__ = 'k0emt'

import unittest

from TrafficLightSignal import SignalState
from TrafficLightSignal import SignalPhase


class SignalStateTests(unittest.TestCase):
    def setUp(self):
        self.signal_state = SignalState(1, 1, 2, 3, SignalState.RED)

    def testCanStartInAnyState(self):
        my_signal_state = SignalState(1, 1, 2, 3, SignalState.GREEN)
        self.assertEqual(SignalState.GREEN, my_signal_state.current_state)

    def testMinTimesSet(self):
        self.assertEqual(self.signal_state.minimum_times.
        get(SignalState.GREEN), 1)
        self.assertEqual(
            self.signal_state.minimum_times.get(SignalState.PRIORITY_GREEN), 1)
        self.assertEqual(self.signal_state.minimum_times.
        get(SignalState.YELLOW), 2)
        self.assertEqual(self.signal_state.minimum_times.get(SignalState.RED),
            3)

    def testOnInitRed(self):
        self.assertEqual(self.signal_state.current_state, SignalState.RED)

    def testValidStatesChange(self):
        # meet the minimum age requirement then change
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.GREEN)

        self.assertEqual(self.signal_state.current_state, SignalState.GREEN)
        self.assertEqual(self.signal_state.change_status,
            SignalState.STATUS_OK)

    def testInvalidStateDoesNotChange(self):
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo("blue")

        self.assertEqual(self.signal_state.current_state, SignalState.RED)
        self.assertEqual(self.signal_state.current_state_age, 3)
        self.assertEqual(self.signal_state.change_status,
            SignalState.STATUS_INVALID_STATE)

    def testTransitionMustBeLogical(self):
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.YELLOW)

        self.assertEqual(self.signal_state.current_state, SignalState.RED)
        self.assertEqual(self.signal_state.change_status,
            SignalState.STATUS_INVALID_PROGRESSION)

    def testNoStateChangeIfMinTimeNotYetMetForRed(self):
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.GREEN)

        self.assertEqual(self.signal_state.current_state, SignalState.RED)
        self.assertEqual(self.signal_state.change_status,
            SignalState.STATUS_MIN_TIME)

    def testMinTimeNotYetMetForRedIncrementAge(self):
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.GREEN)

        self.assertEqual(self.signal_state.current_state, SignalState.RED)
        self.assertEqual(self.signal_state.current_state_age, 3)

    def testCurrentStateAgeIsOneOnInit(self):
        self.assertEqual(self.signal_state.current_state_age, 1)

    def testCurrentStateAgeIsOneIfJustChanged(self):
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.RED)
        self.signal_state.changeStateTo(SignalState.GREEN)

        self.assertEqual(self.signal_state.current_state_age, 1)

    def testCurrentStateAgeIncrementsIfStateStaysTheSame(self):
        self.signal_state.changeStateTo(SignalState.RED)

        self.assertEqual(self.signal_state.current_state_age, 2)
        self.assertEqual(self.signal_state.change_status,
            SignalState.STATUS_OK)


class SignalPhaseTests(unittest.TestCase):
    INITIAL_PHASE = "rrGGGGGg"
    GOOD_NEXT_PHASE = "rryyyyyg"

    def setUp(self):
        self.signal_phase = SignalPhase(SignalPhaseTests.INITIAL_PHASE)

    def tearDown(self):
        self.signal_phase = None

    def testGetPhase(self):
        self.assertEqual(SignalPhaseTests.INITIAL_PHASE,
            self.signal_phase.current_phase)

    def testValidPhaseChange(self):
        result = self.signal_phase.setPhase(SignalPhaseTests.INITIAL_PHASE)
        self.assertEqual(2, self.signal_phase.current_phase_age)

        self.assertEqual(SignalPhaseTests.INITIAL_PHASE,
            self.signal_phase.current_phase)

        for status in self.signal_phase.status_last_change_request:
            self.assertEqual(SignalState.STATUS_OK, status)

        self.assertEqual(SignalPhase.STATUS_OK, result)

    def testValidDifferentPhaseChange(self):
        self.signal_phase.setPhase(SignalPhaseTests.INITIAL_PHASE)
        self.signal_phase.setPhase(SignalPhaseTests.INITIAL_PHASE)

        self.signal_phase.setPhase(SignalPhaseTests.GOOD_NEXT_PHASE)
        self.assertEqual(SignalPhaseTests.GOOD_NEXT_PHASE,
            self.signal_phase.current_phase)

        for status in self.signal_phase.status_last_change_request:
            self.assertEqual(SignalState.STATUS_OK, status)

        self.assertEqual(1, self.signal_phase.current_phase_age)

    def testBadTransitionLeavesPhaseUnchanged(self):
        self.signal_phase.setPhase(SignalPhaseTests.INITIAL_PHASE)
        self.signal_phase.setPhase(SignalPhaseTests.INITIAL_PHASE)

        self.assertEqual(SignalPhase.STATUS_NO_CHANGE,
            self.signal_phase.setPhase("ryGGGGGg"))
        self.assertEqual(SignalPhaseTests.INITIAL_PHASE,
            self.signal_phase.current_phase)

        self.assertEqual([SignalState.STATUS_OK,
                          SignalState.STATUS_INVALID_PROGRESSION,
                          SignalState.STATUS_OK, SignalState.STATUS_OK,
                          SignalState.STATUS_OK, SignalState.STATUS_OK,
                          SignalState.STATUS_OK, SignalState.STATUS_OK],
            self.signal_phase.status_last_change_request)

        self.assertEqual(4, self.signal_phase.current_phase_age)

    def testOfJunctionSsDefaultProgram(self):
        duration = [30, 2, 6, 2, 31, 2]
        phase = ["rrGGGGGg", "rryyyyyg", "rrrrrrrG", "rrrrrrry", "GGGrrrrr",
                 "yyyrrrrr"]

        myPhase = SignalPhase(phase[0])

        for outer, repeat in enumerate(duration):
            for inner in range(0, duration[outer]):
                myPhase.setPhase(phase[outer])

                for status in myPhase.status_last_change_request:
                    self.assertEqual(SignalState.STATUS_OK, status)

    def testOfJunctionRklnDefaultProgram(self):
        duration = [30, 2, 6, 2, 31, 2]
        phase = ["rrrGGGGGg", "rrryyyyyg", "rrrrrrrrG", "rrrrrrrry",
                 "GGGGrrrrr", "yyyyrrrrr"]

        myPhase = SignalPhase(phase[0])

        for outer, repeat in enumerate(duration):
            for inner in range(0, duration[outer]):
                myPhase.setPhase(phase[outer])

                for status in myPhase.status_last_change_request:
                    self.assertEqual(SignalState.STATUS_OK, status)

if __name__ == '__main__':
    unittest.main()
