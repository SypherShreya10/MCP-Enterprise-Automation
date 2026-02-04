from decision_resolver import governance_decision
from weaviate_client import close_client

result = governance_decision(
    current_state="OfferMade",
    next_state="OfferAccepted",
    role="HR_EXECUTIVE",
    workflow="Hiring"
)

print(result)

close_client()

