from typing import Optional, List, Dict, Any
import logging
from odoo_client import OdooClient

logger = logging.getLogger(__name__)
client = OdooClient()


# section 1: tool 3 - get users
def get_user(
    *,
    user_id: Optional[int] = None,
    login: Optional[str] = None,
    name: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Fetch internal system users (res.users) for audit and workflow routing.

    Search by user_id (exact), login/email (exact), or name (partial match).

    Args:
        user_id: Specific user ID for exact lookup
        login: User login/email (exact match)
        name: User name (partial match, case-insensitive)
        limit: Maximum records to return (default=10, max=100)

    Returns:
        List of user dictionaries with allowed fields.
        Empty list if no matches found.

    Raises:
        ValueError: If invalid parameters provided
        RuntimeError: If Odoo operation fails

    Safety Guarantees:
        - Read-only operation
        - Internal users only (share=False, no portal users)
        - Active users only
        - Company-scoped (users with access to current company)
        - No sensitive fields returned (no passwords, API keys, security groups)
        - Field-level access enforced per ai_safety_execution_notes.md
        - All operations logged for audit trail

    Business Use Cases:
        - "Who is the sales manager?"
        - "Find user by email"
        - "Get users in current company for task assignment"

    Compliance:
        - Phase 1 model semantics (res.users)
        - Phase 2 Business Object Map
        - AI Safety & Execution Constraints
    """

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    if not any([user_id, login, name]):
        raise ValueError(
            "At least one search parameter is required: user_id, login, or name."
        )

    if limit < 1 or limit > 100:
        raise ValueError(
            f"Limit must be between 1 and 100, got: {limit}"
        )

    # ------------------------------------------------------------------
    # Domain Construction (with ALL safety constraints)
    # ------------------------------------------------------------------

    domain = [
        ("active", "=", True),  # Active users only
        ("share", "=", False),  # Internal users only (no portal/public users)
        ("company_ids", "in", [client.company_id]),  # ✅ CRITICAL: Company scope
    ]

    # Search parameters
    if user_id:
        domain.append(("id", "=", user_id))

    if login:
        domain.append(("login", "=", login))

    if name:
        domain.append(("name", "ilike", name))

    # ------------------------------------------------------------------
    # Allowed Fields Only (NO security/auth fields)
    # ------------------------------------------------------------------

    fields = [
        "id",
        "name",
        "login",
        "partner_id",  # Link to res.partner for contact info
        "company_id",  # User's main company
        "company_ids",  # All companies user has access to
        "active",
    ]

    # Forbidden fields (documented for clarity, not returned):
    # - password, password_crypt
    # - api_key, totp_secret
    # - groups_id (security groups)
    # - sel_groups_* (group selection fields)

    # ------------------------------------------------------------------
    # Log Operation (Audit Trail)
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: get_user",
        extra={
            "model": "res.users",
            "operation": "search_read",
            "domain": domain,
            "fields": fields,
            "limit": limit,
            "user_id": client.uid,  # Who made this request
            "company_id": client.company_id,  # Company context
            "search_params": {
                "user_id": user_id,
                "login": login,
                "name": name,
            },
        },
    )

    # ------------------------------------------------------------------
    # Execute Safe Read with Error Handling
    # ------------------------------------------------------------------

    try:
        records = client.search_read(
            model="res.users",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        # Log success
        logger.info(
            f"get_user completed successfully: {len(records)} record(s) found",
            extra={
                "record_count": len(records),
                "search_params": {
                    "user_id": user_id,
                    "login": login,
                    "name": name,
                },
            },
        )

        return records

    except Exception as exc:
        # Log failure with full context
        logger.error(
            f"get_user failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "domain": domain,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "search_params": {
                    "user_id": user_id,
                    "login": login,
                    "name": name,
                },
            },
            exc_info=True,
        )

        # Re-raise with context
        raise RuntimeError(
            f"Failed to fetch user information from Odoo: {str(exc)}"
        ) from exc
    

# section 1: tool 4 - get company
def get_company(
    *,
    company_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fetch company (res.company) information.

    If company_id is not provided, returns the current user's company.
    Cross-company access is explicitly forbidden for security.

    Args:
        company_id: Specific company ID (optional, defaults to current company)

    Returns:
        Dictionary with company information (single record)

    Raises:
        ValueError: If cross-company access attempted or invalid company_id
        RuntimeError: If Odoo operation fails or company not found

    Safety Guarantees:
        - Read-only operation
        - Single-record access only (no bulk reads)
        - Cross-company access forbidden
        - Current company only (defaults to current if not specified)
        - Field-level allowlist enforced per ai_safety_execution_notes.md
        - All operations logged for audit trail

    Business Use Cases:
        - "What is our company currency?"
        - "Get company details for invoices/documents"
        - "What's our company contact information?"

    Compliance:
        - Phase 1 model semantics (res.company)
        - Phase 2 Business Object Map
        - AI Safety & Execution Constraints

    Example:
        >>> company = get_company()
        >>> print(f"Company: {company['name']}")
        >>> print(f"Currency: {company['currency_id'][1]}")
    """

    # ------------------------------------------------------------------
    # Resolve & Validate company_id
    # ------------------------------------------------------------------

    # Default to current company if not specified
    resolved_company_id = company_id if company_id is not None else client.company_id

    # CRITICAL: Prevent cross-company access (security requirement)
    if resolved_company_id != client.company_id:
        error_msg = (
            f"Cross-company access is forbidden. "
            f"Requested company_id={resolved_company_id}, "
            f"but current company_id={client.company_id}. "
            f"You may only access the current company."
        )
        logger.warning(
            "Cross-company access attempt blocked",
            extra={
                "requested_company_id": resolved_company_id,
                "current_company_id": client.company_id,
                "user_id": client.uid,
            },
        )
        raise ValueError(error_msg)

    # ------------------------------------------------------------------
    # Domain (STRICT: single company only)
    # ------------------------------------------------------------------

    domain = [
        ("id", "=", resolved_company_id),
    ]

    # ------------------------------------------------------------------
    # Allowed Fields Only (per Tool Spec)
    # ------------------------------------------------------------------

    fields = [
        "id",
        "name",
        "currency_id",  # Returns (id, name) tuple
        "email",
        "phone",
        "street",
        "city",
        "country_id",  # Returns (id, name) tuple
    ]

    # Forbidden fields (not returned, documented for reference):
    # - Internal configuration fields
    # - Accounting setup fields
    # - Security-related fields
    # - Technical metadata

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: get_company",
        extra={
            "model": "res.company",
            "operation": "search_read",
            "domain": domain,
            "fields": fields,
            "requested_company_id": company_id,
            "resolved_company_id": resolved_company_id,
            "user_id": client.uid,
            "company_id": client.company_id,
        },
    )

    # ------------------------------------------------------------------
    # Execute Safe Read with Error Handling
    # ------------------------------------------------------------------

    try:
        records: List[Dict[str, Any]] = client.search_read(
            model="res.company",
            domain=domain,
            fields=fields,
            limit=1,
            apply_company_scope=False,
        )

        # Company must exist
        if not records:
            raise RuntimeError(
                f"Company with id={resolved_company_id} not found. "
                f"This should not happen for current company."
            )

        company_data = records[0]

        # Log success
        logger.info(
            f"get_company completed successfully: {company_data.get('name')}",
            extra={
                "company_id": company_data["id"],
                "company_name": company_data.get("name"),
            },
        )

        return company_data

    except Exception as exc:
        # Log failure with full context
        logger.error(
            f"get_company failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "domain": domain,
                "requested_company_id": company_id,
                "resolved_company_id": resolved_company_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )

        # Re-raise with context
        raise RuntimeError(
            f"Failed to fetch company information from Odoo: {str(exc)}"
        ) from exc