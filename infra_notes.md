# Infrastructure Notes — ERP + Database

## 1. Odoo Application Container

- Container name: odoo
- Docker image: odoo
- Exposed ports: 0.0.0.0:8069->8069/tcp, [::]:8069->8069/tcp
- Purpose: ERP application layer handling business logic
- Depends on: PostgreSQL database (db container)
- Developer mode: Enabled
- Access URL: http://localhost:8069/odoo/apps
- Notes: Used only as data producer. No direct AI access planned.

---

## 2. PostgreSQL Database Container

- Container name: db
- Docker image: postgres:15
- PostgreSQL version: 15.15
- Port: 5432 (internal Docker network)
- Database name(s): dummyERP, postgres, template0, template1
- Default DB user: odoo
- Authentication: Password-based via POSTGRES_USER / POSTGRES_PASSWORD environment variables
- Data persistence: Enabled via Docker volume (odoo-db mounted at /var/lib/postgresql/data)
- Connected application: Odoo ERP container (odoo)
- Notes:
  - Primary ERP database created via Odoo UI
  - Contains all business, academic, and HR data
  - Direct table modification avoided
  - Read-only access planned for MCP agents via SQL views

---

## 3. Networking & Access

- Odoo → DB connection: Internal Docker bridge network
- External DB access: Disabled (no host port binding)
- Internal Docker network: bridge
- Security notes: 
  - PostgreSQL accessible only to containers on Docker network
  - No public exposure of database port
  - Direct DB access restricted to Odoo container

---

## 4. MCP / Agent Readiness (Initial)

- Agent DB access allowed: Yes
- Mode: Read-only
- Allowed operations: SELECT via predefined SQL views
- Forbidden operations: INSERT, UPDATE, DELETE, DDL
- Planned DB views:
  - v_partners_basic
  - v_users_basic
  - v_attendance_summary