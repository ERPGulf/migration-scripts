#!/bin/bash

SITE="benchui.erpgulf.com"  # change this to your actual site name

bench --site "$SITE" console <<EOF
invoices = frappe.get_all("Sales Invoice", filters={"docstatus": 0}, fields=["name"])
for invoice in invoices:
    doc = frappe.get_doc("Sales Invoice", invoice.name)
    doc.submit()
    frappe.db.commit()
    print(f"Submitted: {doc.name}")
exit()
EOF