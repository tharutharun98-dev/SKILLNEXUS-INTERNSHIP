"""
generate_dataset.py
-------------------
Creates the sample sales dataset used in the Week 1 Power BI project.

Star schema:
    sales.csv      (fact table)      - one row per order line
    products.csv   (dimension table) - product, category, unit price, unit cost
    customers.csv  (dimension table) - customer, city, state, region

A few "dirty" records are added ON PURPOSE (duplicate orders, inconsistent
region text) so that the Power Query cleaning step has something to fix.

Run:
    python generate_dataset.py
Output goes to ../dataset/
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_ORDERS = 1000
N_CUSTOMERS = 60
START_DATE = "2025-01-01"
END_DATE = "2026-08-31"

OUT_DIR = Path(__file__).resolve().parent.parent / "dataset"
OUT_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- Products
products = pd.DataFrame(
    [
        # ProductID, ProductName, Category, UnitPrice (INR), UnitCost (INR)
        ("P001", "Laptop",              "Technology",      55000, 43500),
        ("P002", "Smartphone",          "Technology",      28000, 22500),
        ("P003", "Wireless Headphones", "Technology",       4500,  2400),
        ("P004", "Smart Watch",         "Technology",       9500,  5800),
        ("P005", "Tablet",              "Technology",      32000, 25500),
        ("P006", "Office Chair",        "Furniture",        8500,  5000),
        ("P007", "Standing Desk",       "Furniture",       18000, 11500),
        ("P008", "Bookshelf",           "Furniture",        6500,  4400),
        ("P009", "Printer",             "Office Supplies", 12500,  9600),
        ("P010", "Notebook Pack",       "Office Supplies",   450,   210),
        ("P011", "Ink Cartridge",       "Office Supplies",  1800,  1050),
        ("P012", "Desk Lamp",           "Office Supplies",  1600,   750),
    ],
    columns=["ProductID", "ProductName", "Category", "UnitPrice", "UnitCost"],
)

# Relative popularity of each product (drives how often it is ordered)
product_weights = np.array([0.07, 0.10, 0.14, 0.09, 0.05, 0.08, 0.05, 0.06, 0.05, 0.14, 0.09, 0.08])
product_weights = product_weights / product_weights.sum()

# Cheap items are bought in bigger quantities
max_qty = {"P001": 2, "P002": 3, "P003": 5, "P004": 4, "P005": 2, "P006": 4,
           "P007": 2, "P008": 4, "P009": 2, "P010": 10, "P011": 6, "P012": 5}

# --------------------------------------------------------------- Customers
locations = [
    # City, State, Region
    ("Delhi", "Delhi", "North"), ("Chandigarh", "Chandigarh", "North"),
    ("Jaipur", "Rajasthan", "North"), ("Lucknow", "Uttar Pradesh", "North"),
    ("Bengaluru", "Karnataka", "South"), ("Chennai", "Tamil Nadu", "South"),
    ("Hyderabad", "Telangana", "South"), ("Kochi", "Kerala", "South"),
    ("Kolkata", "West Bengal", "East"), ("Bhubaneswar", "Odisha", "East"),
    ("Patna", "Bihar", "East"), ("Guwahati", "Assam", "East"),
    ("Mumbai", "Maharashtra", "West"), ("Pune", "Maharashtra", "West"),
    ("Ahmedabad", "Gujarat", "West"), ("Surat", "Gujarat", "West"),
    ("Bhopal", "Madhya Pradesh", "Central"), ("Indore", "Madhya Pradesh", "Central"),
    ("Nagpur", "Maharashtra", "Central"), ("Raipur", "Chhattisgarh", "Central"),
]
region_share = {"North": 0.20, "South": 0.30, "East": 0.13, "West": 0.27, "Central": 0.10}
loc_weights = np.array([region_share[r] / sum(1 for l in locations if l[2] == r) for _, _, r in locations])
loc_weights = loc_weights / loc_weights.sum()

first = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Karthik", "Rahul", "Siddharth", "Ananya", "Diya",
         "Isha", "Kavya", "Meera", "Neha", "Priya", "Riya", "Sneha", "Tanvi", "Varun", "Nikhil"]
last = ["Sharma", "Verma", "Iyer", "Nair", "Reddy", "Patel", "Gupta", "Singh", "Das", "Mehta",
        "Kumar", "Joshi", "Bose", "Rao", "Menon", "Shetty", "Kapoor", "Chatterjee"]

names = set()
while len(names) < N_CUSTOMERS:
    names.add(f"{rng.choice(first)} {rng.choice(last)}")
names = sorted(names)

loc_idx = rng.choice(len(locations), size=N_CUSTOMERS, p=loc_weights)
customers = pd.DataFrame(
    {
        "CustomerID": [f"C{str(i + 1).zfill(3)}" for i in range(N_CUSTOMERS)],
        "CustomerName": names,
        "Segment": rng.choice(["Consumer", "Corporate", "Home Office"], size=N_CUSTOMERS, p=[0.5, 0.3, 0.2]),
        "City": [locations[i][0] for i in loc_idx],
        "State": [locations[i][1] for i in loc_idx],
        "Region": [locations[i][2] for i in loc_idx],
    }
)

# ------------------------------------------------------------------- Sales
dates = pd.date_range(START_DATE, END_DATE, freq="D")
# mild upward trend + festive-season bump (Oct-Nov)
date_w = np.linspace(0.8, 1.3, len(dates))
date_w = date_w * np.where(dates.month.isin([10, 11]), 1.35, 1.0)
date_w = date_w / date_w.sum()

order_dates = np.sort(rng.choice(dates, size=N_ORDERS, p=date_w))
prod_ids = rng.choice(products["ProductID"], size=N_ORDERS, p=product_weights)

sales = pd.DataFrame(
    {
        "OrderID": [f"ORD-{10001 + i}" for i in range(N_ORDERS)],
        "OrderDate": pd.to_datetime(order_dates).strftime("%Y-%m-%d"),
        "CustomerID": rng.choice(customers["CustomerID"], size=N_ORDERS),
        "ProductID": prod_ids,
        "Quantity": [int(rng.integers(1, max_qty[p] + 1)) for p in prod_ids],
        "Discount": rng.choice([0.0, 0.05, 0.10, 0.15], size=N_ORDERS, p=[0.55, 0.20, 0.15, 0.10]),
        "ShipMode": rng.choice(["Standard", "Express", "Same Day"], size=N_ORDERS, p=[0.6, 0.3, 0.1]),
    }
)

# ------------------------------------------- Deliberately messy records
# 1) duplicate order lines  -> fixed by "Remove Duplicates" in Power Query
dupes = sales.sample(8, random_state=SEED)
sales = pd.concat([sales, dupes], ignore_index=True).sort_values("OrderID", kind="stable").reset_index(drop=True)

# 2) inconsistent region text -> fixed by Trim + Capitalize Each Word
messy_rows = customers.sample(6, random_state=SEED).index
customers.loc[messy_rows[:2], "Region"] = customers.loc[messy_rows[:2], "Region"].str.upper()
customers.loc[messy_rows[2:4], "Region"] = customers.loc[messy_rows[2:4], "Region"].str.lower()
customers.loc[messy_rows[4:], "Region"] = " " + customers.loc[messy_rows[4:], "Region"] + " "

# ------------------------------------------------------------------ Save
products.to_csv(OUT_DIR / "products.csv", index=False)
customers.to_csv(OUT_DIR / "customers.csv", index=False)
sales.to_csv(OUT_DIR / "sales.csv", index=False)

with pd.ExcelWriter(OUT_DIR / "sales_data.xlsx", engine="openpyxl") as writer:
    sales.assign(OrderDate=pd.to_datetime(sales["OrderDate"])).to_excel(writer, sheet_name="Sales", index=False)
    products.to_excel(writer, sheet_name="Products", index=False)
    customers.to_excel(writer, sheet_name="Customers", index=False)
    for ws in writer.book.worksheets:
        for col in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0 for c in col) + 2
            ws.column_dimensions[col[0].column_letter].width = width
        ws.freeze_panes = "A2"

print(f"sales.csv     : {len(sales):>5} rows (incl. 8 intentional duplicates)")
print(f"products.csv  : {len(products):>5} rows")
print(f"customers.csv : {len(customers):>5} rows")
print(f"Saved to      : {OUT_DIR}")
