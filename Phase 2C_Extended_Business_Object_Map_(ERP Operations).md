Purpose of this file
This document extends the Business Object Map to cover core ERP operational domains
(Inventory, Sales, Purchasing, Manufacturing, Accounting) required for enterprise automation.

It defines what business objects exist and what high-level operations AI systems may request,
without specifying technical enforcement or field-level access.


Inventory / Stock Management
| Business Concept   | Odoo Model       | Business Meaning                                | Allowed Operations |
| ------------------ | ---------------- | ----------------------------------------------- | ------------------ |
| Product (Variant)  | product.product  | A sellable or storable item                     | read               |
| Product (Template) | product.template | Generic product definition shared by variants   | read               |
| Stock Quantity     | stock.quant      | Quantity of product at a specific location      | read               |
| Stock Location     | stock.location   | Physical or logical place where stock is stored | read               |
| Stock Movement     | stock.move       | Movement of stock between locations             | read               |


Sales / Order Management
| Business Concept | Odoo Model      | Business Meaning                                     | Allowed Operations |
| ---------------- | --------------- | ---------------------------------------------------- | ------------------ |
| Sales Order      | sale.order      | Customer order requesting goods or services          | read, create       |
| Sales Order Line | sale.order.line | Individual product/service line within a sales order | read               |
| Customer Invoice | account.move    | Financial document requesting payment                | read               |


Purchasing / Procurement
| Business Concept    | Odoo Model          | Business Meaning                               | Allowed Operations |
| ------------------- | ------------------- | ---------------------------------------------- | ------------------ |
| Purchase Order      | purchase.order      | Order placed to a vendor for goods or services | read               |
| Purchase Order Line | purchase.order.line | Individual item within a purchase order        | read               |


Manufacturing (MRP)
Manufacturing applies to both physical goods and service-like production workflows.
| Business Concept    | Odoo Model     | Business Meaning                                       | Allowed Operations |
| ------------------- | -------------- | ------------------------------------------------------ | ------------------ |
| Manufacturing Order | mrp.production | Instruction to produce a product                       | read               |
| Bill of Materials   | mrp.bom        | Definition of components required to produce a product | read               |


Accounting / Finance
| Business Concept | Odoo Model      | Business Meaning                                     | Allowed Operations |
| ---------------- | --------------- | ---------------------------------------------------- | ------------------ |
| Accounting Entry | account.move    | Financial transaction (invoice, bill, journal entry) | read               |
| Payment Record   | account.payment | Record of payment made or received                   | read               |


HR Extensions (Operational HR)
| Business Concept    | Odoo Model    | Business Meaning                        | Allowed Operations |
| ------------------- | ------------- | --------------------------------------- | ------------------ |
| Employee Attendance | hr.attendance | Record of employee check-in / check-out | read               |
| Employee Leave      | hr.leave      | Time-off or leave request               | read               |
| Employment Contract | hr.contract.type   | Legal employment agreement              | read               |
