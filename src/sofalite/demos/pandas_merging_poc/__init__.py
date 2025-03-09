"""
TODO: Step 2

Strategy - do the simplest thing first.

Note - when discussing dimensions always reference rows first then columns to avoid confusion.

Step 1) Ignore totals (especially nested totals!) and row / col percentages.
Just (just!) get the data for the table resulting from the intersection
of all the row and column sub-trees.
Step 2) Afterwards, add totals for rows, then totals for columns.
Step 3) Then calculate row and column percentages.
Step 4) Soft-wire so it can be generated from config
Step 5) Integrate into output/tables/cross_tab/get_tbl_html

https://github.com/posit-dev/great-tables
https://stackoverflow.com/questions/44156051/add-a-series-to-existing-dataframe

"""
