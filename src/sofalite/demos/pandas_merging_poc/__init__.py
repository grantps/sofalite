"""
TODO: Step 2

Strategy - do the simplest thing first.

Note - when discussing dimensions always reference rows first then columns to avoid confusion.

Step 1) Ignore totals (especially nested totals!) and row / col percentages.
Just (just!) get the data for the table resulting from the intersection
of all the row and column sub-trees.
Step 2) Afterwards, add totals for rows, then totals for columns.
Step 3) Then calculate row and column percentages.
Step 4) Simplify output/tables/cross_tab/get_tbl_df so accepts a raw df rather than the data to which we add the multi-indexes.

TODO: what about the order of columns and rows e.b. by label, by value etc?
"""
