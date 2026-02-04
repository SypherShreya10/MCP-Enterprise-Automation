from weaviate_client import get_client

client = get_client()
collection = client.collections.get("ApprovalPolicy")

collection.data.insert({
    "domain": "HR",
    "workflow": "Hiring",
    "action": "OfferAccepted",
    "requested_by_role": "HR_EXECUTIVE",
    "approver_roles": ["HR_MANAGER"],
    "approval_level": 1,
    "auto_approve": False,
    "escalation_role": "HR_DIRECTOR",
    "source": "HR Approval SOP v1.0"
})

print("Approval rule inserted")

client.close()
