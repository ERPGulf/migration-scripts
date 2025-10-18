#!/bin/bash

SITE="benchui2.erpgulf.com"
DOCTYPE="Sales Invoice"
DIR="/mytmp"
PREFIX="split100_part_"
EXT=".csv"

for i in $(seq 1 100); do
    FILE="$DIR/${PREFIX}${i}${EXT}"
    echo "🧹 Cleaning old Data Import Logs..."
    
    bench --site "$SITE" console <<EOF
import frappe
frappe.db.delete("Data Import Log", {})
frappe.db.commit()
EOF

    echo "🚀 Importing file $i/100: $(basename "$FILE")"
    
    bench --site "$SITE" data-import --doctype "$DOCTYPE" --file "$FILE" --type Insert

    echo "✅ Done with: $(basename "$FILE")"
done

