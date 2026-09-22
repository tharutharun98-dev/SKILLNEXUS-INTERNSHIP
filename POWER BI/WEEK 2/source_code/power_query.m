// =====================================================================
//  Week 2 – Power Query (M) transformations
//  Project : Data Modeling & Relationships  |  Author : Tharuna B S
//
//  HOW TO USE
//  1. Power BI Desktop -> Home -> Transform data (Power Query Editor)
//  2. Home -> Manage Parameters -> New Parameter
//        Name: FolderPath   Type: Text
//        Current Value: folder holding the CSVs, WITH trailing slash
//        e.g. C:\Users\Tharuna\PowerBI\Week2_Project\dataset\
//  3. Home -> New Source -> Blank Query -> Advanced Editor -> paste ONE
//     query below and rename the query to match its banner. Repeat x4.
//  4. Close & Apply.
//
//  (If you downloaded the real Kaggle Superstore CSV instead, use
//   Get Data -> Text/CSV on that file and adjust column names to match.)
// =====================================================================


// ---------------------------------------------------------------------
//  QUERY 1 : Orders   (fact table)
// ---------------------------------------------------------------------
let
    Source          = Csv.Document(File.Contents(FolderPath & "orders.csv"),
                        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    ChangedTypes    = Table.TransformColumnTypes(PromotedHeaders, {
                        {"OrderID",    type text},
                        {"OrderDate",  type date},
                        {"ShipDate",   type date},
                        {"CustomerID", type text},
                        {"ProductID",  type text},
                        {"RegionID",   type text},
                        {"Quantity",   Int64.Type},
                        {"Discount",   type number},
                        {"ShipMode",   type text}
                      }, "en-US"),

    RemovedBlanks   = Table.SelectRows(ChangedTypes, each [OrderID] <> null and [OrderDate] <> null),
    RemovedDupes    = Table.Distinct(RemovedBlanks),          // removes the 2 duplicate order rows
    TrimmedText     = Table.TransformColumns(RemovedDupes, {
                        {"OrderID",    Text.Trim, type text},
                        {"CustomerID", Text.Trim, type text},
                        {"ProductID",  Text.Trim, type text},
                        {"RegionID",   Text.Trim, type text},
                        {"ShipMode",   Text.Trim, type text}
                      }),

    // --- Data validation column (Week 2 topic: "Data Validation") ---
    // Flags rows where ShipDate is before OrderDate, which is impossible.
    AddedValidation = Table.AddColumn(TrimmedText, "IsValidShipDate",
                        each [ShipDate] >= [OrderDate], type logical)
in
    AddedValidation


// ---------------------------------------------------------------------
//  QUERY 2 : Customers   (dimension table)
// ---------------------------------------------------------------------
let
    Source          = Csv.Document(File.Contents(FolderPath & "customers.csv"),
                        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes    = Table.TransformColumnTypes(PromotedHeaders, {
                        {"CustomerID",   type text},
                        {"CustomerName", type text},
                        {"Segment",      type text},
                        {"State",        type text},
                        {"RegionID",     type text}
                      }),
    RemovedDupes    = Table.Distinct(ChangedTypes, {"CustomerID"})
in
    RemovedDupes


// ---------------------------------------------------------------------
//  QUERY 3 : Products   (dimension table)
// ---------------------------------------------------------------------
let
    Source          = Csv.Document(File.Contents(FolderPath & "products.csv"),
                        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes    = Table.TransformColumnTypes(PromotedHeaders, {
                        {"ProductID",   type text},
                        {"ProductName", type text},
                        {"Category",    type text},
                        {"SubCategory", type text},
                        {"UnitPrice",   Currency.Type},
                        {"UnitCost",    Currency.Type}
                      }, "en-US"),
    RemovedDupes    = Table.Distinct(ChangedTypes, {"ProductID"})
in
    RemovedDupes


// ---------------------------------------------------------------------
//  QUERY 4 : Regions   (dimension table)
// ---------------------------------------------------------------------
let
    Source          = Csv.Document(File.Contents(FolderPath & "regions.csv"),
                        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    ChangedTypes    = Table.TransformColumnTypes(PromotedHeaders, {
                        {"RegionID",   type text},
                        {"RegionName", type text}
                      }),
    RemovedDupes    = Table.Distinct(ChangedTypes, {"RegionID"})
in
    RemovedDupes


// ---------------------------------------------------------------------
//  OPTIONAL – find orphan keys (Data Validation topic)
//  New Blank Query, paste this AFTER the 4 queries above exist.
//  Returns Orders rows whose ProductID has no match in Products
//  (in this dataset it returns exactly 1 row: PRD-999).
// ---------------------------------------------------------------------
// let
//     Merged  = Table.NestedJoin(Orders, {"ProductID"}, Products, {"ProductID"}, "Match", JoinKind.LeftOuter),
//     Orphans = Table.SelectRows(Merged, each Table.IsEmpty([Match]))
// in
//     Orphans
