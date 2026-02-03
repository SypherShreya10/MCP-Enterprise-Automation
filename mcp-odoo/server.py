from mcp.server.fastmcp import FastMCP

from tools.crm import (
    get_partner,
    create_partner,
    get_lead,
    update_lead_stage,
    get_stage,
    get_team,
)
from tools.common import (
    get_user,
    get_company, 
)

from tools.hr import (
    get_employee,
    get_department,
    get_job,
    get_employee_leaves,
    check_employee_availability,
    get_employee_attendance,
)

# ------------------------------------------------------------------------------
# Create MCP server
# ------------------------------------------------------------------------------

mcp = FastMCP(
    name="odoo-mcp-server",
)

# ------------------------------------------------------------------------------
# Tool: section 1: tool 1 - get_partner
# ------------------------------------------------------------------------------

@mcp.tool(
    name="get_partner",
    description=(
        "Fetch partner (person or organization) records from Odoo.\n\n"
        "Search by partner_id, name (partial), or email (exact).\n"
        "Optional filters: is_customer, is_supplier.\n"
        "Returns a list of matching partners with safe fields only."
    ),
)
def get_partner_tool(
    partner_id: int | None = None,
    name: str | None = None,
    email: str | None = None,
    is_customer: bool | None = None,
    is_supplier: bool | None = None,
    limit: int = 10,
):
    return get_partner(
        partner_id=partner_id,
        name=name,
        email=email,
        is_customer=is_customer,
        is_supplier=is_supplier,
        limit=limit,
    )

# ------------------------------------------------------------------------------
# Tool: section 1: tool 2 - create_partner
# ------------------------------------------------------------------------------

@mcp.tool(
    name="create_partner",
    description=(
        "Create a new partner (contact / customer / supplier) in Odoo.\n\n"
        "Required: name.\n"
        "Optional: email, phone, address fields.\n"
        "Flags: is_customer, is_supplier.\n"
        "Company is automatically set and cannot be overridden."
    ),
)
def create_partner_tool(
    name: str,
    email: str | None = None,
    phone: str | None = None,
    is_customer: bool = False,
    is_supplier: bool = False,
    street: str | None = None,
    city: str | None = None,
    zip: str | None = None,
    country_id: int | None = None,
):
    return create_partner(
        name=name,
        email=email,
        phone=phone,
        is_customer=is_customer,
        is_supplier=is_supplier,
        street=street,
        city=city,
        zip=zip,
        country_id=country_id,
    )

# ------------------------------------------------------------------------------
# Tool: section 1: tool 3 - get_user
# ------------------------------------------------------------------------------

@mcp.tool(
    name="get_user",
    description=(
        "Fetch internal system users from Odoo (read-only).\n\n"
        "Use for audit and workflow routing.\n"
        "Search by user_id, login (email), or name.\n"
        "Only active internal users are returned."
    ),
)
def get_user_tool(
    user_id: int | None = None,
    login: str | None = None,
    name: str | None = None,
    limit: int = 10,
):
    return get_user(
        user_id=user_id,
        login=login,
        name=name,
        limit=limit,
    )

# ------------------------------------------------------------------------------
# Tool: section 1: tool 4 - get_company
# ------------------------------------------------------------------------------

@mcp.tool(
    name="get_company",
    description=(
        "Fetch current company information from Odoo.\n\n"
        "Returns company name, currency, and contact details.\n"
        "Cross-company access is forbidden."
    ),
)
def get_company_tool(
    company_id: int | None = None,
):
    return get_company(company_id=company_id)

# ------------------------------------------------------------------------------
# Tool: section 2: tool 5 - get_employee (READ)
# ------------------------------------------------------------------------------

@mcp.tool(
    name="get_employee",
    description=(
        "Fetch employee information from Odoo (read-only).\n\n"
        "Search by employee_id, name, department, or job role.\n"
        "Only active employees from the current company are returned.\n"
        "Sensitive personal and payroll data is strictly excluded."
    ),
)
def get_employee_tool(
    employee_id: int | None = None,
    name: str | None = None,
    department_id: int | None = None,
    job_id: int | None = None,
    limit: int = 10,
):
    """
    MCP wrapper for get_employee.
    """
    return get_employee(
        employee_id=employee_id,
        name=name,
        department_id=department_id,
        job_id=job_id,
        limit=limit,
    )

# ------------------------------------------------------------------
# section 2: tool 6 - get_department
# ------------------------------------------------------------------

@mcp.tool(
    name="get_department",
    description=(
        "Fetch company department structure.\n\n"
        "Supports listing all departments or searching by name, "
        "manager, or department ID."
    ),
)
def get_department_tool(
    department_id: int | None = None,
    name: str | None = None,
    manager_id: int | None = None,
    limit: int = 100,
):
    return get_department(
        department_id=department_id,
        name=name,
        manager_id=manager_id,
        limit=limit,
    )


# ------------------------------------------------------------------
# section 2: tool 7 - get_job
# ------------------------------------------------------------------

@mcp.tool(
    name="get_job",
    description=(
        "Fetch job role definitions.\n\n"
        "Supports searching by job name, department, or job ID."
    ),
)
def get_job_tool(
    job_id: int | None = None,
    name: str | None = None,
    department_id: int | None = None,
    limit: int = 100,
):
    return get_job(
        job_id=job_id,
        name=name,
        department_id=department_id,
        limit=limit,
    )


# ------------------------------------------------------------------
# section 2: tool 8 - get_employee_leaves
# ------------------------------------------------------------------

@mcp.tool(
    name="get_employee_leaves",
    description=(
        "Fetch approved employee leaves for availability planning.\n\n"
        "Only approved (validated) leaves are returned."
    ),
)
def get_employee_leaves_tool(
    employee_id: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 100,
):
    return get_employee_leaves(
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )

#section 2: tool 9 - check employee availability
@mcp.tool(
    name="check_employee_availability",
    description=(
        "Check if a specific employee is available within a date range.\n\n"
        "This is a composite read-only tool that verifies:\n"
        "- Employee exists and is active\n"
        "- Approved leaves overlapping the date range\n\n"
        "Returns availability summary including conflicting leave dates."
    ),
)
def check_employee_availability_tool(
    employee_id: int,
    date_from: str,
    date_to: str,
):
    return check_employee_availability(
        employee_id=employee_id,
        date_from=date_from,
        date_to=date_to,
    )

#section 2: tool 10 - get_employee attendance
@mcp.tool(
    name="get_employee_attendance",
    description=(
        "Fetch employee attendance (clock-in / clock-out) records.\n\n"
        "Supports filtering by employee and/or date.\n"
        "Used for workforce visibility and attendance checks."
    ),
)
def get_employee_attendance_tool(
    employee_id: int | None = None,
    date_filter: str | None = None,
    limit: int = 100,
):
    return get_employee_attendance(
        employee_id=employee_id,
        date_filter=date_filter,
        limit=limit,
    )

# ------------------------------------------------------------------
# section 3: tool 11 - get_lead
# ------------------------------------------------------------------
@mcp.tool(
    name="get_lead",
    description=(
        "Fetch CRM leads or opportunities from Odoo (read-only).\n\n"
        "Supports filtering by lead_id, partner, stage, assigned user, "
        "or type ('lead' / 'opportunity').\n"
        "Only active, company-scoped records are returned."
    ),
)
def get_lead_tool(
    lead_id: int | None = None,
    partner_id: int | None = None,
    stage_id: int | None = None,
    user_id: int | None = None,
    type: str | None = None,
    limit: int = 10,
):
    return get_lead(
        lead_id=lead_id,
        partner_id=partner_id,
        stage_id=stage_id,
        user_id=user_id,
        type=type,
        limit=limit,
    )

# ------------------------------------------------------------------
# section 3: tool 12 - update_lead_stage (HIGH RISK)
# ------------------------------------------------------------------

@mcp.tool(
    name="update_lead_stage",
    description=(
        "Move a CRM lead or opportunity to a new pipeline stage.\n\n"
        "HIGH RISK: This is the ONLY update operation allowed.\n"
        "Updates stage_id only. Lead must exist and be active.\n"
        "Company scoping and write constraints are enforced automatically."
    ),
)
def update_lead_stage_tool(
    lead_id: int,
    stage_id: int,
):
    return update_lead_stage(
        lead_id=lead_id,
        stage_id=stage_id,
    )

# ------------------------------------------------------------------
# section 3: tool 13 - get_stage
# ------------------------------------------------------------------

@mcp.tool(
    name="get_stage",
    description=(
        "Fetch CRM sales pipeline stages.\n\n"
        "Use this to understand the pipeline structure, stage order, "
        "and identify won/lost stages.\n"
        "Read-only reference data."
    ),
)
def get_stage_tool(
    stage_id: int | None = None,
    name: str | None = None,
    is_won: bool | None = None,
    limit: int = 100,
):
    return get_stage(
        stage_id=stage_id,
        name=name,
        is_won=is_won,
        limit=limit,
    )

# ------------------------------------------------------------------
# section 3: tool 14 - get_team
# ------------------------------------------------------------------

@mcp.tool(
    name="get_team",
    description=(
        "Fetch CRM sales team information.\n\n"
        "Use this to understand sales team structure, team leaders, "
        "and members.\n"
        "Company-scoped, read-only reference data."
    ),
)
def get_team_tool(
    team_id: int | None = None,
    name: str | None = None,
    user_id: int | None = None,
    limit: int = 100,
):
    return get_team(
        team_id=team_id,
        name=name,
        user_id=user_id,
        limit=limit,
    )


# ------------------------------------------------------------------------------
# Server entry point
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
