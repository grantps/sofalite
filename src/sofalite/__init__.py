"""
Top-level package for sofalite.

Big picture architecture of code pipeline:
In short, how we get from config (perhaps from a GUI), and data in a database, to HTML output

We don't want a big pile of spaghetti code, we need structure as we move through the pipeline.
In SOFA (original) the best description is DRYed out macaroni.
Code was written and hacked until it worked. It was basically spaghetti code.
Then parts were pulled out into shorter stretches of code in sub-functions.
So one big tangle of code was pulled into numerous functions (a mass of spaghetti -> lots of macaroni pieces).
But it was still pasta code.
Sometimes functions were to DRY code out (i.e. shared functions were made)
and other times code was just delegated to sub-functions and then sub-sub-functions etc.
It was very difficult to think of the purpose of a function independently of what was calling it.

The new approach is to put logical breaks in the code. And each break should be defined by a data interface.
Instead of a->b->c->...x->y->z
we have GUI -> style config AND intermediate data structure -> output data structure -> HTML
Note - we have an intermediate dc because it follows the most intuitive form based on data extraction not final use.

Internally we still have DRYed out code and delegation but within a comprehensible context.
For example, a data dataclass (dc) might have a method called to_chart_spec or similar.
The role of that function / method within the greater picture is obvious making it less likely
we'll get lost drilling into implementation.

So where exactly do we put the interfaces in the middle of the pipeline from GUI to HTML output?
Broadly speaking the flow is split into data and style, and the main interfaces are dataclasses (dc).
The flow is from config through various standard variables e.g. strings, dicts, and also dataclasses,
through to an HTML string.

                                  | data extraction -> intermediate spec (inc data) dc -> |
GUI / calling code -> design vals |                                                       |  --> output spec dc --> output HTML
                                  | style specs dc + titles + other (show n) etc -------> |

For example - making a Pie Chart:
                                   GUI or directly
                                          |
      ---------------------------------------------------------------
      |                                                              |
      v                                                              v
  Chart design                                            Output / style config
  ------------                                            -----------------------------------------------------
  tbl_name = 'demo_tbl'                                   show_n_records = True     style = 'default'
  tbl_filt_clause = None                                             |              StyleSpec dc
  chart_fld_name = 'country'                                         |              (defined in conf.style)
  chart_fld_lbl = 'Country'                                          |                    from
  category_fld_name = 'browser'                                      |      output.styles.misc.get_style_spec()
  category_fld_lbl = 'Web Browser'                                   |                     |
  chart_vals2lbls = {1: 'Japan', 2: 'Italy',...}                     |                     |
  category_vals2lbls = {'Chrome': 'Google Chrome'}                   |                     |
  category_sort_order = SortOrder.LABEL                              |                     |
              |                                                      |                     |
              v                                                      |                     |
  Intermediate charting spec (including data)                        |                     |
  -------------------------------------------                        |                     |
  ChartCategoryFreqSpecs dc                                          |                     |
  (defined in conf.charts.intermediate.freq_specs)                   |                     |
                 from                                                |                     |
  sql_extraction.charts.freq_specs                                   |                     |
  e.g. get_by_category_chart_spec()                                  |                     |
  takes all the design args as an input                              |                     |
       |                          |                       -----------                      |
       |                          |                      |                                 |
       |                          |                      |                                 |
       v                          v                      |                                 |
 [CategorySpec dc, ...]     [IndivChartSpec dc, ...]     |                                 |
            |                 |                          |                                 |
            |                 |                          |                                 |
            |                 V                          |                                 |
            ------>  PieChartingSpec dc  <---------------                                  |
                     ------------------                                                    |
                     (defined in conf.charts.output.standard)                              |
                              |                                                            |
                              --------------------> HTML str <------------------------------

For example, making a Frequency or CrossTab Table:

                          GUI or directly
                                 |
        ----------------------------------------------------------
        |                                                        |
        v                                                        v
   Table design                                            Output / style config
   ------------                                            ---------------------
   tbl_name = 'demo_tbl'                                   style = 'default'
   tbl_filt_clause = None                                        |
   title = 'Age Group'                                           |
   subtitle = 'Gender'                                           |
                                                                 |
   conf.tables.misc.VarTrees dc                                  |
   conf.tables.misc.Measures dc                                  |
              |                                                  |
              v                                                  |
    Intermediate table spec (including data)                     |
    ----------------------------------------                     |
         CrossTabSpec                                            |
         (defined in conf.tables.intermediate.cross_tab)         |
                                                                 |
            from                                                 |
    sql_extraction.tables.dims                                   |
    e.g. get_cross_tab                                           |
    takes all the design args as an input                        |
              |                                                  |
              v                                                  |
   df made by get_tbl_df()                                       |
   (from conf.tables.output.cross_tab)                           |
              |                                                  |
              --------------------> HTML str <-------------------

Having a clean break between GUI and config makes it easy to swap out to another GUI (e.g. web-based)
or even get user-supplied config directly. The latter is especially convenient when creating unit tests.

Having a clean break at the chart dc to chart HTML point means we could potentially output results in a different way
(different charting engine, or not even as a chart).

The data config to rich data component can be monolithic for convenience.
For histogram bin analyses we need to keep the bins, the data, and the labels tightly coupled
unlike with data where val to label is simply controlled by dictionaries.
The rich data can be full-fat even if it merely passes on / collects some config and makes it available
as part of its output dataclass.

Rich data dc's should have all the methods required to provide the data building blocks needed to make the chart dc

Data-related values should NOT be passed directly to the chart dc but only via the rich data dc.

Pipeline Interface Configuration (sofalite.conf):

* charts
* main tables
* stats

Under each generally data and output although sometimes misc where it doesn't fit anywhere else.
"""
import logging
from sys import stdout

logger = logging.Logger('pysofa')
formatter = logging.Formatter('%(asctime)a %(message)s')

stream_handler = logging.StreamHandler(stream=stdout)
stream_handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)  ## sets level it will pass on to handlers - limits what handlers even know about
stream_handler.setLevel(level=logging.INFO)  ## usually INFO

## overridden on first call to internal cur
SQLITE_DB = {
    'sqlite_default_con': None,
    'sqlite_default_cur': None,
}
