__author__ = 'k0emt'
from Core import Agent
from Core import MactsExchange


class SafetyAgent(Agent):
    """
    This will be an abstract class encapsulating common behavior and logic
    """
    junction = "junction_TBD"

    def checkSafePlan(self, plan):
        pass

    # SR18a The safety agent examines the TLS plan to verify that there are no
    # simultaneously active paths that will cross each other in such a way as
    # to create an unsafe condition.  Foes.

    # SR18b The safety agent enforces minimum times per light color.
    # Example: a light cannot be green for 1 second then switched to yellow.

    # SR18c The safety agent enforces proper progression of light changes.
    # That is a light cannot be switched from green to red.
    # The progression must be a rotation of: green, yellow, red.

    # SR19 If the plan is not safe,
    # it lets the planning agent know and provides the reason why.

    # SR20 Submit verified safe plan to TLS command queue.
    def sendTrafficLightSignalCommand(self, plan):
        decorated_command = {Agent.SIMULATION_ID_KEY: self.simulationId,
                             Agent.SIMULATION_STEP_KEY: self.simulationStep,
                             Agent.AUTHORITY_KEY: self.agent_name,
                             Agent.COMMAND_KEY: Agent.COMMAND_PLAN,
                             Agent.PLAN_KEY: plan,
                             Agent.PLAN_JUNCTION_KEY: self.junction
        }

        self.sendMessage(decorated_command, MactsExchange.COMMAND_RESPONSE,
            self.publishChannel)

#   pulled from the double_t.net.xml file
#    <tlLogic id="JunctionRKLN" type="static" programID="0" offset="0">
#    <phase duration="31" state="rrrGGGGGg"/>
#    <phase duration="2"  state="rrryyyyyg"/>
#    <phase duration="6"  state="rrrrrrrrG"/>
#    <phase duration="2"  state="rrrrrrrry"/>
#    <phase duration="31" state="GGGGrrrrr"/>
#    <phase duration="2"  state="yyyyrrrrr"/>
#    </tlLogic>
#    <tlLogic id="JunctionSS" type="static" programID="0" offset="0">
#    <phase duration="31" state="rrGGGGGg"/>
#    <phase duration="2" state="rryyyyyg"/>
#    <phase duration="6" state="rrrrrrrG"/>
#    <phase duration="2" state="rrrrrrry"/>
#    <phase duration="31" state="GGGrrrrr"/>
#    <phase duration="2" state="yyyrrrrr"/>
#    </tlLogic>
#
#    <junction id="JunctionRKLN" type="traffic_light" x="166.00" y="0.00"
#       incLanes="RKL~SB_0 RKL~SB_1 Pell~WB_0 Pell~WB_1 BAve~EB_0 BAve~EB_1"
#       intLanes=":JunctionRKLN_0_0 :JunctionRKLN_1_0 :JunctionRKLN_9_0
#                 :JunctionRKLN_3_0 :JunctionRKLN_4_0 :JunctionRKLN_5_0
#                 :JunctionRKLN_6_0 :JunctionRKLN_7_0 :JunctionRKLN_10_0"
#       shape="159.45,8.05 172.55,8.05 174.05,6.55 174.05,-6.55 157.95,
#               -6.55 157.95,6.55">
#    <request index="0" response="000000000" foes="000110000" cont="0"/>
#    <request index="1" response="000000000" foes="000110000" cont="0"/>
#    <request index="2" response="000110000" foes="111110000" cont="1"/>
#    <request index="3" response="000000000" foes="100000000" cont="0"/>
#    <request index="4" response="000000011" foes="100000111" cont="0"/>
#    <request index="5" response="000000011" foes="100000111" cont="0"/>
#    <request index="6" response="000000100" foes="000000100" cont="0"/>
#    <request index="7" response="000000100" foes="000000100" cont="0"/>
#    <request index="8" response="000111100" foes="000111100" cont="1"/>
#    </junction>
#    <junction id="JunctionSS" type="traffic_light" x="100.00" y="0.00"
#       incLanes="SteS~SB_0 BAve~WB_0 BAve~WB_1 Best~EB_0 Best~EB_1"
#       intLanes=":JunctionSS_0_0 :JunctionSS_8_0 :JunctionSS_2_0
#                 :JunctionSS_3_0 :JunctionSS_4_0 :JunctionSS_5_0
#                 :JunctionSS_6_0 :JunctionSS_9_0"
#       shape="96.75,8.05 103.25,8.05 104.75,6.55 104.75,-6.55 95.25,
#               -6.55 95.25,6.55">
#    <request index="0" response="00011000" foes="00011000" cont="0"/>
#    <request index="1" response="11111000" foes="11111000" cont="1"/>
#    <request index="2" response="00000000" foes="10000000" cont="0"/>
#    <request index="3" response="00000000" foes="10000011" cont="0"/>
#    <request index="4" response="00000000" foes="10000011" cont="0"/>
#    <request index="5" response="00000000" foes="00000010" cont="0"/>
#    <request index="6" response="00000000" foes="00000010" cont="0"/>
#    <request index="7" response="00011100" foes="00011110" cont="1"/>
#    </junction>
