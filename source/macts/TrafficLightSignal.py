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

        self.changeStateTo(initialState)

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
    object regarding the changing/handling of overal signal phase
    """
