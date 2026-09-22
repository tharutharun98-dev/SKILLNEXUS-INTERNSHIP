"""
generate_dataset.py
-------------------
Creates the Week 2 sample dataset: a Superstore-style star schema with
FOUR tables, matching the assignment's required relationships:

    Orders    (fact table)      -> CustomerID, ProductID, RegionID
    Customers (dimension table) -> CustomerID
    Products  (dimension table) -> ProductID
    Regions   (dimension table) -> RegionID

The Kaggle "Superstore" dataset the assignment links to needs a Kaggle
login to download, so this script builds an equivalent dataset offline,
same shape and column intent, ready to import straight into Power BI.

A few issues are added ON PURPOSE so the "Data Validation" topic has
something to check for:
    - a handful of Orders rows with an OrderDate BEFORE ShipDate is fine,
      but a few rows are added with ShipDate < OrderDate (invalid) to
      practice validation
    - one Orders row references a ProductID that does not exist in
      Products (orphan key) to practice relationship / validation checks

Run:
    python generate_dataset.py
Output goes to ../dataset/
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 7
N_ORDERS = 1200
N_CUSTOMERS = 80
START_DATE = "2024-01-01"
END_DATE = "2026-08-31"

OUT_DIR = Path(__file__).resolve().parent.parent / "dataset"
OUT_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(SEED)

# ----------------------------------------------------------------- Regions
regions = pd.DataFrame(
    {
        "RegionID": ["R01", "R02", "R03", "R04", "R05"],
        "RegionName": ["North", "South", "East", "West", "Central"],
    }
)
region_states = {
    "North": ["Delhi", "Punjab", "Haryana", "Rajasthan", "Uttar Pradesh"],
    "South": ["Karnataka", "Tamil Nadu", "Telangana", "Kerala", "Andhra Pradesh"],
    "East": ["West Bengal", "Odisha", "Bihar", "Assam", "Jharkhand"],
    "West": ["Maharashtra", "Gujarat", "Goa", "Rajasthan"],
    "Central": ["Madhya Pradesh", "Chhattisgarh"],
}

# ---------------------------------------------------------------- Products
products = pd.DataFrame(
    [
        ("PRD-001", "Laptop",              "Technology",       "Computers",       55000, 43500),
        ("PRD-002", "Smartphone",          "Technology",       "Phones",          28000, 22500),
        ("PRD-003", "Wireless Headphones", "Technology",       "Accessories",      4500,  2400),
        ("PRD-004", "Smart Watch",         "Technology",       "Accessories",      9500,  5800),
        ("PRD-005", "Tablet",              "Technology",       "Computers",       32000, 25500),
        ("PRD-006", "Office Chair",        "Furniture",        "Chairs",           8500,  5000),
        ("PRD-007", "Standing Desk",       "Furniture",        "Tables",          18000, 11500),
        ("PRD-008", "Bookshelf",           "Furniture",        "Storage",          6500,  4400),
        ("PRD-009", "Printer",             "Office Supplies",  "Machines",        12500,  9600),
        ("PRD-010", "Notebook Pack",       "Office Supplies",  "Paper",             450,   210),
        ("PRD-011", "Ink Cartridge",       "Office Supplies",  "Supplies",         1800,  1050),
        ("PRD-012", "Desk Lamp",           "Office Supplies",  "Furnishings",      1600,   750),
    ],
    columns=["ProductID", "ProductName", "Category", "SubCategory", "UnitPrice", "UnitCost"],
)
product_weights = np.array([0.07, 0.10, 0.14, 0.09, 0.05, 0.08, 0.05, 0.06, 0.05, 0.14, 0.09, 0.08])
product_weights = product_weights / product_weights.sum()
max_qty = {"PRD-001": 2, "PRD-002": 3, "PRD-003": 5, "PRD-004": 4, "PRD-005": 2, "PRD-006": 4,
           "PRD-007": 2, "PRD-008": 4, "PRD-009": 2, "PRD-010": 10, "PRD-011": 6, "PRD-012": 5}

# --------------------------------------------------------------- Customers
first = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Karthik", "Rahul", "Siddharth", "Ananya", "Diya",
         "Isha", "Kavya", "Meera", "Neha", "Priya", "Riya", "Sneha", "Tanvi", "Varun", "Nikhil"]
last = ["Sharma", "Verma", "Iyer", "Nair", "Reddy", "Patel", "Gupta", "Singh", "Das", "Mehta",
        "Kumar", "Joshi", "Bose", "Rao", "Menon", "Shetty", "Kapoor", "Chatterjee"]

names = set()
while len(names) < N_CUSTOMERS:
    names.add(f"{rng.choice(first)} {rng.choice(last)}")
names = sorted(names)

region_share = {"North": 0.20, "South": 0.30, "East": 0.15, "West": 0.25, "Central": 0.10}
cust_region = rng.choice(regions["RegionName"], size=N_CUSTOMERS, p=list(region_share.values()))
cust_state = [rng.choice(region_states[r]) for r in cust_region]

customers = pd.DataFrame(
    {
        "CustomerID": [f"CUST-{str(i + 1).zfill(3)}" for i in range(N_CUSTOMERS)],
        "CustomerName": names,
        "Segment": rng.choice(["Consumer", "Corporate", "Home Office"], size=N_CUSTOMERS, p=[0.5, 0.3, 0.2]),
        "State": cust_state,
        "RegionName": cust_region,   # kept for reference/validation only - NOT used as the model relationship
    }
)
customers = customers.merge(regions, on="RegionName", how="left").drop(columns=["RegionName"])

# ------------------------------------------------------------------- Orders
dates = pd.date_range(START_DATE, END_DATE, freq="D")
date_w = np.linspace(0.8, 1.3, len(dates))
date_w = date_w * np.where(dates.month.isin([10, 11]), 1.35, 1.0)
date_w = date_w / date_w.sum()

order_dates = np.sort(rng.choice(dates, size=N_ORDERS, p=date_w))
prod_ids = rng.choice(products["ProductID"], size=N_ORDERS, p=product_weights)
cust_ids = rng.choice(customers["CustomerID"], size=N_ORDERS)
cust_region_map = customers.set_index("CustomerID")["RegionID"]
region_ids = cust_region_map.loc[cust_ids].values   # order ships from the customer's own region

ship_days = rng.integers(1, 7, size=N_ORDERS)
order_dates_dt = pd.to_datetime(order_dates)
ship_dates = order_dates_dt + pd.to_timedelta(ship_days, unit="D")

orders = pd.DataFrame(
    {
        "OrderID": [f"ORD-{20001 + i}" for i in range(N_ORDERS)],
        "OrderDate": order_dates_dt.strftime("%Y-%m-%d"),
        "ShipDate": ship_dates.strftime("%Y-%m-%d"),
        "CustomerID": cust_ids,
        "ProductID": prod_ids,
        "RegionID": region_ids,
        "Quantity": [int(rng.integers(1, max_qty[p] + 1)) for p in prod_ids],
        "Discount": rng.choice([0.0, 0.05, 0.10, 0.15], size=N_ORDERS, p=[0.55, 0.20, 0.15, 0.10]),
        "ShipMode": rng.choice(["Standard", "Express", "Same Day"], size=N_ORDERS, p=[0.6, 0.3, 0.1]),
    }
)

# --------------------------------------------- Deliberate data-quality issues
# 1) A few rows with ShipDate BEFORE OrderDate -> invalid, to practice validation
bad_idx = orders.sample(4, random_state=SEED).index
orders.loc[bad_idx, "ShipDate"] = (
    pd.to_datetime(orders.loc[bad_idx, "OrderDate"]) - pd.Timedelta(days=2)
).dt.strftime("%Y-%m-%d")

# 2) One order referencing a ProductID that doesn't exist -> orphan key
orders.loc[orders.index[-1], "ProductID"] = "PRD-999"

# 3) A couple of duplicate order rows -> practice Remove Duplicates
dupes = orders.iloc[[10, 250]]
orders = pd.concat([orders, dupes], ignore_index=True).sort_values("OrderID", kind="stable").reset_index(drop=True)

# ------------------------------------------------------------------ Save
orders.to_csv(OUT_DIR / "orders.csv", index=False)
customers.to_csv(OUT_DIR / "customers.csv", index=False)
products.to_csv(OUT_DIR / "products.csv", index=False)
regions.to_csv(OUT_DIR / "regions.csv", index=False)

with pd.ExcelWriter(OUT_DIR / "superstore_data.xlsx", engine="openpyxl") as writer:
    orders.assign(
        OrderDate=pd.to_datetime(orders["OrderDate"]),
        ShipDate=pd.to_datetime(orders["ShipDate"]),
    ).to_excel(writer, sheet_name="Orders", index=False)
    customers.to_excel(writer, sheet_name="Customers", index=False)
    products.to_excel(writer, sheet_name="Products", index=False)
    regions.to_excel(writer, sheet_name="Regions", index=False)
    for ws in writer.book.worksheets:
        for col in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0 for c in col) + 2
            ws.column_dimensions[col[0].column_letter].width = width
        ws.freeze_panes = "A2"

print(f"orders.csv    : {len(orders):>5} rows (incl. 2 duplicates, 4 bad ship dates, 1 orphan ProductID)")
print(f"customers.csv : {len(customers):>5} rows")
print(f"products.csv  : {len(products):>5} rows")
print(f"regions.csv   : {len(regions):>5} rows")
print(f"Saved to      : {OUT_DIR}")
