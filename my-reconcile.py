#!/usr/bin/env python3
# Ask for PE & Customer, verify relation, show counts/totals, confirm, then reconcile oldest→newest.

import sys
B = "/opt/bench/frappe-bench"
SITES = f"{B}/sites"
sys.path += [f"{B}/apps/frappe", f"{B}/apps/erpnext", B, SITES]

import frappe
from frappe.utils import flt
from erpnext.accounts.utils import reconcile_against_document

SITE = "site01"

# ---- Optional filters (leave empty to ignore) ----
DATE_START, DATE_END = "2025-05-01", "2025-07-29"   # e.g. "2025-05-01", "2025-07-29" or set both to "" to disable
REQUIRE_TYPE = "Retail"                              # e.g. "Retail" or "" to disable
# ---------------------------------------------------

frappe.init(site=SITE, sites_path=SITES)
frappe.connect()
try:
    # Ask for Payment Entry and Customer
    PE = input("Enter Payment Entry number (e.g. PAY202500676): ").strip()
    CUST = input("Enter Customer number (e.g. 12210001): ").strip()

    # Load and validate Payment Entry ↔ Customer relation
    pe = frappe.get_doc("Payment Entry", PE)
    if pe.docstatus != 1:
        raise Exception(f"Payment Entry {PE} is not submitted (docstatus={pe.docstatus}).")
    if pe.party_type != "Customer":
        raise Exception(f"Payment Entry {PE} party_type is {pe.party_type}, expected Customer.")
    if pe.party != CUST:
        raise Exception(f"Payment Entry {PE} is for customer {pe.party}, not {CUST}.")

    # Precisions after connect
    pe_prec  = frappe.get_precision("Payment Entry", "unallocated_amount") or int(frappe.db.get_single_value("System Settings", "currency_precision") or 2)
    ref_prec = frappe.get_precision("Payment Entry Reference", "allocated_amount") or pe_prec

    # Summaries for the PE
    pe_total = flt(pe.received_amount or pe.paid_amount or 0, pe_prec)  # Receive PE usually uses received_amount
    pe_unalloc = flt(pe.unallocated_amount or 0, pe_prec)

    # Build invoice filters
    filters = {"customer": CUST, "docstatus": 1, "outstanding_amount": (">", 0)}
    if DATE_START and DATE_END:
        filters["posting_date"] = ("between", [DATE_START, DATE_END])
    if REQUIRE_TYPE:
        filters["custom_invoice_type"] = REQUIRE_TYPE

    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "debit_to", "outstanding_amount", "due_date", "posting_date"],
        order_by="posting_date asc, name asc",
    )

    # Present summary and ask for confirmation
    print("\n=== Summary ===")
    print(f"Payment Entry: {PE}")
    print(f"Customer:      {CUST}")
    if DATE_START and DATE_END: print(f"Date range:    {DATE_START} → {DATE_END}")
    if REQUIRE_TYPE:            print(f"Type filter:   {REQUIRE_TYPE}")
    print(f"Invoices found: {len(invoices)}")
    print(f"PE total:       {pe_total}")
    print(f"PE unallocated: {pe_unalloc}")
    if len(invoices) == 0 or pe_unalloc <= 0:
        print("Nothing to do (no invoices or no PE balance).")
        sys.exit(0)

    confirm = input("Proceed with reconciliation? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        sys.exit(0)

    # Reconcile oldest → newest until PE runs out
    success = 0
    for si in invoices:
        # Refresh PE balance each loop
        pe_unalloc = flt(frappe.db.get_value("Payment Entry", PE, "unallocated_amount") or 0, pe_prec)
        if pe_unalloc <= 0:
            break

        si_out = flt(si.outstanding_amount or 0, ref_prec)
        if si_out <= 0:
            continue

        # Validators need both fields; allocated must be ≤ both
        unadjusted_amount   = flt(pe_unalloc, ref_prec)  # validate_allocated_amount compares against this
        unreconciled_amount = flt(pe_unalloc, pe_prec)   # check_if_advance_entry_modified compares against this
        alloc               = flt(min(unadjusted_amount, si_out), ref_prec)
        if alloc <= 0:
            continue

        row = frappe._dict(
            voucher_type="Payment Entry",
            voucher_no=PE,
            against_voucher_type="Sales Invoice",
            against_voucher=si.name,
            party_type="Customer",
            party=CUST,
            account=si.debit_to,
            unadjusted_amount=unadjusted_amount,
            unreconciled_amount=unreconciled_amount,
            allocated_amount=alloc,
            due_date=si.due_date or si.posting_date,
        )

        print(f"Alloc {alloc:.2f} → {si.name} (date {si.posting_date}) | PE bal {pe_unalloc:.2f} | SI out {si_out:.2f}")
        reconcile_against_document([row])
        frappe.db.commit()
        success += 1

    final_unalloc = flt(frappe.db.get_value("Payment Entry", PE, "unallocated_amount") or 0, pe_prec)
    print(f"\nDone. Allocations applied: {success}. Final PE unallocated: {final_unalloc:.2f}")

finally:
    frappe.destroy()
