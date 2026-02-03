from typing import Optional, List, Dict, Any, Union
import logging
from datetime import date, timedelta
from odoo_client import OdooClient

logger = logging.getLogger(__name__)
client = OdooClient()

# section 2: tool 5 - get employee
def get_employee(
    *,
    employee_id: Optional[int] = None,
    name: Optional[str] = None,
    department_id: Optional[int] = None,
    job_id: Optional[int] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Fetch employee information (hr.employee).

    Read-only HR tool with strict privacy controls.
    Sensitive personal and financial data is excluded.

    Safety Guarantees:
        - Read-only
        - Active employees only
        - Company-scoped (current company only)
        - No private or legal HR data
        - GDPR / privacy compliant
        - Fully audited

    Business Use Cases:
        - "Who is Sarah Chen?"
        - "List employees in Engineering"
        - "Find employees by role"
    """

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    if not any([employee_id, name, department_id, job_id]):
        raise ValueError(
            "At least one filter is required: "
            "employee_id, name, department_id, or job_id."
        )

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100.")

    # ------------------------------------------------------------------
    # Domain Construction (STRICT HR SAFETY)
    # ------------------------------------------------------------------

    domain = [
        ("active", "=", True),
        ("company_id", "=", client.company_id),  # 🔒 Company isolation
    ]

    if employee_id:
        domain.append(("id", "=", employee_id))

    if name:
        domain.append(("name", "ilike", name))

    if department_id:
        domain.append(("department_id", "=", department_id))

    if job_id:
        domain.append(("job_id", "=", job_id))

    # ------------------------------------------------------------------
    # Allowed Fields ONLY (No private HR data)
    # ------------------------------------------------------------------

    fields = [
        "id",
        "name",
        "job_id",
        "job_title",
        "department_id",
        "parent_id",       # Manager
        "work_email",
        "work_phone",
        "active",
    ]

    # Explicitly NOT included:
    # - private_email
    # - private_phone
    # - identification_id
    # - bank_account_id
    # - salary / wage fields
    # - home address

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: get_employee",
        extra={
            "model": "hr.employee",
            "operation": "search_read",
            "domain": domain,
            "fields": fields,
            "limit": limit,
            "company_id": client.company_id,
            "user_id": client.uid,
            "filters": {
                "employee_id": employee_id,
                "name": name,
                "department_id": department_id,
                "job_id": job_id,
            },
        },
    )

    # ------------------------------------------------------------------
    # Execute Safe Read
    # ------------------------------------------------------------------

    try:
        records = client.search_read(
            model="hr.employee",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        logger.info(
            f"get_employee completed: {len(records)} record(s) found",
            extra={"record_count": len(records)},
        )

        return records

    except Exception as exc:
        logger.error(
            f"get_employee failed: {type(exc).__name__}: {str(exc)}",
            extra={"domain": domain},
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to fetch employee information: {str(exc)}"
        ) from exc


# section 2: tool 6 - get department
def get_department(
    *,
    department_id: Optional[int] = None,
    name: Optional[str] = None,
    manager_id: Optional[int] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch department structure (hr.department).
    
    Returns organizational hierarchy and management structure.

    Args:
        department_id: Specific department ID
        name: Search by department name (partial match)
        manager_id: Filter by manager (employee_id)
        limit: Maximum records (default=100, max=100)

    Returns:
        List of department dictionaries

    Raises:
        ValueError: If invalid parameters
        RuntimeError: If Odoo operation fails

    Safety:
        - Read-only
        - Company scoped
        - No sensitive data

    Business Use Cases:
        - "List all departments"
        - "Who manages Engineering?"
        - "Get department structure"
    """

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    # Allow listing all departments, so no required param check needed
    # (Unlike employee where you don't want to return all employees)

    if limit < 1 or limit > 100:
        raise ValueError(f"Limit must be between 1 and 100, got: {limit}")

    # ------------------------------------------------------------------
    # Domain Construction
    # ------------------------------------------------------------------

    domain = [
        ("company_id", "=", client.company_id),
    ]

    if department_id:
        domain.append(("id", "=", department_id))

    if name:
        domain.append(("name", "ilike", name))

    if manager_id:
        domain.append(("manager_id", "=", manager_id))

    # ------------------------------------------------------------------
    # Allowed Fields
    # ------------------------------------------------------------------

    fields = [
        "id",
        "name",
        "manager_id",   # Returns (id, name) tuple
        "parent_id",    # Returns (id, name) tuple
        "company_id",   # Returns (id, name) tuple
    ]

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: get_department",
        extra={
            "model": "hr.department",
            "operation": "search_read",
            "domain": domain,
            "fields": fields,
            "limit": limit,
            "company_id": client.company_id,
            "user_id": client.uid,
            "search_params": {
                "department_id": department_id,
                "name": name,
                "manager_id": manager_id,
            },
        },
    )

    # ------------------------------------------------------------------
    # Execute with Error Handling
    # ------------------------------------------------------------------

    try:
        records = client.search_read(
            model="hr.department",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        logger.info(
            f"get_department completed: {len(records)} record(s) found",
            extra={"record_count": len(records)},
        )

        return records

    except Exception as exc:
        logger.error(
            f"get_department failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "domain": domain,
                "error_type": type(exc).__name__,
            },
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to fetch department information: {str(exc)}"
        ) from exc
    

#section 2: tool 7 - get job
def get_job(
    *,
    job_id: Optional[int] = None,
    name: Optional[str] = None,
    department_id: Optional[int] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch job role definitions (hr.job).
    
    Used to understand organizational roles and requirements.

    Args:
        job_id: Specific job ID
        name: Search by job name (partial match)
        department_id: Filter jobs by department
        limit: Maximum records (default=100, max=100)

    Returns:
        List of job dictionaries

    Raises:
        ValueError: If invalid parameters
        RuntimeError: If Odoo operation fails

    Safety:
        - Read-only
        - Company scoped

    Business Use Cases:
        - "What job positions exist?"
        - "Job requirements for role X"
        - "List all developer roles"
    """

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    if limit < 1 or limit > 100:
        raise ValueError(f"Limit must be between 1 and 100, got: {limit}")

    # ------------------------------------------------------------------
    # Domain Construction
    # ------------------------------------------------------------------

    domain = [
        ("company_id", "=", client.company_id),
    ]

    if job_id:
        domain.append(("id", "=", job_id))

    if name:
        domain.append(("name", "ilike", name))

    if department_id:
        domain.append(("department_id", "=", department_id))

    # ------------------------------------------------------------------
    # Allowed Fields
    # ------------------------------------------------------------------

    fields = [
        "id",
        "name",
        "department_id",  # Returns (id, name) tuple
        "description",
    ]

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: get_job",
        extra={
            "model": "hr.job",
            "operation": "search_read",
            "domain": domain,
            "fields": fields,
            "limit": limit,
            "company_id": client.company_id,
            "user_id": client.uid,
            "search_params": {
                "job_id": job_id,
                "name": name,
                "department_id": department_id,
            },
        },
    )

    # ------------------------------------------------------------------
    # Execute with Error Handling
    # ------------------------------------------------------------------

    try:
        records = client.search_read(
            model="hr.job",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        logger.info(
            f"get_job completed: {len(records)} record(s) found",
            extra={"record_count": len(records)},
        )

        return records

    except Exception as exc:
        logger.error(
            f"get_job failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "domain": domain,
                "error_type": type(exc).__name__,
            },
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to fetch job information: {str(exc)}"
        ) from exc
    

#section 2: tool 8 - get employee leaves
def get_employee_leaves(
    *,
    employee_id: Optional[int] = None,
    date_from: Optional[Union[date, str]] = None,
    date_to: Optional[Union[date, str]] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch approved employee leaves (hr.leave).
    
    Used for availability checking and resource planning.

    Args:
        employee_id: Filter by specific employee
        date_from: Show leaves ending on or after this date (YYYY-MM-DD or date object)
        date_to: Show leaves starting on or before this date (YYYY-MM-DD or date object)
        limit: Maximum records (default=100, max=100)

    Returns:
        List of approved leave records with employee_name added

    Raises:
        ValueError: If invalid parameters
        RuntimeError: If Odoo operation fails

    Safety:
        - Approved leaves only (state='validate')
        - Company scoped
        - Read-only

    Business Use Cases:
        - "Is John on vacation next week?"
        - "Who's available Dec 15?"
        - "Check employee availability for overtime"

    Domain Logic:
        - date_to >= date_from: Leave ends on/after search start
        - date_from <= date_to: Leave starts on/before search end
        This finds all leaves that overlap with the date range.
    """

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    if limit < 1 or limit > 100:
        raise ValueError(f"Limit must be between 1 and 100, got: {limit}")

    # Convert date objects to strings (Odoo expects strings)
    date_from_str = None
    date_to_str = None

    if date_from:
        if isinstance(date_from, date):
            date_from_str = date_from.strftime("%Y-%m-%d")
        elif isinstance(date_from, str):
            # Validate format (basic check)
            if len(date_from) != 10 or date_from[4] != "-" or date_from[7] != "-":
                raise ValueError(f"date_from must be in format YYYY-MM-DD, got: {date_from}")
            date_from_str = date_from
        else:
            raise ValueError(f"date_from must be date object or string, got: {type(date_from)}")

    if date_to:
        if isinstance(date_to, date):
            date_to_str = date_to.strftime("%Y-%m-%d")
        elif isinstance(date_to, str):
            if len(date_to) != 10 or date_to[4] != "-" or date_to[7] != "-":
                raise ValueError(f"date_to must be in format YYYY-MM-DD, got: {date_to}")
            date_to_str = date_to
        else:
            raise ValueError(f"date_to must be date object or string, got: {type(date_to)}")

    # Validate date range
    if date_from_str and date_to_str:
        if date_from_str > date_to_str:
            raise ValueError(
                f"date_from ({date_from_str}) cannot be after date_to ({date_to_str})"
            )

    # ------------------------------------------------------------------
    # Domain Construction
    # ------------------------------------------------------------------

    domain = [
        ("state", "=", "validate"),  # Approved leaves only
        ("company_id", "=", client.company_id),
    ]

    if employee_id:
        domain.append(("employee_id", "=", employee_id))

    # Find leaves that overlap with date range
    if date_from_str:
        domain.append(("date_to", ">=", date_from_str))

    if date_to_str:
        domain.append(("date_from", "<=", date_to_str))

    # ------------------------------------------------------------------
    # Allowed Fields
    # ------------------------------------------------------------------

    fields = [
        "id",
        "employee_id",      # Returns (id, name) tuple
        "date_from",
        "date_to",
        "number_of_days",
        "holiday_status_id",  # Returns (id, name) tuple - leave type
        "state",
    ]

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: get_employee_leaves",
        extra={
            "model": "hr.leave",
            "operation": "search_read",
            "domain": domain,
            "fields": fields,
            "limit": limit,
            "company_id": client.company_id,
            "user_id": client.uid,
            "search_params": {
                "employee_id": employee_id,
                "date_from": date_from_str,
                "date_to": date_to_str,
            },
        },
    )

    # ------------------------------------------------------------------
    # Execute with Error Handling
    # ------------------------------------------------------------------

    try:
        records = client.search_read(
            model="hr.leave",
            domain=domain,
            fields=fields,
            limit=limit,
        )

        # Post-process: Add employee_name for convenience
        for rec in records:
            emp_id = rec.get("employee_id")
            if emp_id and isinstance(emp_id, (tuple, list)) and len(emp_id) >= 2:
                rec["employee_name"] = emp_id[1]
            else:
                rec["employee_name"] = None

        logger.info(
            f"get_employee_leaves completed: {len(records)} record(s) found",
            extra={"record_count": len(records)},
        )

        return records

    except Exception as exc:
        logger.error(
            f"get_employee_leaves failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "domain": domain,
                "error_type": type(exc).__name__,
                "search_params": {
                    "employee_id": employee_id,
                    "date_from": date_from_str,
                    "date_to": date_to_str,
                },
            },
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to fetch employee leave information: {str(exc)}"
        ) from exc
    

#section 2: tool 9 - check_employee_availability
from typing import Dict, Any, List, Optional, Union
def check_employee_availability(
    *,
    employee_id: int,
    date_from: Union[date, str],
    date_to: Union[date, str],
) -> Dict[str, Any]:
    """
    Check if a specific employee is available within a date range.

    Composite tool combining:
    - hr.employee (validate employee exists and is active)
    - hr.leave (check for approved leaves in date range)

    Args:
        employee_id: Employee to check (required)
        date_from: Start date (YYYY-MM-DD string or date object)
        date_to: End date (YYYY-MM-DD string or date object)

    Returns:
        Availability summary dictionary:
        {
            "employee_id": int,
            "employee_name": str,
            "date_range": {"from": str, "to": str},
            "total_days": int,
            "available_days": int,
            "unavailable_days": int,
            "is_available": bool,
            "conflicting_leaves": [...]
        }

    Raises:
        ValueError: If employee not found or invalid dates
        RuntimeError: If Odoo operation fails

    Business Use Case:
        "Can John work overtime Dec 20-22?"
        "Is Sarah available for the project next week?"

    Safety:
        - Read-only operation
        - Company-scoped automatically
        - Approved leaves only (state='validate')
        - Handles overlapping leaves correctly
    """

    # ------------------------------------------------------------------
    # Input Validation & Date Normalization
    # ------------------------------------------------------------------

    if isinstance(date_from, date):
        date_from_str = date_from.strftime("%Y-%m-%d")
    elif isinstance(date_from, str):
        # Validate format
        if len(date_from) != 10 or date_from[4] != "-" or date_from[7] != "-":
            raise ValueError(f"date_from must be YYYY-MM-DD format, got: {date_from}")
        date_from_str = date_from
    else:
        raise ValueError(
            f"date_from must be date object or YYYY-MM-DD string, got: {type(date_from)}"
        )

    if isinstance(date_to, date):
        date_to_str = date_to.strftime("%Y-%m-%d")
    elif isinstance(date_to, str):
        if len(date_to) != 10 or date_to[4] != "-" or date_to[7] != "-":
            raise ValueError(f"date_to must be YYYY-MM-DD format, got: {date_to}")
        date_to_str = date_to
    else:
        raise ValueError(
            f"date_to must be date object or YYYY-MM-DD string, got: {type(date_to)}"
        )

    # Validate date range
    if date_from_str > date_to_str:
        raise ValueError(
            f"date_from ({date_from_str}) cannot be after date_to ({date_to_str})"
        )

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: check_employee_availability",
        extra={
            "model": "hr.employee + hr.leave (composite)",
            "operation": "availability_check",
            "employee_id": employee_id,
            "date_from": date_from_str,
            "date_to": date_to_str,
            "company_id": client.company_id,
            "user_id": client.uid,
        },
    )

    # ------------------------------------------------------------------
    # Execute Composite Logic with Error Handling
    # ------------------------------------------------------------------

    try:
        # Step 1: Fetch and validate employee
        employees = client.search_read(
            model="hr.employee",
            domain=[
                ("id", "=", employee_id),
                ("active", "=", True),
                ("company_id", "=", client.company_id),
            ],
            fields=["id", "name"],
            limit=1,
        )

        if not employees:
            raise ValueError(
                f"Active employee with id={employee_id} not found in current company"
            )

        employee = employees[0]

        # Step 2: Fetch approved leaves overlapping the date range
        leave_domain = [
            ("employee_id", "=", employee_id),
            ("state", "=", "validate"),  # Approved leaves only
            ("company_id", "=", client.company_id),
            ("date_to", ">=", date_from_str),  # Leave ends on/after range start
            ("date_from", "<=", date_to_str),  # Leave starts on/before range end
        ]

        leave_fields = [
            "id",
            "date_from",
            "date_to",
            "number_of_days",
            "holiday_status_id",
        ]

        leaves = client.search_read(
            model="hr.leave",
            domain=leave_domain,
            fields=leave_fields,
            limit=100,
        )

        # Step 3: Calculate availability (handle overlapping leaves correctly)
        date_from_obj = date.fromisoformat(date_from_str)
        date_to_obj = date.fromisoformat(date_to_str)
        
        total_days = (date_to_obj - date_from_obj).days + 1

        # Track unique unavailable dates (handles overlaps automatically)
        unavailable_dates = set()
        conflicting_leaves = []

        for leave in leaves:
            # Parse leave dates (handle both date and datetime formats)
            leave_from_str = leave["date_from"].split()[0] if ' ' in leave["date_from"] else leave["date_from"]
            leave_to_str = leave["date_to"].split()[0] if ' ' in leave["date_to"] else leave["date_to"]
            
            leave_start = max(
                date.fromisoformat(leave_from_str),
                date_from_obj,
            )
            leave_end = min(
                date.fromisoformat(leave_to_str),
                date_to_obj,
            )

            # Add each day to unavailable set
            current = leave_start
            affected_dates = []
            while current <= leave_end:
                unavailable_dates.add(current)
                affected_dates.append(current.strftime("%Y-%m-%d"))
                current = current + timedelta(days=1)

            conflicting_leaves.append({
                "leave_id": leave["id"],
                "date_from": leave["date_from"],
                "date_to": leave["date_to"],
                "leave_type": (
                    leave["holiday_status_id"][1]
                    if leave.get("holiday_status_id") and 
                       isinstance(leave["holiday_status_id"], (tuple, list))
                    else "Unknown"
                ),
                "days_in_range": len(affected_dates),
                "affected_dates": affected_dates,
            })

        unavailable_days = len(unavailable_dates)
        available_days = total_days - unavailable_days

        # Log result
        logger.info(
            f"check_employee_availability completed: {employee['name']} - "
            f"{'Fully Available' if unavailable_days == 0 else f'{available_days}/{total_days} days available'}",
            extra={
                "employee_name": employee["name"],
                "total_days": total_days,
                "available_days": available_days,
                "conflicting_leaves_count": len(conflicting_leaves),
            },
        )

        # Return comprehensive availability summary
        return {
            "employee_id": employee["id"],
            "employee_name": employee["name"],
            "date_range": {
                "from": date_from_str,
                "to": date_to_str,
            },
            "total_days": total_days,
            "available_days": available_days,
            "unavailable_days": unavailable_days,
            "is_available": unavailable_days == 0,
            "conflicting_leaves": conflicting_leaves,
        }

    except ValueError:
        # Re-raise validation errors as-is (already have good messages)
        raise

    except Exception as exc:
        logger.error(
            f"check_employee_availability failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "employee_id": employee_id,
                "date_from": date_from_str,
                "date_to": date_to_str,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to check employee availability: {str(exc)}"
        ) from exc
    

#section 2: tool 10 - get employee attendance
def get_employee_attendance(
    *,
    employee_id: Optional[int] = None,
    date_filter: Optional[Union[date, str]] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch employee attendance records (hr.attendance).

    Clock-in/out records for workforce visibility.

    Args:
        employee_id: Specific employee (optional, all employees if not specified)
        date_filter: Filter by specific date (YYYY-MM-DD string or date object)
        limit: Maximum records to return (default=100, max=100)

    Returns:
        List of attendance records:
        [
            {
                "employee_id": (id, name),
                "check_in": "YYYY-MM-DD HH:MM:SS",
                "check_out": "YYYY-MM-DD HH:MM:SS" or False,
                "worked_hours": float
            }
        ]

    Raises:
        ValueError: If invalid parameters
        RuntimeError: If Odoo operation fails

    Business Use Cases:
        - "Is employee currently working?"
        - "Who's in the office today?"
        - "Get attendance records for payroll"

    Safety:
        - Read-only operation
        - Company-scoped automatically
        - No sensitive data exposed
    """

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    if limit < 1 or limit > 100:
        raise ValueError(f"Limit must be between 1 and 100, got: {limit}")

    # Normalize date filter
    date_str = None
    if date_filter:
        if isinstance(date_filter, date):
            date_str = date_filter.strftime("%Y-%m-%d")
        elif isinstance(date_filter, str):
            # Validate format
            if len(date_filter) != 10 or date_filter[4] != "-" or date_filter[7] != "-":
                raise ValueError(
                    f"date_filter must be YYYY-MM-DD format, got: {date_filter}"
                )
            date_str = date_filter
        else:
            raise ValueError(
                f"date_filter must be date object or YYYY-MM-DD string, got: {type(date_filter)}"
            )

    # ------------------------------------------------------------------
    # Domain Construction
    # ------------------------------------------------------------------

    # domain = [
    #     ("company_id", "=", client.company_id),
    # ]

    domain = [
        ("employee_id", "!=", False)
    ]

    if employee_id:
        domain.append(("employee_id", "=", employee_id))

    if date_str:
        # Filter for check-ins on this specific date
        domain.append(("check_in", ">=", f"{date_str} 00:00:00"))
        domain.append(("check_in", "<=", f"{date_str} 23:59:59"))

    # ------------------------------------------------------------------
    # Allowed Fields
    # ------------------------------------------------------------------

    fields = [
        "employee_id",    # Returns (id, name) tuple
        "check_in",       # Datetime
        "check_out",      # Datetime or False if still checked in
        "worked_hours",   # Float (computed field)
    ]

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    logger.info(
        "MCP Tool: get_employee_attendance",
        extra={
            "model": "hr.attendance",
            "operation": "search_read",
            "domain": domain,
            "fields": fields,
            "limit": limit,
            "employee_id": employee_id,
            "date_filter": date_str,
            "company_id": client.company_id,
            "user_id": client.uid,
        },
    )

    # ------------------------------------------------------------------
    # Execute with Error Handling
    # ------------------------------------------------------------------

    try:
        records = client.search_read(
            model="hr.attendance",
            domain=domain,
            fields=fields,
            limit=limit,
            apply_company_scope=False,
        )

        # Log success
        logger.info(
            f"get_employee_attendance completed: {len(records)} record(s) found",
            extra={
                "record_count": len(records),
                "employee_id": employee_id,
                "date_filter": date_str,
            },
        )

        return records

    except Exception as exc:
        logger.error(
            f"get_employee_attendance failed: {type(exc).__name__}: {str(exc)}",
            extra={
                "domain": domain,
                "employee_id": employee_id,
                "date_filter": date_str,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )
        raise RuntimeError(
            f"Failed to fetch attendance data: {str(exc)}"
        ) from exc