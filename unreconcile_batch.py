# unreconcile payment entry in batches 
#runt it like below
#bench --site site01 execute yourapp.unreconcile_batch.unreconcile_in_batches --args '["PAY202500695", 10]'
# your_app/your_app/unreconcile_batch.py

import frappe

def unreconcile_in_batches(payment_entry: str, batch_size: int = 10):
    """
    Run in chunks to avoid timeouts/memory issues.
    Execute with:
    bench execute "your_app.unreconcile_batch.unreconcile_in_batches" --args '["PAY202500695", 10]'
    """

    company = frappe.db.get_value("Payment Entry", payment_entry, "company")
    if not company:
        frappe.throw(f"Payment Entry {payment_entry} not found")

    # Pull allocations once
    probe = frappe.new_doc("Unreconcile Payment")
    probe.company = company
    probe.voucher_type = "Payment Entry"
    probe.voucher_no = payment_entry
    allocs = probe.get_allocations_from_payment() or []

    total = len(allocs)
    processed = 0

    print(f"Total allocations: {total}")

    while processed < total:
        batch = allocs[processed: processed + batch_size]
        print(f"Processing {len(batch)} items... (starting at index {processed})")

        try:
            doc = frappe.new_doc("Unreconcile Payment")
            doc.company = company
            doc.voucher_type = "Payment Entry"
            doc.voucher_no = payment_entry

            for a in batch:
                doc.append("allocations", frappe._dict(a))

            doc.save()
            doc.submit()
            frappe.db.commit()

            processed += len(batch)
            print(f"Done: {processed}/{total}")

        except Exception as e:
            frappe.db.rollback()
            print(f"FAILED at {processed}. Error: {e}")
            raise

    print("Completed.")

~                                 
