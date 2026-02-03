HARE KRISHNA

Below are **Section 2 notes written in the *same depth, structure, and tone* as your Section 1 document**, but **explicitly optimized for a LangGraph engineer**.
The goal is that someone building workflows can read this and immediately know **which tool to call, why, in what order, and what guarantees they get**.

I’ve mirrored the architectural language and mental models from your Section 1 notes so both sections feel like one coherent system.

---

# SECTION 2 — HR / EMPLOYEE MANAGEMENT

## **Read-Only Workforce Intelligence via MCP Tools**

---

## 1. SECTION 2 PHILOSOPHY (WHY THIS SECTION EXISTS)

Section 2 tools answer **people-centric questions** that workflows *must* know before acting:

* Who is an employee?
* Which department do they belong to?
* What role do they have?
* Are they on leave?
* Are they available during a given time window?
* Are they currently clocked in?

> **Key rule:**
> Section 2 tools never *change* HR data.
> They only **observe, validate, and contextualize** it.

This makes them safe to use inside **planning, routing, and decision workflows** in LangGraph.

---

## 2. HOW SECTION 2 FITS INTO THE OVERALL ARCHITECTURE

```
LangGraph Agent
   ↓ (decides next step)
MCP Tool Call (HR Tool)
   ↓
HR Domain Tool (tools/hr.py)
   ↓
OdooClient.search_read()
   ↓
Odoo HR Models
```

Exactly the same architecture as Section 1 — **no special cases**.

What changes is **what kind of questions are being asked**.

---

## 3. IMPORTANT MODEL DIFFERENCE (LANGGRAPH ENGINEERS MUST KNOW THIS)

Not all HR models behave the same with respect to `company_id`.

| Model           | Has `company_id` field? | Handling                        |
| --------------- | ----------------------- | ------------------------------- |
| `hr.employee`   | ✅ Yes                   | Explicit company filter         |
| `hr.department` | ✅ Yes                   | Explicit company filter         |
| `hr.job`        | ⚠️ Sometimes shared     | Company scoping via OdooClient  |
| `hr.leave`      | ✅ Yes                   | Explicit company filter         |
| `hr.attendance` | ❌ **No**                | ❗ **No company filter allowed** |

This is why:

* `get_employee_attendance` **must not** use `company_id`
* All other HR tools **must**

This distinction is enforced partly in tools and partly in `OdooClient`.

---

## 4. TOOL DESIGN PATTERN (SAME AS SECTION 1)

Every HR tool follows the same invariant pipeline:

```
1. Validate inputs (fail early)
2. Normalize inputs (dates, strings)
3. Build domain (filters)
4. Enforce HR safety constraints
5. Allowlist fields (privacy!)
6. Log intent
7. Call OdooClient
8. Post-process if needed
9. Return workflow-safe output
```

LangGraph engineers can rely on this **consistency**.

---

## 5. TOOL-BY-TOOL DOCUMENTATION (SECTION 2)

---

## 🧰 TOOL 005 — `get_employee`

### Purpose

Fetch **public, work-related employee information**.

### Typical Workflow Questions

* “Who is Sarah Chen?”
* “List engineers in R&D”
* “Find employees reporting to X”

### Question Asked to Odoo

> “Give me **active employees in my company** matching these filters, excluding all private HR data.”

### Domain Guarantees

```python
[
  ("active", "=", True),
  ("company_id", "=", current_company),
  optional filters...
]
```

### Answer Returned

```json
[
  {
    "id": 18,
    "name": "Paul Williams",
    "job_id": [7, "Senior Engineer"],
    "department_id": [5, "R&D USA"],
    "parent_id": [3, "Marc Demo"],
    "work_email": "paul@company.com",
    "active": true
  }
]
```

### What Is Explicitly Excluded

* private email / phone
* home address
* identification numbers
* salary / wage
* bank details

### Why This Matters for LangGraph

* Safe to use in **routing, task assignment, approvals**
* Can be used as the **entry point** for almost all HR workflows

---

## 🧰 TOOL 006 — `get_department`

### Purpose

Understand **organizational structure**.

### Typical Workflow Questions

* “List all departments”
* “Who manages Engineering?”
* “What department is X under?”

### Question Asked to Odoo

> “Give me department hierarchy and managers for my company.”

### Answer Returned

```json
{
  "id": 5,
  "name": "R&D USA",
  "manager_id": [4, "Ronnie Hart"],
  "parent_id": [2, "Management"],
  "company_id": [1, "My Company"]
}
```

### Interpretation (Very Important)

* `parent_id` → hierarchy
* `manager_id` → reporting responsibility

LangGraph can build **org charts**, **approval chains**, and **routing logic** from this alone.

---

## 🧰 TOOL 007 — `get_job`

### Purpose

Fetch **role definitions**, not people.

### Typical Workflow Questions

* “What job positions exist?”
* “What does a Senior Engineer role mean?”
* “Which jobs belong to Engineering?”

### Question Asked to Odoo

> “Give me job role definitions and their department mapping.”

### Answer Returned

```json
{
  "id": 7,
  "name": "Senior Engineer",
  "department_id": [5, "R&D USA"],
  "description": "Handles long-term architecture and mentoring"
}
```

### Why LangGraph Needs This

* Distinguishes **role** from **person**
* Enables role-based routing (“any Senior Engineer can do this”)

---

## 🧰 TOOL 008 — `get_employee_leaves`

### Purpose

Check **approved time off**.

### Typical Workflow Questions

* “Is John on leave next week?”
* “Who is unavailable on Dec 15?”
* “Can we assign overtime?”

### Critical Constraint

Only **approved leaves**:

```python
("state", "=", "validate")
```

### Answer Returned

```json
{
  "employee_id": [18, "Paul Williams"],
  "date_from": "2024-12-20",
  "date_to": "2024-12-22",
  "holiday_status_id": [1, "Vacation"],
  "employee_name": "Paul Williams"
}
```

### Why LangGraph Must Use This

* Prevents scheduling conflicts
* Required before assignments or overtime workflows

---

## 🧰 TOOL 009 — `check_employee_availability` (COMPOSITE TOOL)

### Purpose

Answer **availability in one call**.

### What It Internally Does

1. Calls `hr.employee` → validates employee exists & active
2. Calls `hr.leave` → fetches approved overlapping leaves
3. Calculates exact day-level overlap (no double counting)

### Question Asked

> “Is this employee available between these dates?”

### Answer Returned

```json
{
  "employee_id": 18,
  "employee_name": "Paul Williams",
  "date_range": {
    "from": "2024-12-20",
    "to": "2024-12-22"
  },
  "total_days": 3,
  "available_days": 1,
  "unavailable_days": 2,
  "is_available": false,
  "conflicting_leaves": [...]
}
```

### Why This Is Gold for LangGraph

* Single-node decision
* No reasoning ambiguity
* Direct boolean (`is_available`) for branching

---

## 🧰 TOOL 010 — `get_employee_attendance`

### Purpose

Check **actual presence**, not planned availability.

### Typical Workflow Questions

* “Is employee currently working?”
* “Who is in the office today?”
* “Has X checked in?”

### Important Technical Constraint

`hr.attendance` **does NOT have `company_id`**

Therefore:

* ❌ No company filter
* ❌ No automatic company scoping
* ✅ Safety enforced by **required filters** (employee/date)

### Answer Returned

```json
{
  "employee_id": [18, "Paul Williams"],
  "check_in": "2024-01-15 09:02:11",
  "check_out": false,
  "worked_hours": 3.25
}
```

### How LangGraph Should Use This

* Real-time checks
* Guardrails before assigning live tasks
* Attendance-aware routing

---

## 6. SAFETY & PRIVACY SUMMARY (FOR REVIEWS)

| Protection             | How It’s Enforced             |
| ---------------------- | ----------------------------- |
| No writes              | No write primitives used      |
| No private HR data     | Field allowlists              |
| No cross-company leaks | Explicit filters + OdooClient |
| No full table scans    | Domain validation             |
| Auditability           | Centralized logging           |

---

## 7. HOW LANGGRAPH SHOULD THINK ABOUT SECTION 2

### Canonical Patterns

* **Identify person** → `get_employee`
* **Understand org context** → `get_department`, `get_job`
* **Check planned availability** → `get_employee_leaves` or `check_employee_availability`
* **Check real-time presence** → `get_employee_attendance`

### One Sentence Summary

> *“Section 2 provides read-only, privacy-safe HR intelligence tools that allow LangGraph workflows to reason about people, roles, availability, and presence without ever modifying HR data.”*

---
