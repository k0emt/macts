import SafetyAgent

__author__ = 'k0emt'


class SafetyAgentRoseKiln(SafetyAgent):
    """
    Safety Agent specifically built for the Rose Kiln Lane Junction with
    Pell and B Avenue.
    """

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

    # SR20 Submit verified safe plan to TLS command queue.
