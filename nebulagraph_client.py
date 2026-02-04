def check_process_legality(current_state, next_state, role):
    """
    Returns:
    {
        valid: bool
        approval_required: bool
        reason: str
    }
    """

    # TODO: replace with real NebulaGraph query
    return {
        "valid": True,
        "approval_required": False,
        "reason": "Valid HR workflow transition"
    }
