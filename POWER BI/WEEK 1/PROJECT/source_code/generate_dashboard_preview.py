"""
generate_dashboard_preview.py
-----------------------------
Re-creates the Week 1 sales dashboard with Python (pandas + matplotlib) so the
numbers can be cross-checked against the Power BI report.

It applies the same cleaning rules as source_code/power_query.m and the same
formulas as source_code/dax_measures.dax:

    Revenue = Quantity * UnitPrice * (1 - Discount)
    Cost    = Quantity * UnitCost
    Profit  = Revenue - Cost

Run:
    python generate_dashboard_preview.py
Output:
    ../output/dashboard_preview.png
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "dataset"
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

# Colour palette (matches the course slide deck)
NAVY, GOLD, TEAL, BLUE, GREY, BG = "#22384A", "#C09000", "#00796B", "#1A3CF5", "#6B7280", "#F3F4F6"

# ----------------------------------------------------------------- Load
sales = pd.read_csv(DATA / "sales.csv", parse_dates=["OrderDate"])
products = pd.read_csv(DATA / "products.csv")
customers = pd.read_csv(DATA / "customers.csv")

# ---------------------------------------------------------------- Clean
sales = sales.drop_duplicates()                                   # Remove Duplicates
customers["Region"] = customers["Region"].str.strip().str.title()  # Trim + Capitalize Each Word

# ---------------------------------------------------------------- Model
df = (
    sales.merge(products, on="ProductID", how="left")
         .merge(customers[["CustomerID", "Region"]], on="CustomerID", how="left")
)
df["Revenue"] = df["Quantity"] * df["UnitPrice"] * (1 - df["Discount"])
df["Cost"] = df["Quantity"] * df["UnitCost"]
df["Profit"] = df["Revenue"] - df["Cost"]

# ------------------------------------------------------------------ KPIs
total_revenue = df["Revenue"].sum()
total_profit = df["Profit"].sum()
total_orders = df["OrderID"].nunique()
margin = total_profit / total_revenue

by_region = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
top5 = df.groupby("ProductName")["Profit"].sum().sort_values(ascending=False).head(5)
monthly = df.set_index("OrderDate")["Revenue"].resample("MS").sum()


def inr(x: float) -> str:
    """Format a rupee amount in lakh / crore for readability."""
    if x >= 1e7:
        return f"₹{x / 1e7:.2f} Cr"
    if x >= 1e5:
        return f"₹{x / 1e5:.2f} L"
    return f"₹{x:,.0f}"


# ---------------------------------------------------------- Print summary
print("=== KPI SUMMARY (cross-check with Power BI) ===")
print(f"Total Revenue : {total_revenue:,.2f}  ({inr(total_revenue)})")
print(f"Total Profit  : {total_profit:,.2f}  ({inr(total_profit)})")
print(f"Total Orders  : {total_orders}")
print(f"Profit Margin : {margin:.2%}")
print("\nRevenue by Region:")
print(by_region.round(2).to_string())
print("\nTop 5 Products by Profit:")
print(top5.round(2).to_string())

# ------------------------------------------------------------------ Plot
plt.rcParams["font.family"] = "DejaVu Sans"
fig = plt.figure(figsize=(16, 9), facecolor="white")
gs = fig.add_gridspec(
    nrows=3, ncols=4, height_ratios=[0.5, 1.0, 1.0], hspace=0.55, wspace=0.35,
    left=0.12, right=0.97, top=0.85, bottom=0.10,
)

# Header
fig.add_artist(Rectangle((0, 0.90), 1, 0.10, transform=fig.transFigure, facecolor=NAVY, edgecolor="none", zorder=0))
fig.text(0.03, 0.945, "Sales Performance Dashboard", color="white", fontsize=24, fontweight="bold", va="center")
fig.text(0.97, 0.945, "Week 1 · Power BI Developer Intern · Skill Nexis", color="#D1D5DB",
         fontsize=11, ha="right", va="center")

# KPI cards
kpis = [
    ("Total Revenue", inr(total_revenue), NAVY),
    ("Total Profit", inr(total_profit), TEAL),
    ("Profit Margin", f"{margin:.1%}", GOLD),
    ("Total Orders", f"{total_orders:,}", BLUE),
]
for i, (label, value, color) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(BG)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axvline(0, color=color, linewidth=10, ymin=0, ymax=1)
    ax.text(0.5, 0.68, label, ha="center", va="center", fontsize=12, color=GREY, transform=ax.transAxes)
    ax.text(0.5, 0.30, value, ha="center", va="center", fontsize=26, fontweight="bold", color=color,
            transform=ax.transAxes)

# Monthly trend (spans two columns) + Sales by Region
ax_trend = fig.add_subplot(gs[1, 0:2])
ax_trend.plot(monthly.index, monthly.values / 1e5, color=BLUE, linewidth=2.5, marker="o", markersize=4)
ax_trend.fill_between(monthly.index, monthly.values / 1e5, color=BLUE, alpha=0.10)
ax_trend.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax_trend.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
ax_trend.set_title("Monthly Revenue Trend (₹ Lakh)", loc="left", fontsize=13, fontweight="bold", color=NAVY)

ax_region = fig.add_subplot(gs[1, 2:4])
bars = ax_region.bar(by_region.index, by_region.values / 1e5, color=[TEAL, NAVY, GOLD, BLUE, GREY][: len(by_region)])
ax_region.set_ylim(0, by_region.max() / 1e5 * 1.12)
ax_region.set_title("Sales by Region (₹ Lakh)", loc="left", fontsize=13, fontweight="bold", color=NAVY)
for b in bars:
    ax_region.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.1f}",
                   ha="center", va="bottom", fontsize=10, color=NAVY)

# Top 5 products (full width, horizontal bars)
ax_top = fig.add_subplot(gs[2, 0:4])
top5_sorted = top5.sort_values()
bars = ax_top.barh(top5_sorted.index, top5_sorted.values / 1e5, color=GOLD)
ax_top.set_title("Top 5 Products by Profit (₹ Lakh)", loc="left", fontsize=13, fontweight="bold", color=NAVY)
for b in bars:
    ax_top.text(b.get_width(), b.get_y() + b.get_height() / 2, f" {b.get_width():.1f}",
                va="center", fontsize=10, color=NAVY)

for ax in (ax_trend, ax_region, ax_top):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#D1D5DB")
    ax.spines["bottom"].set_color("#D1D5DB")
    ax.tick_params(colors=GREY, labelsize=10)
    ax.grid(axis="y" if ax is not ax_top else "x", color="#E5E7EB", linewidth=0.8)
    ax.set_axisbelow(True)
ax_top.set_xlim(0, top5.max() / 1e5 * 1.12)

fig.text(0.5, 0.03,
         "Preview generated with Python from dataset/*.csv – replace with a Power BI Desktop screenshot "
         "(output/powerbi_dashboard.png) once your report is built.",
         ha="center", fontsize=9, color=GREY, style="italic")

fig.savefig(OUT / "dashboard_preview.png", dpi=150, facecolor="white")
print(f"\nSaved: {OUT / 'dashboard_preview.png'}")
