__author__ = 'k0emt'

import unittest

from TrafficLightSignal import SignalState
from TrafficLightSignal import SignalPhase


class SignalStateTests(unittest.TestCase):
    def setUp(self):
        self.signal_state = SignalState(1, 1, 2, 3, SignalState.RED)

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
    def setUp(self):
        self.signal_phase = SignalPhase()

#    def testGetItem(self):
#        self.assertEqual(self.a_typedlist[1], 2)

if __name__ == '__main__':
    unittest.main()
