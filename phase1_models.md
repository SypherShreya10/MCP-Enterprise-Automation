## ## Model:res.partner
# # What real-world entity does this represent??

Represents any real-world person or organization known to the system.
Used for students, teachers, employees, vendors, customers, and companies.
Acts as the central identity record in Odoo.

# # Why does this model exist??

To maintain a single, persistent identity per entity while allowing multiple roles
(user, employee, customer, vendor) to be attached without duplication.

# # What kind of data does it store??

Identity information (name, individual or organization)

Contact details (email, phone, address)

Hierarchical relationships (parent organization)

System linkage metadata (user link, audit fields)

Classification and extensible metadata

# # Key relationships with other models

Linked to res.users for system login access

Linked to res.company to represent organizations

Linked to hr.employee to represent employment

Referenced by multiple business models as the actor or owner

# # Business-sensible actions on this model

Allowed:

Read partner information

Create new partners via Odoo workflows

Update contact or classification details

Not allowed / risky:

Direct deletion

Direct SQL updates

Uncontrolled bulk modification

# Special notes

This is a core, high-risk model.
All other business and access models depend on it.
It must be treated as read-heavy and write-sensitive.


## ## Model:res.users
# # What real-world entity does this represent??

Represents a system user account that is allowed to log in and perform actions in Odoo.
It does not represent a person directly; instead, it represents access and authority
granted to a real-world entity that exists in res.partner.

# # Why does this model exist??

To separate identity from access control.
This allows a real-world person or organization to exist in the system without
necessarily having login permissions, and allows access to be enabled, disabled,
or modified without affecting the underlying identity.

# # What kind of data does it store??

Login and authentication information

Access status (active or inactive)

Company context for user actions

Links to the corresponding real-world identity

Audit information identifying which user performed system actions

# # Key relationships with other models

Linked to res.partner via partner_id

Linked to res.company to define operating context

Linked to res.groups to define roles and permissions

Referenced by most system and business models via audit fields

# # Business-sensible actions on this model

Allowed:

Read user information for auditing or display

Manage users only through controlled Odoo workflows

Not allowed / risky:

Direct SQL updates

Automated creation, deletion, or modification by AI systems

# Special notes

This is one of the most security-sensitive models in the system.
It represents authority, not identity.
AI systems must never directly modify this model.

## Model:res.company
# What real-world entity does this represent??

Represents an organization or operational entity on whose behalf actions are performed
in the system, such as a company, institution, subsidiary, or branch.

# Why does this model exist??

To explicitly represent organizational context and support multi-company operations,
data isolation, and organization-specific configuration.

# What kind of data does it store??

Organizational identity and linkage to a partner record

Company-specific defaults (currency, sequences)

Reporting and presentation configuration

Hierarchical company relationships

Audit and lifecycle information

# Key relationships with other models

Linked to res.partner to represent the organization as an identity

Linked to res.users for company-scoped access

Referenced by most business models to scope records

# Business-sensible actions on this model

Allowed:

Read company information

Modify company settings via administrative workflows

Not allowed / risky:

Direct SQL updates

Automated creation or alteration by AI systems

Special notes

This model defines organizational boundaries.
Incorrect handling can cause data leakage or cross-company contamination.

## Model:res.groups
# What real-world entity does this represent??

Represents a role or permission set within the system.

# Why does this model exist??

To manage access control in a scalable and structured way by grouping permissions
instead of assigning them directly to users.

# What kind of data does it store??

Group identity and descriptions

Permission inheritance and hierarchy

Metadata related to access scope

Audit information

# Key relationships with other models

Linked to res.users for role assignment

Linked to access control and record rule models

Controls visibility of menus, views, and actions

# Business-sensible actions on this model

Allowed:

Read group and role definitions

Manage groups through administrative workflows

Not allowed / risky:

Automated group assignment by AI systems

Direct SQL modification

Special notes

This model is central to system security.
Incorrect changes can grant unintended access or expose sensitive data.

## Model:hr.employee
# What real-world entity does this represent??

Represents a person in their role as an employee of an organization.

# Why does this model exist??

To separate employment information from identity and system access.

# What kind of data does it store??

Employment identity and status

Organizational placement and reporting structure

Work contact information

Personal and legal HR data

Audit and lifecycle information

# Key relationships with other models

Linked to res.partner for identity and contact data

Optionally linked to res.users for system access

Linked to res.company and hr.department

Self-referential management hierarchy

# Business-sensible actions on this model

Allowed:

Read employee information for reporting and context

Not allowed / risky:

Automated updates or deletions

Direct SQL modification

Special notes

This is a highly sensitive HR model.
AI systems must treat it as strictly read-only.

## Model:hr.department
# What real-world entity does this represent??

Represents an organizational unit within a company.

# Why does this model exist??

To model internal structure, reporting lines, and workflow routing.

# What kind of data does it store??

Department identity and hierarchy

Company association

Department manager

Notes and lifecycle metadata

# Key relationships with other models

Linked to res.company

Linked to hr.employee for managers

Referenced by hr.job and workflow models

# Business-sensible actions on this model

Allowed:

Read department structure

Not allowed / risky:

Automated restructuring or deletion

Special notes

This is a structural, relatively stable model.
AI systems should use it only for context.

## Model:hr.job
# What real-world entity does this represent??

Represents a job position or role within an organization.

# Why does this model exist??

To define organizational roles independently of individual employees.

# What kind of data does it store??

Job identity and title

Department and company placement

Recruitment and planning metadata

Role descriptions and requirements

# Key relationships with other models

Linked to hr.department and res.company

Referenced by hr.employee

# Business-sensible actions on this model

Allowed:

Read job definitions

Not allowed / risky:

Automated creation or modification

Special notes

This is a stable reference model.
AI systems must treat it as read-only.

## Model:crm.lead
# What real-world entity does this represent??

Represents a sales lead or business opportunity.

# Why does this model exist??

To track potential business interactions as they move through a sales pipeline.

# What kind of data does it store??

Lead identity

Pipeline stage

Ownership and responsibility

Optional customer linkage

Revenue expectations and lifecycle data

# Key relationships with other models

Linked to res.partner, res.users, crm.stage, crm.team, and res.company

Integrated with mail.activity for follow-ups

# Business-sensible actions on this model

Allowed:

Read lead information

Update stage under controlled rules

Not allowed / risky:

Deletion

Uncontrolled updates

Special notes

CRM automation should assist decision-making, not replace it.

## Model:crm.stage
# What real-world entity does this represent??

Represents a sales pipeline stage.

# Why does this model exist??

To standardize sales progression and pipeline analysis.

# What kind of data does it store??

Stage identity and ordering

Completion indicators

Display and lifecycle metadata

# Business-sensible actions on this model

Allowed:

Read stage definitions

Not allowed / risky:

Automated modification

Special notes

Stages are stable reference data and must be treated as read-only.

## Model:crm.team
# What real-world entity does this represent??

Represents a sales team responsible for managing opportunities.

# Why does this model exist??

To group sales responsibility and enable team-level reporting.

# Business-sensible actions on this model

Allowed:

Read team definitions

Not allowed / risky:

Automated reassignment or modification

## Model:mail.activity
# What real-world entity does this represent??

Represents a task or follow-up assigned to a user.

# Why does this model exist??

To ensure important business actions are tracked and completed.

# What kind of data does it store??

Activity type

Assigned user

Deadline

Related business record

# Business-sensible actions on this model

Allowed:

Read activities

Create follow-up tasks

Not allowed / risky:

Automated completion or deletion

Special notes

This is a low-risk, high-impact model for AI assistance.