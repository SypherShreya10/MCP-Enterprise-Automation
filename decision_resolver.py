from nebulagraph_client import check_process_legality
from policy_engine import check_policy_constraints
from approval_engine import get_approval_requirement


def governance_decision(
    current_state,
    next_state,
    role,
    workflow
):
    # 1. Process legality (NebulaGraph)
    process = check_process_legality(current_state, next_state, role)

    if not process["valid"]:
        return {
            "verdict": "BLOCKED",
            "reason": process["reason"],
            "authority": "NebulaGraph"
        }

    # 2. Policy constraints (Weaviate - HRPolicy)
    policy = check_policy_constraints(workflow, role)

    if policy["severity"] == "BLOCK":
        return {
            "verdict": "BLOCKED",
            "reason": policy["policies"],
            "authority": "Weaviate"
        }

    # 3. Approval handling
    if policy["severity"] == "REQUIRE_APPROVAL" or process["approval_required"]:
        approval = get_approval_requirement(
            domain="HR",
            workflow=workflow,
            action=next_state,
            role=role
        )

        return {
            "verdict": "NEEDS_APPROVAL",
            "reason": policy["policies"],
            "approval": approval,
            "authority": "GovernanceLayer"
        }

    # 4. Fully allowed
    return {
        "verdict": "ALLOWED",
        "reason": "Process and policy compliant",
        "authority": "GovernanceLayer"
    }

