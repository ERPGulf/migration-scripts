#!/usr/bin/env python3
# Fast block reconciliation: Retail SIs between 2025-01-01 and 2025-07-29
# Prompts only PE & Customer. Processes 100 at a time with ONE reconcile + ONE commit per block.
# Uses decreasing `remaining` so the "modified after you pulled it" check passes.

import sys
B="/opt/bench/frappe-bench"; S=f"{B}/sites"
sys.path += [f"{B}/apps/frappe", f"{B}/apps/erpnext", B, S]

import frappe
from frappe.utils import flt
from erpnext.accounts.utils import reconcile_against_document

SITE = "site01"
DATE_START, DATE_END = "2025-01-01", "2025-07-29"
REQUIRE_TYPE = "Retail"
BLOCK_SIZE = 1000      # bump to 300/500 if your DB is comfy

def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def main():
    frappe.init(site=SITE, sites_path=S)
    frappe.connect()
    try:
        PE   = input("Payment Entry (e.g. PAY202500676): ").strip()
        CUST = input("Customer code (e.g. 12210001): ").strip()

        pe = frappe.get_doc("Payment Entry", PE)
        if pe.docstatus != 1: raise Exception(f"{PE} not submitted")
        if pe.party_type != "Customer": raise Exception(f"{PE} party_type={pe.party_type}, expected Customer")
        if pe.party != CUST: raise Exception(f"{PE} is for {pe.party}, not {CUST}")

        pe_prec  = frappe.get_precision("Payment Entry", "unallocated_amount") \
                   or int(frappe.db.get_single_value("System Settings","currency_precision") or 2)
        ref_prec = frappe.get_precision("Payment Entry Reference", "allocated_amount") or pe_prec

        # 1) Fetch invoices via SQL (faster)
        rows = frappe.db.sql("""
            SELECT name, debit_to, outstanding_amount, due_date, posting_date
            FROM `tabSales Invoice`
            WHERE docstatus=1
              AND customer=%s
              AND outstanding_amount>0
              AND custom_invoice_type=%s
              AND posting_date BETWEEN %s AND %s
            ORDER BY posting_date ASC, name ASC
        """, (CUST, REQUIRE_TYPE, DATE_START, DATE_END), as_dict=True)

        pe_unalloc = flt(pe.unallocated_amount or 0, pe_prec)
        if not rows or pe_unalloc <= 0:
            print("Nothing to do."); return

        total = len(rows)
        print(f"Invoices: {total} | PE unallocated start: {pe_unalloc}")
        if input("Proceed (y/n)? ").strip().lower() != "y":
            return

        processed = 0
        remaining_global = flt(pe_unalloc, ref_prec)

        for bi, block in enumerate(chunks(rows, BLOCK_SIZE), 1):
            if remaining_global <= 0: break

            alloc_rows = []
            local_remaining = remaining_global  # snapshot at block start
            # 2) Build all allocations for this block using DECREASING remaining
            for si in block:
                if local_remaining <= 0: break
                si_out = flt(si.outstanding_amount or 0, ref_prec)
                if si_out <= 0: continue

                alloc = flt(min(local_remaining, si_out), ref_prec)
                if alloc <= 0: continue

                # critical: pass *current* remaining so the guard matches DB expectation
                alloc_rows.append(frappe._dict(
                    voucher_type="Payment Entry",
                    voucher_no=PE,
                    against_voucher_type="Sales Invoice",
                    against_voucher=si["name"],
                    party_type="Customer",
                    party=CUST,
                    account=si["debit_to"],
                    unadjusted_amount=local_remaining,   # validate_allocated_amount checks this
                    unreconciled_amount=local_remaining, # check_if_advance_entry_modified checks this
                    allocated_amount=alloc,
                    due_date=si["due_date"] or si["posting_date"],
                ))
                local_remaining = flt(local_remaining - alloc, ref_prec)

            if not alloc_rows:
                continue

            # 3) Single reconcile + single commit per block
            reconcile_against_document(alloc_rows)
            frappe.db.commit()

            processed += len(alloc_rows)
            remaining_global = local_remaining  # advance the global after success
            print(f"Block {bi}: {len(alloc_rows)} allocations | remaining PE: {remaining_global:.2f}")

            if remaining_global <= 0:
                print("PE exhausted."); break

        print(f"Done. Applied: {processed} allocations. Final remaining: {remaining_global:.2f}")

    finally:
        frappe.destroy()

if __name__ == "__main__":
    main()
