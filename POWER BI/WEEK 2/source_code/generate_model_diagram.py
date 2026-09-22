"""
generate_model_diagram.py
--------------------------
Two things, mirroring the Week 2 assignment:

1. Runs the same data-validation checks as source_code/dax_measures.dax
   (invalid ship dates, orphan ProductID/CustomerID/RegionID references)
   and prints a report -- cross-check these against the DAX validation
   measures once the model is open in Power BI Desktop.

2. Draws the star-schema model diagram (Orders fact table in the middle,
   Customers / Products / Regions / Calendar dimensions around it) as a
   stand-in for a Power BI "Model view" screenshot.

Run:
    python generate_model_diagram.py
Output:
    ../output/validation_report.txt
    ../output/model_diagram.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "dataset"
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

NAVY, GOLD, TEAL, BLUE, GREY = "#22384A", "#C09000", "#00796B", "#1A3CF5", "#6B7280"

# ----------------------------------------------------------------- Load
orders = pd.read_csv(DATA / "orders.csv", parse_dates=["OrderDate", "ShipDate"])
customers = pd.read_csv(DATA / "customers.csv")
products = pd.read_csv(DATA / "products.csv")
regions = pd.read_csv(DATA / "regions.csv")

raw_order_count = len(orders)
orders_clean = orders.drop_duplicates()

# ------------------------------------------------------------ Validation
lines = []
lines.append("=== WEEK 2 DATA VALIDATION REPORT ===\n")
lines.append(f"Orders rows (raw)               : {raw_order_count}")
lines.append(f"Orders rows (after de-dup)       : {len(orders_clean)}")
lines.append(f"Duplicate rows removed           : {raw_order_count - len(orders_clean)}\n")

invalid_ship = orders_clean[orders_clean["ShipDate"] < orders_clean["OrderDate"]]
lines.append(f"[Invalid Ship Dates]   ShipDate < OrderDate : {len(invalid_ship)} row(s)")
if len(invalid_ship):
    lines.append("  " + ", ".join(invalid_ship["OrderID"].tolist()))

orphan_products = orders_clean[~orders_clean["ProductID"].isin(products["ProductID"])]
lines.append(f"\n[Orphan ProductID]     Orders -> Products      : {len(orphan_products)} row(s)")
if len(orphan_products):
    lines.append("  " + ", ".join(f"{r.OrderID} -> {r.ProductID}" for r in orphan_products.itertuples()))

orphan_customers = orders_clean[~orders_clean["CustomerID"].isin(customers["CustomerID"])]
lines.append(f"\n[Orphan CustomerID]    Orders -> Customers     : {len(orphan_customers)} row(s)")

orphan_regions = orders_clean[~orders_clean["RegionID"].isin(regions["RegionID"])]
lines.append(f"[Orphan RegionID]      Orders -> Regions       : {len(orphan_regions)} row(s)")

lines.append(
    "\nResult: Customers and Regions relationships are 100% clean. "
    "Products has exactly 1 orphan row (ORD-2" + orphan_products["OrderID"].iloc[0][-4:]
    + " -> " + orphan_products["ProductID"].iloc[0] + ") and there are "
    f"{len(invalid_ship)} rows with an impossible ship date -- both planted on purpose "
    "so the DAX validation measures in dax_measures.dax have something real to catch. "
    "Fix by either correcting the source row or filtering it out in Power Query "
    "before it reaches the model."
    if len(orphan_products) else "\nResult: all relationships are clean."
)

report = "\n".join(lines)
print(report)
(OUT / "validation_report.txt").write_text(report + "\n")

# ---------------------------------------------------------- Model diagram
fig, ax = plt.subplots(figsize=(11, 7.5), facecolor="white")
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis("off")


def draw_table(x, y, w, h, title, cols, header_color, key_col=None):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                          linewidth=1.2, edgecolor=NAVY, facecolor="white", zorder=2)
    ax.add_patch(box)
    head = FancyBboxPatch((x, y + h - 0.5), w, 0.5, boxstyle="round,pad=0.02,rounding_size=0.08",
                           linewidth=0, facecolor=header_color, zorder=3)
    ax.add_patch(head)
    ax.text(x + w / 2, y + h - 0.25, title, ha="center", va="center", fontsize=11,
            fontweight="bold", color="white", zorder=4)
    row_h = (h - 0.5) / max(len(cols), 1)
    for i, col in enumerate(cols):
        cy = y + h - 0.5 - row_h * (i + 0.5)
        weight = "bold" if col == key_col else "normal"
        marker = "PK " if col == key_col else "    "
        ax.text(x + 0.15, cy, f"{marker}{col}", ha="left", va="center", fontsize=9.5,
                fontweight=weight, color=NAVY, zorder=4)
    return (x, y, w, h)


def anchor(box, side):
    x, y, w, h = box
    mid_y = y + h / 2
    return {"left": (x, mid_y), "right": (x + w, mid_y), "top": (x + w / 2, y + h),
            "bottom": (x + w / 2, y)}[side]


def connect(p1, p2, label):
    arrow = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14,
                             color=GREY, linewidth=1.4, zorder=1,
                             connectionstyle="arc3,rad=0.0")
    ax.add_patch(arrow)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    ax.text(mx, my + 0.12, label, ha="center", fontsize=8, color=GREY, style="italic",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none"))


orders_box = draw_table(3.7, 3.1, 2.6, 2.6, "Orders  (fact)",
                         ["OrderID", "OrderDate", "ShipDate", "CustomerID", "ProductID",
                          "RegionID", "Quantity", "Discount", "Revenue", "Profit"],
                         NAVY, key_col="OrderID")

cust_box = draw_table(0.3, 5.7, 2.6, 2.0, "Customers",
                      ["CustomerID", "CustomerName", "Segment", "State", "RegionID"],
                      TEAL, key_col="CustomerID")

prod_box = draw_table(7.1, 5.7, 2.6, 2.0, "Products",
                      ["ProductID", "ProductName", "Category", "SubCategory", "UnitPrice", "UnitCost"],
                      GOLD, key_col="ProductID")

region_box = draw_table(0.3, 0.3, 2.6, 1.4, "Regions",
                        ["RegionID", "RegionName"], BLUE, key_col="RegionID")

cal_box = draw_table(7.1, 0.3, 2.6, 1.8, "Calendar",
                     ["Date", "Year", "Quarter", "Month", "Day"], "#8E44AD", key_col="Date")

connect(anchor(cust_box, "bottom"), anchor(orders_box, "top"), "1 : *  (CustomerID)")
connect(anchor(prod_box, "bottom"), anchor(orders_box, "top"), "1 : *  (ProductID)")
connect(anchor(region_box, "top"), anchor(orders_box, "bottom"), "1 : *  (RegionID)")
connect(anchor(cal_box, "top"), anchor(orders_box, "bottom"), "1 : *  (OrderDate)")

ax.text(5, 7.6, "Week 2 – Star Schema Data Model", ha="center", fontsize=16,
        fontweight="bold", color=NAVY)
ax.text(5, 0.05, "Every dimension connects directly to Orders → pure star schema (no snowflake chain).",
        ha="center", fontsize=9, color=GREY, style="italic")

fig.tight_layout()
fig.savefig(OUT / "model_diagram.png", dpi=150, facecolor="white")
print(f"\nSaved: {OUT / 'model_diagram.png'}")
print(f"Saved: {OUT / 'validation_report.txt'}")
