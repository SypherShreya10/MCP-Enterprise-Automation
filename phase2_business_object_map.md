# Phase 2A — Business Object Map (Current Odoo Installation)

| Business Concept  | Odoo Model  | Key Fields     | Allowed Operations |
| ----------------- | ----------- | -------------- | ------------------ |
| Person / Org      | res.partner | name, email    | read, create       |
| System User       | res.users   | login, active  | read               |
| Organization      | res.company | name, currency | read               |
| Role / Permission | res.groups  | name           | read               |


# Phase 2B — Business Object Map (ERP + HRIS + CRM)

| Business Concept   | Odoo Model    | Key Fields                               | Allowed Operations |
| ------------------ | ------------- | ---------------------------------------- | ------------------ |
| Person / Contact   | res.partner   | name, email, phone                       | read, create       |
| System User        | res.users     | login, active, company_id                | read               |
| Organization       | res.company   | name, currency_id                        | read               |
| Role / Permission  | res.groups    | name                                     | read               |
| Employee           | hr.employee   | name, job_id, department_id              | read               |
| Department         | hr.department | name, manager_id                         | read               |
| Job Role           | hr.job        | name                                     | read               |
| Lead / Opportunity | crm.lead      | name, stage_id, partner_id               | read, update       |
| Sales Stage        | crm.stage     | name, sequence                           | read               |
| Task / Follow-up   | mail.activity | activity_type_id, user_id, date_deadline | read, create       |
