# AI Safety & Execution Constraints — Odoo MCP

## Purpose
This document defines execution-time safety constraints for all AI-initiated
operations against Odoo via MCP servers.

It enforces:
- Field-level access control
- Domain (filter) restrictions
- Rate limits and bulk access limits
- Cross-company and cross-module safety boundaries

This file MUST be enforced by the MCP server.
It MUST NOT be interpreted or bypassed by the AI agent.

---

## Global Execution Rules (Apply to ALL Models)

### Company & Access Scope
- All queries MUST be scoped to the current user’s company
- Cross-company reads are forbidden
- Cross-company writes are forbidden

### Query Limits
- Maximum records per request: 100
- Pagination is mandatory for larger result sets
- Full table scans are forbidden

### Operation Safety
- No raw SQL execution
- No dynamic field access
- No schema discovery by AI
- No access to technical or security models

### Audit & Traceability
- Every AI operation must be logged with:
  - model
  - operation
  - domain used
  - fields accessed
  - record count

---

## Inventory / Stock Management

### Model: product.product

Allowed Operations:
- read

Allowed Fields:
- id
- name
- default_code
- list_price
- type

Forbidden Fields:
- cost fields
- internal tracking fields
- accounting properties

Domain Restrictions:
- active = true

---

### Model: stock.quant

Allowed Operations:
- read

Allowed Fields:
- product_id
- quantity
- location_id

Forbidden Fields:
- inventory_value
- owner_id
- lot_id

Domain Restrictions:
- company_id = current_company
- quantity > 0

---

## Sales / Order Management

### Model: sale.order

Allowed Operations:
- read
- create

Allowed Fields (READ):
- id
- name
- partner_id
- date_order
- amount_total
- state

Allowed Fields (CREATE):
- partner_id
- order_line

Forbidden Fields:
- company_id
- create_uid
- write_uid
- internal notes
- fiscal locking fields

Domain Restrictions:
- company_id = current_company
- state != 'cancel'

---

### Model: sale.order.line

Allowed Operations:
- read

Allowed Fields:
- product_id
- product_uom_qty
- price_unit
- order_id

Forbidden Fields:
- discount_policy
- tax_computation internals

---

## Purchasing / Procurement

### Model: purchase.order

Allowed Operations:
- read

Allowed Fields:
- name
- partner_id
- date_order
- amount_total
- state

Forbidden Fields:
- approval metadata
- internal vendor ratings

Domain Restrictions:
- company_id = current_company

---

## Manufacturing (MRP)

### Model: mrp.production

Allowed Operations:
- read

Allowed Fields:
- name
- product_id
- product_qty
- state
- date_planned_start

Forbidden Fields:
- cost breakdown
- internal routing logic

Domain Restrictions:
- company_id = current_company

---

### Model: mrp.bom

Allowed Operations:
- read

Allowed Fields:
- product_tmpl_id
- product_qty
- type

Forbidden Fields:
- internal versioning metadata

---

## Accounting / Finance

### Model: account.move

Allowed Operations:
- read

Allowed Fields:
- name
- move_type
- amount_total
- state
- invoice_date

Forbidden Fields:
- journal_id
- tax_line_ids
- reconciliation metadata

Domain Restrictions:
- company_id = current_company
- move_type IN ('out_invoice', 'out_refund')

---

## HR Extensions

### Model: hr.employee

Allowed Operations:
- read

Allowed Fields:
- id
- name
- job_id
- department_id
- parent_id

Forbidden Fields:
- salary
- private_email
- private_phone
- identification numbers
- personal documents

Domain Restrictions:
- company_id = current_company
- active = true

---

### Model: hr.leave

Allowed Operations:
- read

Allowed Fields:
- employee_id
- date_from
- date_to
- state
- holiday_status_id

Forbidden Fields:
- approval chain metadata
- internal comments

Domain Restrictions:
- company_id = current_company

---

### Model: hr.attendance

Allowed Operations:
- read

Allowed Fields:
- employee_id
- check_in
- check_out

Forbidden Fields:
- device identifiers
- raw biometric metadata

Domain Restrictions:
- company_id = current_company

---

## Final Enforcement Notes

- Any request violating this file MUST be rejected
- Rejections must be explicit and logged
- This file is version-controlled and reviewed before expansion
- New models must be added here before exposure to AI systems
