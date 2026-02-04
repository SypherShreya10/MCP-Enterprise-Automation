from decision_resolver import governance_decision

def governance_node(state):
    """
    Input state example:
    {
        current_state: "OfferMade",
        next_state: "OfferAccepted",
        role: "HR_EXECUTIVE",
        workflow: "Hiring"
    }
    """

    decision = governance_decision(
        current_state=state["current_state"],
        next_state=state["next_state"],
        role=state["role"],
        workflow=state["workflow"]
    )

    state["governance_verdict"] = decision
    return state
