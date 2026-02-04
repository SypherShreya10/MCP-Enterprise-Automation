from typing import Optional, List, Dict, Any
from odoo_client import OdooClient
import logging
import re

logger = logging.getLogger(__name__)

client = OdooClient()


# tool 1 - get partner
def get_partner(
    *,
    partner_id: Optional[int] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    is_customer: Optional[bool] = None,
    is_supplier: Optional[bool] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Fetch partner (person or organization) records.

    Safety guarantees:
    - Read-only
    - Company-scoped (enforced by odoo_client)
    - Active records only
    - Bounded results (limit <= 100)
    """

    # ---------- Input validation ----------
    if not any([partner_id, name, email]):
        raise ValueError(
            "At least one search parameter must be provided: "
            "partner_id, name, or email."
        )

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    # ---------- Domain construction ----------
    domain = []

    if partner_id is not None:
        domain.append(("id", "=", partner_id))

    if email is not None:
        domain.append(("email", "=", email))

    if name is not None:
        domain.append(("name", "ilike", name))

    if is_customer is True:
        domain.append(("customer_rank", ">", 0))
    elif is_customer is False:
        domain.append(("customer_rank", "=", 0))

    if is_supplier is True:
        domain.append(("supplier_rank", ">", 0))
    elif is_supplier is False:
        domain.append(("supplier_rank", "=", 0))

    # Phase-2 mandatory constraint
    domain.append(("active", "=", True))

    # ---------- Allowed fields ----------
    fields = [
        "id",
        "name",
        "email",
        "phone",
        "street",
        "city",
        "country_id",
        "customer_rank",
        "supplier_rank",
        "credit_limit",
        "parent_id",
    ]

    logger.info("Tool get_partner invoked")

    try:
        records = client.search_read(
            model="res.partner",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        # Optional: derive booleans for clean output
        for r in records:
            r["is_customer"] = r.get("customer_rank", 0) > 0
            r["is_supplier"] = r.get("supplier_rank", 0) > 0

        return records

    except Exception as exc:
        logger.error("get_partner failed", exc_info=True)
        raise RuntimeError(
            "Failed to fetch partner data from Odoo"
        ) from exc


# tool 2 - create partner
def create_partner(
    *,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    is_customer: bool = False,
    is_supplier: bool = False,
    street: Optional[str] = None,
    city: Optional[str] = None,
    zip: Optional[str] = None,
    country_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create a new partner (contact / customer / supplier).

    Guarantees:
    - Create-only operation
    - Company-scoped automatically via odoo_client
    - Field allowlist enforced
    - Duplicate protection (within company scope)
    - Phase 1 & Phase 2 compliant
    """

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    if not name or not name.strip():
        raise ValueError("Partner name is required.")

    name = name.strip()

    if email:
        # Intentionally simple email sanity check (not RFC-exhaustive)
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("Invalid email format.")

    # ------------------------------------------------------------------
    # Uniqueness check
    # NOTE:
    # Company scoping is enforced inside odoo_client.search_read().
    # Do NOT re-apply company filters here.
    # ------------------------------------------------------------------

    existing = client.search_read(
        model="res.partner",
        domain=[
            ("name", "=", name),
            ("active", "=", True),
        ],
        fields=["id"],
        limit=1,
    )

    if existing:
        raise ValueError(
            f"A partner named '{name}' already exists in this company."
        )

    # ------------------------------------------------------------------
    # Prepare allowlisted create values
    # ------------------------------------------------------------------

    values: Dict[str, Any] = {
        "name": name,
    }

    if email:
        values["email"] = email
    if phone:
        values["phone"] = phone
    if street:
        values["street"] = street
    if city:
        values["city"] = city
    if zip:
        values["zip"] = zip
    if country_id:
        values["country_id"] = country_id

    # Partner role classification (via ranks, not booleans)
    if is_customer:
        values["customer_rank"] = 1
    if is_supplier:
        values["supplier_rank"] = 1

    logger.info(
        "Tool create_partner invoked",
        extra={
            "name": name,
            "is_customer": is_customer,
            "is_supplier": is_supplier,
        },
    )

    # ------------------------------------------------------------------
    # Create record (delegated to odoo_client)
    # ------------------------------------------------------------------

    try:
        partner_id = client.create(
            model="res.partner",
            values=values,
        )

        logger.info(
            "Partner created successfully",
            extra={
                "partner_id": partner_id,
                "name": name,
            },
        )

        return {
            "partner_id": partner_id,
            "message": f"Partner '{name}' created successfully.",
        }

    except Exception as exc:
        logger.error(
            "create_partner failed",
            extra={
                "name": name,
                "values": values,
            },
            exc_info=True,
        )
        raise RuntimeError(
            "Failed to create partner in Odoo."
        ) from exc
    

#section 3: tool 11 - get lead
def get_lead(
    *,
    lead_id: Optional[int] = None,
    partner_id: Optional[int] = None,
    stage_id: Optional[int] = None,
    user_id: Optional[int] = None,
    type: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Fetch CRM leads / opportunities.

    Safety guarantees:
    - Read-only
    - Company-scoped (enforced by OdooClient)
    - Active records only
    - Bounded results
    """

    # ---------------- Validation ----------------

    if not any([lead_id, partner_id, stage_id, user_id, type]):
        raise ValueError(
            "At least one search parameter must be provided."
        )

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    if type and type not in {"lead", "opportunity"}:
        raise ValueError("type must be 'lead' or 'opportunity'")

    # ---------------- Domain ----------------

    domain = [("active", "=", True)]

    if lead_id is not None:
        domain.append(("id", "=", lead_id))
    if partner_id is not None:
        domain.append(("partner_id", "=", partner_id))
    if stage_id is not None:
        domain.append(("stage_id", "=", stage_id))
    if user_id is not None:
        domain.append(("user_id", "=", user_id))
    if type is not None:
        domain.append(("type", "=", type))

    # ---------------- Fields ----------------

    fields = [
        "id",
        "name",
        "partner_id",
        "expected_revenue",
        "probability",
        "stage_id",
        "user_id",
        "date_deadline",
        "create_date",
        "type",
    ]

    logger.info("Tool get_lead invoked")

    # ---------------- Execution ----------------

    try:
        records = client.search_read(
            model="crm.lead",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        # Safe denormalization
        for r in records:
            r["partner_name"] = (
                r["partner_id"][1]
                if isinstance(r.get("partner_id"), (list, tuple))
                else None
            )
            r["stage_name"] = (
                r["stage_id"][1]
                if isinstance(r.get("stage_id"), (list, tuple))
                else None
            )

        return records

    except Exception as exc:
        logger.error(
            "get_lead failed",
            extra={"domain": domain},
            exc_info=True,
        )
        raise RuntimeError(
            "Failed to fetch CRM lead data from Odoo"
        ) from exc


# section 3: tool 12 - update lead stage
def update_lead_stage(
    *,
    lead_id: int,
    stage_id: int,
) -> Dict[str, Any]:
    """
    Update the stage of a CRM lead / opportunity.
    
    This is the ONLY update operation allowed in the entire MCP system.
    Moves a lead/opportunity through the sales pipeline.
    
    Args:
        lead_id: Lead ID to update (required, must be positive integer)
        stage_id: New stage ID (required, must be positive integer)
    
    Returns:
        Dictionary with:
        - lead_id: Updated lead ID
        - lead_name: Lead name
        - old_stage_id: Previous stage ID (or None)
        - new_stage_id: New stage ID
        - new_stage_name: New stage name
        - message: Confirmation message
    
    Raises:
        ValueError: If lead/stage doesn't exist or invalid parameters
        RuntimeError: If Odoo update operation fails
    
    Security Guarantees:
        - ONLY stage_id can be updated (enforced by OdooClient)
        - Lead must exist and be active
        - Stage must exist
        - Company scoping enforced automatically
        - All operations logged for audit
        - Write constraints enforced by OdooClient.write()
    
    Business Use Cases:
        - "Mark opportunity as won"
        - "Move lead to negotiation stage"
        - "Update pipeline stage based on customer action"
    
    Why This is the ONLY Update:
        This is the sole update operation allowed to minimize risk.
        All other updates require human intervention through Odoo UI.
    
    Compliance:
        - Phase 1 model semantics (crm.lead)
        - Phase 2 Business Object Map
        - AI Safety & Execution Constraints (HIGH RISK operation)
    """

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    if not isinstance(lead_id, int) or lead_id <= 0:
        raise ValueError(
            f"lead_id must be a positive integer, got: {lead_id} ({type(lead_id).__name__})"
        )
    
    if not isinstance(stage_id, int) or stage_id <= 0:
        raise ValueError(
            f"stage_id must be a positive integer, got: {stage_id} ({type(stage_id).__name__})"
        )

    # ------------------------------------------------------------------
    # Verify Lead Exists and is Active
    # ------------------------------------------------------------------

    lead = client.search_read(
        model="crm.lead",
        domain=[
            ("id", "=", lead_id),
            ("active", "=", True),
        ],
        fields=["id", "name", "stage_id", "team_id"],  # Include team for validation
        limit=1,
    )

    if not lead:
        raise ValueError(
            f"Active lead with id={lead_id} not found in current company. "
            f"Lead may not exist, be archived, or belong to different company."
        )

    lead_data = lead[0]
    old_stage_id = lead_data["stage_id"][0] if lead_data.get("stage_id") else None

    # ------------------------------------------------------------------
    # Verify Stage Exists (and optionally valid for team)
    # ------------------------------------------------------------------

    stage_domain = [("id", "=", stage_id)]
    
    # Optional: Enforce stage belongs to lead's team
    # Uncomment if your business rules require this:
    # if lead_data.get("team_id"):
    #     team_id = lead_data["team_id"][0]
    #     stage_domain.append(("team_id", "=", team_id))

    stage = client.search_read(
        model="crm.stage",
        domain=stage_domain,
        fields=["id", "name"],
        limit=1,
        apply_company_scope=False,
    )

    if not stage:
        raise ValueError(
            f"Stage with id={stage_id} does not exist or is not accessible."
        )

    stage_data = stage[0]

    # ------------------------------------------------------------------
    # Audit Logging (Before Update)
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: update_lead_stage (HIGH RISK OPERATION)",
        extra={
            "model": "crm.lead",
            "operation": "write",
            "lead_id": lead_id,
            "lead_name": lead_data["name"],
            "old_stage_id": old_stage_id,
            "new_stage_id": stage_id,
            "new_stage_name": stage_data["name"],
            "user_id": client.uid,
            "company_id": client.company_id,
        },
    )

    # ------------------------------------------------------------------
    # Perform Controlled Update
    # ------------------------------------------------------------------

    try:
        # OdooClient.write() enforces:
        # - model must be crm.lead
        # - values must contain ONLY stage_id
        client.write(
            model="crm.lead",
            record_id=lead_id,
            values={"stage_id": stage_id},
        )

        # Log success
        logger.info(
            f"Lead stage updated successfully: '{lead_data['name']}' (ID: {lead_id}) "
            f"moved to stage '{stage_data['name']}' (ID: {stage_id})",
            extra={
                "lead_id": lead_id,
                "old_stage_id": old_stage_id,
                "new_stage_id": stage_id,
                "success": True,
            },
        )

        # Return comprehensive result
        return {
            "lead_id": lead_id,
            "lead_name": lead_data["name"],
            "old_stage_id": old_stage_id,
            "new_stage_id": stage_id,
            "new_stage_name": stage_data["name"],
            "message": f"Lead '{lead_data['name']}' moved to stage '{stage_data['name']}'",
        }

    except Exception as exc:
        # Log failure with full context
        logger.error(
            f"update_lead_stage failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "lead_id": lead_id,
                "lead_name": lead_data["name"],
                "old_stage_id": old_stage_id,
                "new_stage_id": stage_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )
        
        raise RuntimeError(
            f"Failed to update lead {lead_id} ('{lead_data['name']}') "
            f"to stage {stage_id}: {str(exc)}"
        ) from exc
    

# section 3: tool 13 - get stage
def get_stage(
    *,
    stage_id: Optional[int] = None,
    name: Optional[str] = None,
    is_won: Optional[bool] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch CRM sales pipeline stages (crm.stage).

    Reference data for understanding pipeline structure.

    Note:
    crm.stage is typically shared reference data in Odoo and
    does NOT have a company_id field. Company scoping is
    intentionally disabled.
    """

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    domain = [("id", "!=", 0)]

    if stage_id is not None:
        domain.append(("id", "=", stage_id))

    if name is not None:
        domain.append(("name", "ilike", name))

    if is_won is not None:
        domain.append(("is_won", "=", is_won))

    fields = [
        "id",
        "name",
        "sequence",
        "is_won",
        "fold",
    ]

    logger.info("Tool get_stage invoked")

    try:
        return client.search_read(
            model="crm.stage",
            domain=domain,
            fields=fields,
            limit=limit,
            apply_company_scope=False,  # ✅ REQUIRED
        )

    except Exception as exc:
        logger.error("get_stage failed", exc_info=True)
        raise RuntimeError("Failed to fetch CRM stages") from exc


# section 3: tool 14 - get team
def get_team(
    *,
    team_id: Optional[int] = None,
    name: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch CRM sales team information (crm.team).

    Sales teams are company-specific.
    Company scoping MUST be enforced.
    """

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    domain = [("id", "!=", 0)]

    if team_id is not None:
        domain.append(("id", "=", team_id))

    if name is not None:
        domain.append(("name", "ilike", name))

    if user_id is not None:
        domain.append(("user_id", "=", user_id))

    fields = [
        "id",
        "name",
        "user_id",     # team leader
        "member_ids",  # team members
    ]

    logger.info("Tool get_team invoked")

    try:
        return client.search_read(
            model="crm.team",
            domain=domain,
            fields=fields,
            limit=limit,
            apply_company_scope=True,  # ✅ CRITICAL FIX
        )

    except Exception as exc:
        logger.error("get_team failed", exc_info=True)
        raise RuntimeError("Failed to fetch CRM teams") from exc
