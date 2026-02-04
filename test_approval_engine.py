from approval_engine import get_approval_requirement
from weaviate_client import close_client

print("=== START TEST ===")

result = get_approval_requirement(
    domain="HR",
    workflow="Hiring",
    action="OfferAccepted",
    role="HR_EXECUTIVE"
)

print("RESULT:", result)

print("=== END TEST ===")

close_client()

