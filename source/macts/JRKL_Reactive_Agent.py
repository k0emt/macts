__author__ = 'k0emt'

#'e1det_Pell~WB_0',
#'e1det_Pell~WB_1',
#'e1det_SteS~SB_0',
#'e1det_BAve~WB_1',
#'e1det_BAve~WB_0',
#'e1det_Best~EB_1',
#'e1det_Best~EB_0',
#'e1det_RKL~SB_1',
#'e1det_RKL~SB_0',
#'e1det_BAve~EB_1',
#'e1det_BAve~EB_0',

__author__ = 'k0emt'
import json

from PlanningAgent import BasePlanningAgent
from Core import MactsExchange
from Core import SensorState
from Core import Agent
from JRKL_SafetyAgent import SafetyAgentRoseKiln


class JRKL_ReactiveAgent(BasePlanningAgent):
    """
    Reactive Agent for Ste Saviors Junction
    """

    verbose_level = 1

    WINDOW_SIZE = 4

    P_EAST_WEST = "rrrGGGGGg"
    P_CLEARING_FOR_NB = "rrryyyyyg"
    P_PROTECTED_NB = "rrrrrrrrG"
    P_CLEARING_ALL = "rrrrrrrry"
    P_SB_WEST_TO_NORTH = "GGGGrrrrr"
    P_SLOWING = "yyyyrrrrr"

    # default program duration = [31, 2, 6, 2, 31, 2]
    # this program default duration = [15, 2, 2, 2, 15, 2]
    max_bump = {P_EAST_WEST: 20, P_CLEARING_FOR_NB: 2,
                P_PROTECTED_NB: 4, P_CLEARING_ALL: 0,
                P_SB_WEST_TO_NORTH: 20, P_SLOWING: 0}

    PROGRAM = (P_EAST_WEST, P_EAST_WEST, P_EAST_WEST, P_EAST_WEST, P_EAST_WEST,
               P_EAST_WEST, P_EAST_WEST, P_EAST_WEST, P_EAST_WEST, P_EAST_WEST,
               P_EAST_WEST, P_EAST_WEST, P_EAST_WEST, P_EAST_WEST, P_EAST_WEST,
               P_CLEARING_FOR_NB, P_CLEARING_FOR_NB,
               P_PROTECTED_NB, P_PROTECTED_NB,
               P_CLEARING_ALL, P_CLEARING_ALL,
               P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH,
               P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH,
               P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH,
               P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH,
               P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH, P_SB_WEST_TO_NORTH,
               P_SLOWING, P_SLOWING)

    program_pointer = 0
    program_length = len(PROGRAM) - 1
    bump_counter = {"phase": "", "count": 0}

    bump_map = {
        P_EAST_WEST: ['e1det_Pell~WB_0', 'e1det_Pell~WB_1',
                      'e1det_BAve~EB_1', 'e1det_BAve~EB_0'],
        P_CLEARING_FOR_NB: ['e1det_Pell~WB_0', 'e1det_Pell~WB_1'],
        P_PROTECTED_NB: ['e1det_Pell~WB_0', 'e1det_Pell~WB_1'],

        P_SB_WEST_TO_NORTH: ['e1det_RKL~SB_1', 'e1det_RKL~SB_0',
                             'e1det_Pell~WB_0', 'e1det_Pell~WB_1']
    }

    def should_bump(self, current_state, raw_sensor_data):
        # don't bump if the next state is the same as the current state
        next_index = ((self.program_pointer + JRKL_ReactiveAgent.WINDOW_SIZE) %
                      self.program_length)
        if current_state == self.PROGRAM[next_index]:
            return False

        if current_state in [self.P_CLEARING_ALL, self.P_SLOWING]:
            return False

        impacting_sensors = self.bump_map.get(current_state)
        for sensor in impacting_sensors:
            if raw_sensor_data.get(sensor) == 1:
                return True

        return False

    def sensor_consumer(self, channel, method, header, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)

        sensor_info = json.loads(body)
        self.verbose_display("SC: %s", sensor_info, 1)

        # SR 15 Examine incoming data and creates a TLS plan.
        # SR 17 is not applicable to this agent ?

        self.simulationId = sensor_info.get(Agent.SIMULATION_ID_KEY)
        self.simulationStep = sensor_info.get(Agent.SIMULATION_STEP_KEY)

        current_phase = self.PROGRAM[self.program_pointer]

        if self.should_bump(current_phase, sensor_info):
            if self.bump_counter.get("phase") == current_phase:
                max_count = self.max_bump.get(current_phase)
                if self.bump_counter.get("count") < max_count:
                    self.bump_counter.update(
                            {"phase": current_phase, "count": max_count + 1})
                    # do the bump/ don't increment
                    self.verbose_display("Doing %s", "the bump!", 1)
                else:
                    self.program_pointer = (
                        (self.program_pointer + 1) % self.program_length)
            else:
                self.bump_counter.update({"phase": current_phase, "count": 1})
                self.verbose_display("BUMP! %s", "new phase", 1)
                # do the bump/ don't increment
        else:
            self.program_pointer = (
                (self.program_pointer + 1) % self.program_length)

        desired_phase = self.PROGRAM[self.program_pointer]

        # SR 16 The planning agent submits the plan to the Safety Agent
        self.safety_agent.simulationStep = self.simulationStep
        self.safety_agent.simulationId = self.simulationId
        self.safety_agent.checkSafePlan(desired_phase)

    def __init__(self):
        BasePlanningAgent.__init__(self)
        self.agent_name = "JRKL_ReactiveAgent"
        print self.agent_name + " Agent ONLINE"

        self.Connect_RabbitMQ()

        self.establish_connection("commands",
            self.command_consumer, MactsExchange.COMMAND_DISCOVERY)

        self.establish_connection("sensor",
            self.sensor_consumer,
            MactsExchange.SENSOR_PREFIX + SensorState.RKL_JUNCTION
        )

        self.safety_agent = SafetyAgentRoseKiln(
            self.PROGRAM[self.program_pointer]
        )

        self.start_consuming()

        print self.agent_name + " Agent OFFLINE"

if __name__ == "__main__":
    JRKL_ReactiveAgent()
