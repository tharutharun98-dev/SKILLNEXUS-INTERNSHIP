// =====================================================================
//  Week 1 – Power Query (M) transformations
//  Project : Sales Dashboard  |  Author : Tharuna B S
//
//  HOW TO USE
//  1. Power BI Desktop  ->  Home  ->  Transform data  (opens Power Query Editor)
//  2. Home -> Manage Parameters -> New Parameter
//        Name: FolderPath   Type: Text
//        Current Value: the folder that holds the CSVs, WITH a trailing slash,
//        e.g.  C:\Users\Tharuna\PowerBI\Week1_Project\dataset\
//  3. Home -> New Source -> Blank Query -> Advanced Editor.
//     Paste ONE query below (everything between the "QUERY" banners) and
//     rename the query to the name shown in the banner. Repeat for all 3.
//  4. Close & Apply.
//
//  (Alternative: Get Data -> Text/CSV for each file and click the same
//   steps in the UI; Power Query writes equivalent M code for you.)
// =====================================================================


// ---------------------------------------------------------------------
//  QUERY 1 : Sales   (fact table)
// ---------------------------------------------------------------------
let
    Source          = Csv.Document(File.Contents(FolderPath & "sales.csv"),
                        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Data types
    ChangedTypes    = Table.TransformColumnTypes(PromotedHeaders, {
                        {"OrderID",    type text},
                        {"OrderDate",  type date},
                        {"CustomerID", type text},
                        {"ProductID",  type text},
                        {"Quantity",   Int64.Type},
                        {"Discount",   type number},
                        {"ShipMode",   type text}
                      }, "en-US"),

    // Cleaning
    RemovedBlanks   = Table.SelectRows(ChangedTypes, each [OrderID] <> null and [OrderDate] <> null),
    RemovedDupes    = Table.Distinct(RemovedBlanks),                      // 8 duplicate rows removed
    TrimmedText     = Table.TransformColumns(RemovedDupes, {
                        {"OrderID",    Text.Trim, type text},
                        {"CustomerID", Text.Trim, type text},
                        {"ProductID",  Text.Trim, type text},
                        {"ShipMode",   Text.Trim, type text}
                      })
in
    TrimmedText


// ---------------------------------------------------------------------
//  QUERY 2 : Products   (dimension table)
// ---------------------------------------------------------------------
let
    Source          = Csv.Document(File.Contents(FolderPath & "products.csv"),
                        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes    = Table.TransformColumnTypes(PromotedHeaders, {
                        {"ProductID",   type text},
                        {"ProductName", type text},
                        {"Category",    type text},
                        {"UnitPrice",   Currency.Type},
                        {"UnitCost",    Currency.Type}
                      }, "en-US"),
    RemovedDupes    = Table.Distinct(ChangedTypes, {"ProductID"})
in
    RemovedDupes


// ---------------------------------------------------------------------
//  QUERY 3 : Customers   (dimension table)
// ---------------------------------------------------------------------
let
    Source          = Csv.Document(File.Contents(FolderPath & "customers.csv"),
                        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes    = Table.TransformColumnTypes(PromotedHeaders, {
                        {"CustomerID",   type text},
                        {"CustomerName", type text},
                        {"Segment",      type text},
                        {"City",         type text},
                        {"State",        type text},
                        {"Region",       type text}
                      }),

    // Fix inconsistent Region text: " West ", "SOUTH", "central"  ->  "West", "South", "Central"
    CleanedRegion   = Table.TransformColumns(ChangedTypes, {
                        {"Region", each Text.Proper(Text.Trim(Text.Clean(_))), type text}
                      }),
    RemovedDupes    = Table.Distinct(CleanedRegion, {"CustomerID"})
in
    RemovedDupes


// ---------------------------------------------------------------------
//  OPTIONAL – Merge example (Data transformation topic: "merging")
//  Use only if you want ONE flat table instead of a star-schema model.
//  Create as a new query that references the three queries above.
// ---------------------------------------------------------------------
// let
//     MergedProducts  = Table.NestedJoin(Sales, {"ProductID"}, Products, {"ProductID"}, "Product", JoinKind.LeftOuter),
//     ExpandedProduct = Table.ExpandTableColumn(MergedProducts, "Product", {"ProductName", "Category", "UnitPrice", "UnitCost"}),
//     MergedCustomers = Table.NestedJoin(ExpandedProduct, {"CustomerID"}, Customers, {"CustomerID"}, "Customer", JoinKind.LeftOuter),
//     ExpandedCust    = Table.ExpandTableColumn(MergedCustomers, "Customer", {"CustomerName", "City", "State", "Region"})
// in
//     ExpandedCust
