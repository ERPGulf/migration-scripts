Here’s a ready-to-paste README.md designed for GitHub — clean, formatted, and developer-friendly 👇

⸻


ERPNext Migration Scripts

###Automated migration utilities for ERPNext from legacy ERPs — SAP, Oracle, Dynamics, Tally, and more

---

## 📖 Overview

This repository contains scripts and utilities developed by our **ERPGulf Migration Team** to automate data migration from other ERP systems into **ERPNext**.

These scripts are designed for structured, repeatable, and auditable migrations — covering master data, transactional data, and opening balances.  
Each script is tested in live customer projects and continuously improved for accuracy and performance.

---

## 🚀 Supported Source Systems

| Source ERP | Supported Formats | Description |
|-------------|------------------|--------------|
| **SAP** | CSV, XLSX, OData | Imports GL accounts, Items, Customers, and Balances |
| **Oracle E-Business Suite** | SQL dumps, CSV | Supports COA mapping and vendor/customer migration |
| **Microsoft Dynamics (AX/365)** | API, CSV | Handles inventory, AR/AP, and financials |
| **Tally** | XML, JSON, CSV | Migrates ledgers, vouchers, and stock entries |
| **Custom Systems** | API, CSV | Mappings configurable via JSON/YAML schemas |

---

## 🏗️ Folder Structure

erpnext_migration_scripts/
│
├── README.md                       # Documentation
├── requirements.txt                 # Dependencies
│
├── /common/                         # Shared utilities
│    ├── frappe_connect.py           # ERPNext site connection helpers
│    ├── data_validator.py           # Consistency checks
│    └── mapper.py                   # Field mapping engine
│
├── /sources/                        # Source ERP-specific modules
│    ├── sap_migration/
│    ├── oracle_migration/
│    ├── dynamics_migration/
│    ├── tally_migration/
│    └── custom_migration/
│
├── /templates/                      # Sample mapping files
│    ├── item_mapping.yaml
│    ├── customer_mapping.yaml
│    └── gl_mapping.yaml
│
└── /scripts/                        # Executable importers
├── migrate_items.py
├── migrate_customers.py
├── migrate_gl_entries.py
└── migrate_opening_balances.py

---

## ⚙️ Installation

### Prerequisites
- Python **3.10+**
- ERPNext / Frappe instance (v14 or newer)
- API key or DB access for target ERPNext site
- CSV or SQL exports from your legacy system

### Setup
```bash
# Clone this repository
git clone https://github.com/erpgulf/erpnext_migration_scripts.git
cd erpnext_migration_scripts

# Install required dependencies
pip install -r requirements.txt


⸻

🧩 Configuration

Set up your ERPNext connection in an .env file:

FRAPPE_URL=https://your-erpnext-site.com
FRAPPE_API_KEY=your_api_key
FRAPPE_API_SECRET=your_api_secret

Or edit directly in frappe_connect.py.

⸻

▶️ Usage

Example: migrate items from a CSV extracted from SAP

python scripts/migrate_items.py --source sap --file sap_items.csv

Example: migrate GL entries from Oracle export

python scripts/migrate_gl_entries.py --source oracle --file oracle_gl.csv


⸻

🧪 Features

✅ Schema mapping using YAML or JSON
✅ Automatic validation before insert
✅ Error logging and rollback-safe execution
✅ Compatible with ERPNext REST API or direct DB write
✅ Modular design for new ERP connectors

⸻

🧠 Example Mapping File (YAML)

source_table: SAP_ITEMS
target_doctype: Item
fields:
  ItemCode: item_code
  ItemName: item_name
  Group: item_group
  Price: standard_rate


⸻

👥 Contribution

We welcome contributions from the community and ERPNext partners.
	•	Fork the repo
	•	Create a new branch (feature/add-odoo-migration)
	•	Commit your changes
	•	Submit a Pull Request

⸻

📜 License

This project is released under the MIT License.
You are free to use, modify, and distribute it with attribution.

⸻

🧑‍💻 Maintainers

ERPGulf Migration Team
🌐 www.erpgulf.com
📧 support@erpgulf.com
📦 GitHub: github.com/erpgulf

⸻

“Helping businesses migrate to ERPNext — faster, safer, and smarter.”

---

