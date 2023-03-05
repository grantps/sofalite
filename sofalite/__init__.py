"""
Top-level package for sofalite.

Big picture architecture:

dc = dataclass
Sometimes it is best to supply standard args to a function, other times to use a mix of dcs and standard arguments.
A pragmatic thing depending on the number of args and their complexity.

              | DATA ONLY data extraction config --> data extraction --> rich data dc --> |
GUI -> config |                                                                           |  --> chart dc --> chart
              | CHARTING ONLY chart style config dc plus titles etc --------------------> |

Could use another GUI (e.g. web-based) or even get user-supplied config directly

Could output results in a different way (different charting engine, or not even as a chart)

The data config to rich data component can be monolithic for convenience.
For histogram bin analyses we need to keep the bins, the data, and the labels tightly coupled
unlike with data where val to label is simply controlled by dictionaries.
The rich data can be full fat even if it merely passes on / collects some config and makes it available
as part of its output dataclass.

rich data dc should have all the methods required to provide the data building blocks needed to make the chart dc

Data-related values should NOT be passed directly to the chart dc but only via the rich data dc.
"""

import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

__author__ = """Grant Paton-Simpson"""
__email__ = 'grant@sofastatistics.com'
__version__ = '0.1.0'

