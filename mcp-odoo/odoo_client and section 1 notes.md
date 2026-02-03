# SECTION 1 — MCP ↔ ODOO INTEGRATION

## **Architecture, Tools, and Execution Model (Detailed Notes)**

---

## 1. HIGH-LEVEL ARCHITECTURE

### 🧱 What You Built (Big Picture)

```
LLM (Claude)
   ↓ (MCP protocol)
MCP Server (FastMCP)
   ↓ (tool calls)
Domain Tools (get_partner, create_partner, get_user, get_company)
   ↓ (safe primitives only)
OdooClient (single gateway)
   ↓ (XML-RPC)
Odoo ERP (Docker instance)
```

### 🔑 Key Architectural Principle

> **The AI never talks to Odoo directly.**
> **The AI only talks to tools.**
> **Tools only talk to Odoo via `OdooClient`.**

This prevents:

* accidental writes
* full table scans
* cross-company data leaks
* privilege escalation

---

## 2. THE ROLE OF `odoo_client.py` (CORE FOUNDATION)

### 🧠 What is `OdooClient`?

`OdooClient` is **the only object allowed to communicate with Odoo**.

Think of it as:

> *A secure, opinionated firewall + translator between Python and Odoo.*

---

### 🔌 What Protocol Is Used?

**XML-RPC** (Odoo standard external API)

Why XML-RPC (and not JSON-RPC)?

* XML-RPC is:

  * officially supported
  * stable
  * permission-aware
  * works cleanly with Docker setups
* JSON-RPC is mainly for browser/web clients

---

### 🧩 What `OdooClient` Does (Step-by-Step)

#### 1. Authentication

```python
uid = common.authenticate(db, username, password)
```

* Logs in once
* Stores `uid` (user ID)
* Establishes identity for **every operation**

---

#### 2. Determine Current Company (Bootstrap)

```python
res.users.read(uid, ["company_id"])
```

Why this special handling?

* Company scoping cannot be applied *before* knowing the company
* This bootstrap step bypasses safety filters **only once**

Result:

```text
Authenticated user → company_id = 1
```

---

#### 3. Safe Read (`search_read`)

Every read:

* validates limit
* validates fields
* validates domain
* **automatically injects company scope**

Injected silently:

```python
| (company_id = current) OR (company_id = False)
```

This guarantees:

* no cross-company leakage
* shared records still visible

---

#### 4. Safe Create (`create`)

Rules enforced:

* `company_id` cannot be set manually
* company is injected automatically
* values must be allowlisted by tools

---

#### 5. Centralized Logging

Every operation logs:

* model
* operation type
* domain
* fields
* limit / values

This is **audit-grade logging**.

---

## 3. TOOL DESIGN PATTERN (VERY IMPORTANT)

Every tool you wrote follows the **same mental model**:

---

### 🔁 Universal Tool Flow

```
1. Validate inputs
2. Resolve defaults
3. Build domain (filters)
4. Enforce safety constraints
5. Allowlist fields
6. Log intent
7. Call OdooClient
8. Handle errors
9. Return safe output
```

If someone asks *“How do your tools work?”*
This is the answer.

---

## 4. TOOL-BY-TOOL DOCUMENTATION

---

## 🧰 TOOL 001 — `get_partner`

### Purpose

Fetch contacts/customers/suppliers safely.

### Question Asked to Odoo

> “Find partners matching these criteria, **only active**, **only in my company**, and return **only safe fields**.”

### Domain Examples

```python
[
  ("name", "ilike", "AutoCorp"),
  ("active", "=", True),
  "|",
  ("company_id", "=", 1),
  ("company_id", "=", False)
]
```

### Answer Returned

A **list of partners**:

```json
[
  {
    "id": 15,
    "name": "Azure Interior",
    "email": "...",
    "customer_rank": 6,
    "supplier_rank": 0,
    "is_customer": true
  }
]
```

### Why It’s Safe

* No full-table scan allowed
* Company-scoped
* Read-only
* No internal fields

---

## 🧰 TOOL 002 — `create_partner`

### Purpose

Create a new customer/supplier/contact.

### Question Asked to Odoo

> “Create a new partner with these allowed fields and assign it to **my company**.”

### Pre-Checks

* name exists?
* email format valid?
* credit limit valid?
* uniqueness within company?

### What Odoo Receives

```python
create({
  "name": "MCP Test Partner",
  "email": "...",
  "customer_rank": 1,
  "company_id": 1
})
```

### Answer Returned

```json
{
  "partner_id": 72,
  "message": "Partner created successfully."
}
```

### Why It’s Safe

* No manual company assignment
* No forbidden fields
* No updates allowed (create-only)
* Logged for audit

---

## 🧰 TOOL 003 — `get_user`

### Purpose

Fetch **internal system users** (not portal users).

### Question Asked to Odoo

> “Find internal, active users who belong to my company and match these filters.”

### Domain Highlights

```python
[
  ("active", "=", True),
  ("share", "=", False),
  ("company_ids", "in", [1])
]
```

### Answer Returned

```json
[
  {
    "id": 2,
    "name": "Shreya Admin",
    "login": "shreya@...",
    "company_ids": [1,2,3]
  }
]
```

### Why It’s Safe

* No passwords
* No groups
* No tokens
* Company-scoped via `company_ids`

---

## 🧰 TOOL 004 — `get_company`

### Purpose

Get **current company context**.

### Question Asked to Odoo

> “Give me details of **my current company only**.”

### Domain

```python
[("id", "=", current_company_id)]
```

### Answer Returned

```json
{
  "id": 1,
  "name": "My Company (San Francisco)",
  "currency_id": ["USD"],
  "email": "...",
  "phone": "..."
}
```

### Why It’s Extra Secure

* Single-record only
* Explicit cross-company block
* No company scoping injected (not applicable)
* Read-only

---

## 5. WHY THESE CONSTRAINTS EXIST (FOR REVIEWS)

### 🔒 Company Scoping

Prevents:

* data leaks
* incorrect assignments
* cross-tenant access

### 📋 Field Allowlisting

Prevents:

* exposure of passwords
* accounting internals
* security configuration

### 🔢 Limit Enforcement

Prevents:

* accidental bulk reads
* performance degradation

### 🧾 Logging

Enables:

* audit trails
* incident investigation
* compliance checks

---

## 6. MCP SERVER ROLE

### What MCP Does

* Exposes tools to LLMs
* Validates tool schemas
* Routes calls to Python functions

### What MCP Does *NOT* Do

* It does not talk to Odoo
* It does not enforce business rules
* It does not bypass safety

All intelligence is **below MCP**, not inside it.

---

## 7. ONE-SENTENCE SUMMARY (USE THIS IN REVIEWS)

> *“We built a layered, safety-first MCP integration where all AI-driven ERP operations are mediated through auditable, company-scoped tools backed by a single secure Odoo client.”*

---

## 8. FINAL REASSURANCE
* enforced multi-company isolation
* designed tool-level contracts
* prevented privilege escalation
* created testable, reviewable ERP tools
