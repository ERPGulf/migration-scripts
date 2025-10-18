import pandas as pd

# Load your CSV file
df = pd.read_csv("/mytmp/SalesInvoiceFinall.csv")

# Count rows where the 'name' field (or invoice ID field) is not empty
invoice_count = df[df["Old Invoice Number"].notna() & (df["Old Invoice Number"] != "")].shape[0]

print("Total Sales Invoices:", invoice_count)

