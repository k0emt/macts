__author__ = 'k0emt'


class SignalState:
    """
    object regarding the changing/handling of an individual light
    """
    GREEN = 'g'
    YELLOW = 'y'
    RED = 'r'
    PRIORITY_GREEN = 'G'

    VALID_STATES = [GREEN, YELLOW, RED, PRIORITY_GREEN]

    VALID_PROGRESSIONS = [GREEN + GREEN, GREEN + YELLOW,
                          GREEN + PRIORITY_GREEN, PRIORITY_GREEN + GREEN,
                          PRIORITY_GREEN + PRIORITY_GREEN,
                          PRIORITY_GREEN + YELLOW,
                          YELLOW + YELLOW, YELLOW + RED,
                          RED + RED,
                          RED + GREEN, RED + PRIORITY_GREEN
    ]

    current_state = RED
    current_state_minimum_time = 0
    current_state_age = 0

    STATUS_OK = "OK"
    STATUS_MIN_TIME = "Has not had Minimum Time in state"
    STATUS_INVALID_PROGRESSION = "Invalid Progression"
    STATUS_INVALID_STATE = "NOT A VALID STATE"

    change_status = ""

    minimum_times = {GREEN: 0, YELLOW: 0, RED: 0, PRIORITY_GREEN: 0}

    def __init__(self, minGreenTime, minPriorityGreen, minYellowTime,
                 minRedTime, initialState):
        self.minimum_times.update({SignalState.GREEN: minGreenTime})
        self.minimum_times.update(
                {SignalState.PRIORITY_GREEN: minPriorityGreen})
        self.minimum_times.update({SignalState.YELLOW: minYellowTime})
        self.minimum_times.update({SignalState.RED: minRedTime})

        if initialState in SignalState.VALID_STATES:
            self.current_state = initialState
            self.change_status = SignalState.STATUS_OK
        else:
            self.current_state = SignalState.RED
            self.change_status = SignalState.STATUS_INVALID_STATE

        self.current_state_age = 1

    def minimumTimeInStateMet(self):
        return self.current_state_age >= self.minimum_times.get(
            self.current_state)

    def validProgression(self, desired_state):
        return (self.current_state + desired_state) in\
               SignalState.VALID_PROGRESSIONS

    def changeStateTo(self, desired_state):
        if desired_state in self.VALID_STATES:
            if self.current_state == desired_state:
                self.change_status = SignalState.STATUS_OK
                self.current_state_age += 1
            else:
                if self.minimumTimeInStateMet():
                    if self.validProgression(desired_state):
                        self.current_state = desired_state
                        self.change_status = SignalState.STATUS_OK
                        self.current_state_age = 1
                    else:
                        self.change_status =\
                        SignalState.STATUS_INVALID_PROGRESSION
                        self.current_state_age += 1
                else:
                    self.change_status = SignalState.STATUS_MIN_TIME
                    self.current_state_age += 1
        else:
            self.change_status = SignalState.STATUS_INVALID_STATE
            self.current_state_age += 1


class SignalPhase:
    """
    object regarding the changing/handling of overall signal phase
    """
    STATUS_OK = "OK"
    STATUS_NO_CHANGE = "NO CHANGE"
    status_last_change_request = []

    current_phase = ""
    current_states = []
    current_phase_age = 0

    def __init__(self, initial_phase):
        self.status_last_change_request = []

        self.current_phase = ""
        self.current_states = []
        self.current_phase_age = 0

        for state in initial_phase:
            self.current_states.append(SignalState(3, 3, 2, 3, state))

        self.setPhase(initial_phase)

    def setPhase(self, desired_phase):
        new_phase = ""
        change_status = []

        for i, new_state in enumerate(desired_phase):
            self.current_states[i].changeStateTo(new_state)
            new_phase += self.current_states[i].current_state
            change_status.append(self.current_states[i].change_status)

        self.status_last_change_request = change_status

        if new_phase == desired_phase:
            if self.current_phase == desired_phase:
                self.current_phase_age += 1
            else:
                self.current_phase = desired_phase
                self.current_phase_age = 1
            return SignalPhase.STATUS_OK
        else:
            self.current_phase_age += 1
            return SignalPhase.STATUS_NO_CHANGE
