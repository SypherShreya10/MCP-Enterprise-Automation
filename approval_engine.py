from weaviate_client import get_client
from weaviate.classes.query import Filter


def get_approval_requirement(domain, workflow, action, role):
    """
    Returns approval requirements if any exist.
    """

    client = get_client()
    collection = client.collections.get("ApprovalPolicy")

    filters = (
        Filter.by_property("domain").equal(domain)
        & Filter.by_property("workflow").equal(workflow)
        & Filter.by_property("action").equal(action)
        & Filter.by_property("requested_by_role").equal(role)
    )

    result = collection.query.fetch_objects(filters=filters)

    if not result.objects:
        return {
            "approval_required": False,
            "auto_approve": True,
        }

    policy = result.objects[0].properties

    return {
        "approval_required": True,
        "approver_roles": policy["approver_roles"],
        "approval_level": policy["approval_level"],
        "auto_approve": policy["auto_approve"],
        "escalation_role": policy["escalation_role"],
    }

    

