from weaviate_client import get_client
from weaviate.classes.query import Filter

def check_policy_constraints(workflow, role):
    """
    Returns:
    {
        severity: BLOCK | REQUIRE_APPROVAL | ALLOW
        policies: [policy_texts]
    }
    """

    client = get_client()
    collection = client.collections.get("HRPolicy")

    filters = (
        Filter.by_property("domain").equal("HR")
        & Filter.by_property("applies_to").equal(workflow)
        & Filter.by_property("roles").contains_any([role])
    )

    result = collection.query.fetch_objects(filters=filters)

    if not result.objects:
        return {"severity": "ALLOW", "policies": []}

    severities = set()
    policies = []

    for obj in result.objects:
        severities.add(obj.properties["severity"])
        policies.append(obj.properties["policy_text"])

    if "BLOCK" in severities:
        return {"severity": "BLOCK", "policies": policies}

    if "REQUIRE_APPROVAL" in severities:
        return {"severity": "REQUIRE_APPROVAL", "policies": policies}

    return {"severity": "ALLOW", "policies": policies}

