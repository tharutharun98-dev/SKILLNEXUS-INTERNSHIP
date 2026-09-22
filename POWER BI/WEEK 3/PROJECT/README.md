# Week 3: DAX Functions & KPI Visuals

**Author:** Tharuna B S
**Internship ID:** _Not listed on offer letter — add your Internship ID here_
**Internship:** Power BI Developer Intern, Skill Nexis
**Date:** 04/09/2026

## Topics Covered
- Calculated Columns & Measures using DAX
- SUMX, AVERAGE, CALCULATE, DIVIDE functions
- Creating KPIs (Key Performance Indicators)
- Using slicers & filters for interactive dashboards

## Assignment
1. Create DAX measures:
   - `Total Sales = SUM(Sales[Sales])`
   - `Total Profit = SUM(Sales[Profit])`
   - `Profit Margin = DIVIDE([Total Profit],[Total Sales])`
2. Build 3 KPI cards: Total Sales, Total Profit, Profit Margin.
3. Add slicers for **Region** and **Year**.
4. Use conditional formatting to highlight negative profits in red.

## Folder Contents
| File | Description |
|---|---|
| `source_code/DAX_Measures.dax` | All DAX measures required for this week |
| `dataset/retail_sales_data.csv` / `.xlsx` | Sample retail sales dataset (Order Date, Region, Category, Sales, Profit, Quantity, Discount) |
| `output/kpi_dashboard_mockup.png` | Placeholder dashboard preview — replace with your real Power BI screenshot |
| `requirements.txt` | Software & setup steps needed to complete this assignment |

## How to Reproduce
See `requirements.txt` for full setup steps. In short: load the dataset into Power BI Desktop, add the measures from `DAX_Measures.dax`, build the 3 KPI cards, add Region/Year slicers, and apply conditional formatting (red for negative profit).
