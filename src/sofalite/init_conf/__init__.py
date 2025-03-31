"""
A lot of the main conf dataclasses need to run stats calculations to display derived properties.
So they depend on some stats calculations.
Which in turn depend on some special stats interface conf.
So we need an init_conf before conf.

Sometimes from engine and sometimes directly from stats calculation utils.

histo, box -> engine -> conf
     |          |
     |          ------------------------->
     |                                      stats_calc
     ------------------------------------>

It required import-linter to untangle this.
"""