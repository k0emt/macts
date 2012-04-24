from SafetyAgent import SafetyAgent
from TrafficLightSignal import SignalPhase

__author__ = 'k0emt'

# NOTE increment Communications Agent EXPECTED_NUMBER_SAFETY_AGENT_COMMANDS


class SafetyAgentStSaviours(SafetyAgent):
    """
    Safety Agent specifically built for the St Saviours Junction with
    B Avenue and B West Avenue.
    """

    verbose_level = 0

    # TODO
    # SR18a The safety agent examines the TLS plan to verify that there are no
    # simultaneously active paths that will cross each other in such a way as
    # to create an unsafe condition.

    # SR18b The safety agent enforces minimum times per light color.
    # Example: a light cannot be green for 1 second then switched to yellow.

    # SR18c The safety agent enforces proper progression of light changes.
    # That is a light cannot be switched from green to red.
    # The progression must be a rotation of: green, yellow, red.

    # SR19 If the plan is not safe,
    # it lets the planning agent know and provides the reason why.

    def checkSafePlan(self, plan):
        self.phase_manager.setPhase(plan)

        self.verbose_display("SA %s %s %d",
            (self.agent_name, self.simulationId, self.simulationStep), 1)

        # SR20 Submit verified safe plan to TLS command queue.
        self.sendTrafficLightSignalCommand(self.phase_manager.current_phase)

    def __init__(self, initial_phase):
        self.junction = "JunctionSS"
        self.agent_name = "SafetyAgentStSaviours"

        self.Connect_RabbitMQ()
        self.phase_manager = SignalPhase(initial_phase)
        if self.phase_manager.status_last_change_request ==\
           SignalPhase.STATUS_OK:
            self.sendTrafficLightSignalCommand(
                self.phase_manager.current_phase)
