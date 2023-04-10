"""

<!--css_fils = ["/home/e/Documents/sofastats/css/default.css"]-->

<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.01 Transitional//EN'
'http://www.w3.org/TR/html4/loose.dtd'>
<html>
<head>
<meta http-equiv="P3P" content='CP="IDC DSP COR CURa ADMa OUR IND PHY ONL COM
STA"'>
<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
<title>SOFA Statistics Report 2023-03-25_17:24:22</title>

<style type="text/css">
<!--

body {
    background-color: #ffffff;
}
td, th {
    background-color: white;
}
/*
dojo_style_start
chart_bg = "white"
chart_font_colour = "#423126"
plot_bg = "#f2f1f0"
plot_font_colour = "#423126"
plot_bg_filled = "#f2f1f0"
plot_font_colour_filled = "#423126"
axis_font_colour = "#423126"
major_gridline_colour = "#b8a49e"
gridline_width = 1
stroke_width = 3
tooltip_border_colour = "#736354"
normal_curve_colour = "#423126"
colour_mappings = [
    ("#e95f29", "#ef7d44"),
    ("#f4cb3a", "#f7d858"),
    ("#4495c3", "#62add2"),
    ("#44953a", "#62ad58"),
    ("#f43a3a", "#f75858"),
    ]
connector_style = "defbrown"
dojo_style_end
*/
    body{
        font-size: 12px;
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
    }
    h1, h2{
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
    }
    h1{
        font-size: 18px;
    }
    h2{
        font-size: 16px;
    }
    .gui-msg-medium, gui-msg-small{
        color: #29221c;
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
    }
    .gui-msg-medium{
        font-size: 16px;
    }
    *html .gui-msg-medium{
        font-weight: bold;
        font-size: 18px;
    }
    .gui-msg-small{
        font-size: 13px;
        line-height: 150%;
    }
    .gui-note{
        background-color: #e95829;
        color: white;
        font-weight: bold;
        padding: 2px;
    }
    tr, td, th{
        margin: 0;
    }

    .tbltitle0, .tblsubtitle0{
        margin: 0;
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
        font-size: 14px;
    }
    .tbltitle0{ /*spans*/
        padding: 0;
        font-size: 18px;
    }
    .tblsubtitle0{
        padding: 12px 0px 0px 0px;
        font-size: 14px;
    }
    .tblcelltitle0{ /*th*/
        text-align: left;
        border: none;
        padding: 0px 0px 12px 0px;
        margin: 0;
    }

    th, .rowvar0, .rowval0, .datacell0, .firstdatacell0 {
        border: solid 1px #A1A1A1;
    }
    th{
        margin: 0;
        padding: 0px 6px;
    }
    td{
        padding: 2px 6px;
        border: solid 1px #c0c0c0;
        font-size: 13px;
    }
    .subtable0{
        border-top: solid 3px #c0c0c0;
    }
    .rowval0{
        margin: 0;
    }
    .datacell0, .firstdatacell0{
        text-align: right;
        margin: 0;
    }
    .firstcolvar0, .firstrowvar0, .spaceholder0 {
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
        font-size: 14px;
        color: white;
    }
    .firstcolvar0, .firstrowvar0{
        background-color: #333435;
    }
    .firstrowvar0{
        border-left: solid 1px #333435;
        border-bottom:  solid 1px #333435;
    }
    .topline0{
        border-top: 2px solid #c0c0c0;
    }
    .spaceholder0 {
        background-color: #CCD9D7;
    }
    .firstcolvar0{
        padding: 9px 6px;
        vertical-align: top;
    }
    .rowvar0, .colvar0{
        font-family: Ubuntu, Helvetica, Arial, sans-serif;
        font-weight: bold;
        font-size: 14px;
        color: #333435;
        background-color: white;
    }
    .colvar0{
        padding: 6px 0px;
    }
    .colval0, .measure0{
        font-size: 12px;
        vertical-align: top;
    }
    table {
        border-collapse: collapse;
    }
    tr.total-row0 td{
        font-weight: bold;
        border-top: solid 2px black;
        border-bottom: double 3px black;
    }
    .page-break-before0{
        page-break-before: always;
        border-bottom: none; /*3px dotted #AFAFAF;*/
        width: auto;
        height: 18px;
    }
    td.lbl0{
        text-align: left;
        background-color: #F5F5F5;
    }
    td.right0{
        text-align: right;
    }
    .ftnote-line{
        /* for hr http://www.w3schools.com/TAGS/att_hr_align.asp*/
        width: 300px;
        text-align: left; /* IE and Opera*/
        margin-left: 0; /* Firefox, Chrome, Safari */
    }
    .tbl-header-ftnote0{
        color: white;
    }
    .ftnote{
        color: black;
    }
    /* Tool tip connector arrows */
    .dijitTooltipBelow-defbrown {

	    padding-top: 13px;
    }
    .dijitTooltipAbove-defbrown {

	    padding-bottom: 13px;
    }
    .tundra .dijitTooltipBelow-defbrown .dijitTooltipConnector {

	    top: 0px;
	    left: 3px;
	    background: url("sofastats_report_extras/tooltipConnectorUp-defbrown.png") no-repeat top left !important;
	    width:16px;
	    height:14px;
    }
    .dj_ie .tundra .dijitTooltipBelow-defbrown .dijitTooltipConnector {

	    background-image: url("sofastats_report_extras/tooltipConnectorUp-defbrown.gif") !important;
    }
    .tundra .dijitTooltipAbove-defbrown .dijitTooltipConnector {

	    bottom: 0px;
	    left: 3px;
	    background:url("sofastats_report_extras/tooltipConnectorDown-defbrown.png") no-repeat top left !important;
	    width:16px;
	    height:14px;
    }
    .dj_ie .tundra .dijitTooltipAbove-defbrown .dijitTooltipConnector {
	    background-image: url("sofastats_report_extras/tooltipConnectorDown-defbrown.gif") !important;
    }
    .dj_ie6 .tundra .dijitTooltipAbove-defbrown .dijitTooltipConnector {
	    bottom: -3px;
    }
    .tundra .dijitTooltipLeft-defbrown {
	    padding-right: 14px;
    }
    .dj_ie6 .tundra .dijitTooltipLeft-defbrown {
	    padding-left: 15px;
    }
    .tundra .dijitTooltipLeft-defbrown .dijitTooltipConnector {

	    right: 0px;
	    bottom: 3px;
	    background:url("sofastats_report_extras/tooltipConnectorRight-defbrown.png") no-repeat top left !important;
	    width:16px;
	    height:14px;
    }
    .dj_ie .tundra .dijitTooltipLeft-defbrown .dijitTooltipConnector {
	    background-image: url("sofastats_report_extras/tooltipConnectorRight-defbrown.gif") !important;
    }
    .tundra .dijitTooltipRight-defbrown {
	    padding-left: 14px;
    }
    .tundra .dijitTooltipRight-defbrown .dijitTooltipConnector {

	    left: 0px;
	    bottom: 3px;
	    background:url("sofastats_report_extras/tooltipConnectorLeft-defbrown.png") no-repeat top left !important;
	    width:16px;
	    height:14px;
    }
    .dj_ie .tundra .dijitTooltipRight-defbrown .dijitTooltipConnector {
	    background-image: url("sofastats_report_extras/tooltipConnectorLeft-defbrown.gif") !important;
    }

-->
</style>
</head>
<body class="tundra">





<br><br>
<hr style="clear: both; ">

<p>From sofa_db.demo_tbl on 25/03/2023 at 05:24 PM</p>
<p>All data in table included - no filtering</p>
<!-- _VISUAL_DIVIDER_BEFORE_THIS -->
<table cellspacing='0'><thead><tr><th class='tblcelltitle0'>
<span class='tbltitle0'>
<!-- _TBL_TITLE_START -->
<!-- _TBL_TITLE_END -->
</span>
<span class='tblsubtitle0'>
<!-- _TBL_SUBTITLE_START -->
<!-- _TBL_SUBTITLE_END -->
</span>
</th></tr></thead></table>
<!-- _REPORT_TABLE_START --><table cellspacing='0'>


<thead>
<tr></tr>
<tr><th class='spaceholder0' rowspan='3' colspan='4'>&nbsp;&nbsp;</th><th class='firstcolvar0'   colspan='2' >Gender</th><th class='firstcolvar0'   colspan='15' >Web Browser</th></tr>
<tr><th class='colval0'  >Male</th><th class='colval0'  >Female</th><th class='colval0'   colspan='3' >Google Chrome</th><th class='colval0'   colspan='3' >Firefox</th><th class='colval0'   colspan='3' >Internet Explorer</th><th class='colval0'   colspan='3' >Opera</th><th class='colval0'   colspan='3' >Safari</th></tr>
<tr><th class='measure0'  >Freq</th><th class='measure0'  >Freq</th><th class='measure0'  >Freq</th><th class='measure0'  >Col %</th><th class='measure0'  >Row %</th><th class='measure0'  >Freq</th><th class='measure0'  >Col %</th><th class='measure0'  >Row %</th><th class='measure0'  >Freq</th><th class='measure0'  >Col %</th><th class='measure0'  >Row %</th><th class='measure0'  >Freq</th><th class='measure0'  >Col %</th><th class='measure0'  >Row %</th><th class='measure0'  >Freq</th><th class='measure0'  >Col %</th><th class='measure0'  >Row %</th></tr>
</thead>


<tbody>
<tr><td class='firstrowvar0'  rowspan='15'  >Age Group</td><td class='rowval0'  rowspan='3'  >< 20</td><td class='rowvar0'  rowspan='3'  >Country</td><td class='rowval0'  >Japan</td><td class='firstdatacell0'>37</td><td class='datacell0'>26</td><td class='datacell0'>10</td><td class='datacell0'>16.7%</td><td class='datacell0'>15.9%</td><td class='datacell0'>25</td><td class='datacell0'>22.9%</td><td class='datacell0'>39.7%</td><td class='datacell0'>15</td><td class='datacell0'>21.7%</td><td class='datacell0'>23.8%</td><td class='datacell0'>6</td><td class='datacell0'>15.8%</td><td class='datacell0'>9.5%</td><td class='datacell0'>7</td><td class='datacell0'>21.2%</td><td class='datacell0'>11.1%</td></tr>
<tr><td class='rowval0'  >Italy</td><td class='firstdatacell0'>70</td><td class='datacell0'>71</td><td class='datacell0'>32</td><td class='datacell0'>53.3%</td><td class='datacell0'>22.7%</td><td class='datacell0'>49</td><td class='datacell0'>45.0%</td><td class='datacell0'>34.8%</td><td class='datacell0'>30</td><td class='datacell0'>43.5%</td><td class='datacell0'>21.3%</td><td class='datacell0'>17</td><td class='datacell0'>44.7%</td><td class='datacell0'>12.1%</td><td class='datacell0'>13</td><td class='datacell0'>39.4%</td><td class='datacell0'>9.2%</td></tr>
<tr><td class='rowval0'  >Germany</td><td class='firstdatacell0'>48</td><td class='datacell0'>57</td><td class='datacell0'>18</td><td class='datacell0'>30.0%</td><td class='datacell0'>17.1%</td><td class='datacell0'>35</td><td class='datacell0'>32.1%</td><td class='datacell0'>33.3%</td><td class='datacell0'>24</td><td class='datacell0'>34.8%</td><td class='datacell0'>22.9%</td><td class='datacell0'>15</td><td class='datacell0'>39.5%</td><td class='datacell0'>14.3%</td><td class='datacell0'>13</td><td class='datacell0'>39.4%</td><td class='datacell0'>12.4%</td></tr>
<tr><td class='rowval0'  rowspan='3'  >20-29</td><td class='rowvar0'  rowspan='3'  >Country</td><td class='rowval0'  >Japan</td><td class='firstdatacell0'>38</td><td class='datacell0'>28</td><td class='datacell0'>19</td><td class='datacell0'>43.2%</td><td class='datacell0'>28.8%</td><td class='datacell0'>26</td><td class='datacell0'>35.1%</td><td class='datacell0'>39.4%</td><td class='datacell0'>13</td><td class='datacell0'>48.1%</td><td class='datacell0'>19.7%</td><td class='datacell0'>6</td><td class='datacell0'>31.6%</td><td class='datacell0'>9.1%</td><td class='datacell0'>2</td><td class='datacell0'>8.0%</td><td class='datacell0'>3.0%</td></tr>
<tr><td class='rowval0'  >Italy</td><td class='firstdatacell0'>22</td><td class='datacell0'>32</td><td class='datacell0'>17</td><td class='datacell0'>38.6%</td><td class='datacell0'>31.5%</td><td class='datacell0'>23</td><td class='datacell0'>31.1%</td><td class='datacell0'>42.6%</td><td class='datacell0'>4</td><td class='datacell0'>14.8%</td><td class='datacell0'>7.4%</td><td class='datacell0'>2</td><td class='datacell0'>10.5%</td><td class='datacell0'>3.7%</td><td class='datacell0'>8</td><td class='datacell0'>32.0%</td><td class='datacell0'>14.8%</td></tr>
<tr><td class='rowval0'  >Germany</td><td class='firstdatacell0'>31</td><td class='datacell0'>38</td><td class='datacell0'>8</td><td class='datacell0'>18.2%</td><td class='datacell0'>11.6%</td><td class='datacell0'>25</td><td class='datacell0'>33.8%</td><td class='datacell0'>36.2%</td><td class='datacell0'>10</td><td class='datacell0'>37.0%</td><td class='datacell0'>14.5%</td><td class='datacell0'>11</td><td class='datacell0'>57.9%</td><td class='datacell0'>15.9%</td><td class='datacell0'>15</td><td class='datacell0'>60.0%</td><td class='datacell0'>21.7%</td></tr>
<tr><td class='rowval0'  rowspan='3'  >30-39</td><td class='rowvar0'  rowspan='3'  >Country</td><td class='rowval0'  >Japan</td><td class='firstdatacell0'>36</td><td class='datacell0'>27</td><td class='datacell0'>17</td><td class='datacell0'>39.5%</td><td class='datacell0'>27.0%</td><td class='datacell0'>14</td><td class='datacell0'>25.5%</td><td class='datacell0'>22.2%</td><td class='datacell0'>15</td><td class='datacell0'>38.5%</td><td class='datacell0'>23.8%</td><td class='datacell0'>5</td><td class='datacell0'>35.7%</td><td class='datacell0'>7.9%</td><td class='datacell0'>12</td><td class='datacell0'>48.0%</td><td class='datacell0'>19.0%</td></tr>
<tr><td class='rowval0'  >Italy</td><td class='firstdatacell0'>29</td><td class='datacell0'>24</td><td class='datacell0'>16</td><td class='datacell0'>37.2%</td><td class='datacell0'>30.2%</td><td class='datacell0'>17</td><td class='datacell0'>30.9%</td><td class='datacell0'>32.1%</td><td class='datacell0'>10</td><td class='datacell0'>25.6%</td><td class='datacell0'>18.9%</td><td class='datacell0'>5</td><td class='datacell0'>35.7%</td><td class='datacell0'>9.4%</td><td class='datacell0'>5</td><td class='datacell0'>20.0%</td><td class='datacell0'>9.4%</td></tr>
<tr><td class='rowval0'  >Germany</td><td class='firstdatacell0'>35</td><td class='datacell0'>25</td><td class='datacell0'>10</td><td class='datacell0'>23.3%</td><td class='datacell0'>16.7%</td><td class='datacell0'>24</td><td class='datacell0'>43.6%</td><td class='datacell0'>40.0%</td><td class='datacell0'>14</td><td class='datacell0'>35.9%</td><td class='datacell0'>23.3%</td><td class='datacell0'>4</td><td class='datacell0'>28.6%</td><td class='datacell0'>6.7%</td><td class='datacell0'>8</td><td class='datacell0'>32.0%</td><td class='datacell0'>13.3%</td></tr>
<tr><td class='rowval0'  rowspan='3'  >40-64</td><td class='rowvar0'  rowspan='3'  >Country</td><td class='rowval0'  >Japan</td><td class='firstdatacell0'>58</td><td class='datacell0'>58</td><td class='datacell0'>28</td><td class='datacell0'>31.1%</td><td class='datacell0'>24.1%</td><td class='datacell0'>38</td><td class='datacell0'>28.8%</td><td class='datacell0'>32.8%</td><td class='datacell0'>28</td><td class='datacell0'>31.5%</td><td class='datacell0'>24.1%</td><td class='datacell0'>12</td><td class='datacell0'>35.3%</td><td class='datacell0'>10.3%</td><td class='datacell0'>10</td><td class='datacell0'>22.2%</td><td class='datacell0'>8.6%</td></tr>
<tr><td class='rowval0'  >Italy</td><td class='firstdatacell0'>75</td><td class='datacell0'>60</td><td class='datacell0'>35</td><td class='datacell0'>38.9%</td><td class='datacell0'>25.9%</td><td class='datacell0'>43</td><td class='datacell0'>32.6%</td><td class='datacell0'>31.9%</td><td class='datacell0'>26</td><td class='datacell0'>29.2%</td><td class='datacell0'>19.3%</td><td class='datacell0'>13</td><td class='datacell0'>38.2%</td><td class='datacell0'>9.6%</td><td class='datacell0'>18</td><td class='datacell0'>40.0%</td><td class='datacell0'>13.3%</td></tr>
<tr><td class='rowval0'  >Germany</td><td class='firstdatacell0'>66</td><td class='datacell0'>73</td><td class='datacell0'>27</td><td class='datacell0'>30.0%</td><td class='datacell0'>19.4%</td><td class='datacell0'>51</td><td class='datacell0'>38.6%</td><td class='datacell0'>36.7%</td><td class='datacell0'>35</td><td class='datacell0'>39.3%</td><td class='datacell0'>25.2%</td><td class='datacell0'>9</td><td class='datacell0'>26.5%</td><td class='datacell0'>6.5%</td><td class='datacell0'>17</td><td class='datacell0'>37.8%</td><td class='datacell0'>12.2%</td></tr>
<tr><td class='rowval0'  rowspan='3'  >65+</td><td class='rowvar0'  rowspan='3'  >Country</td><td class='rowval0'  >Japan</td><td class='firstdatacell0'>85</td><td class='datacell0'>73</td><td class='datacell0'>44</td><td class='datacell0'>46.3%</td><td class='datacell0'>27.8%</td><td class='datacell0'>48</td><td class='datacell0'>31.6%</td><td class='datacell0'>30.4%</td><td class='datacell0'>35</td><td class='datacell0'>36.1%</td><td class='datacell0'>22.2%</td><td class='datacell0'>21</td><td class='datacell0'>41.2%</td><td class='datacell0'>13.3%</td><td class='datacell0'>10</td><td class='datacell0'>24.4%</td><td class='datacell0'>6.3%</td></tr>
<tr><td class='rowval0'  >Italy</td><td class='firstdatacell0'>69</td><td class='datacell0'>55</td><td class='datacell0'>21</td><td class='datacell0'>22.1%</td><td class='datacell0'>16.9%</td><td class='datacell0'>49</td><td class='datacell0'>32.2%</td><td class='datacell0'>39.5%</td><td class='datacell0'>31</td><td class='datacell0'>32.0%</td><td class='datacell0'>25.0%</td><td class='datacell0'>11</td><td class='datacell0'>21.6%</td><td class='datacell0'>8.9%</td><td class='datacell0'>12</td><td class='datacell0'>29.3%</td><td class='datacell0'>9.7%</td></tr>
<tr><td class='rowval0'  >Germany</td><td class='firstdatacell0'>70</td><td class='datacell0'>84</td><td class='datacell0'>30</td><td class='datacell0'>31.6%</td><td class='datacell0'>19.5%</td><td class='datacell0'>55</td><td class='datacell0'>36.2%</td><td class='datacell0'>35.7%</td><td class='datacell0'>31</td><td class='datacell0'>32.0%</td><td class='datacell0'>20.1%</td><td class='datacell0'>19</td><td class='datacell0'>37.3%</td><td class='datacell0'>12.3%</td><td class='datacell0'>19</td><td class='datacell0'>46.3%</td><td class='datacell0'>12.3%</td></tr>
</tbody>

</table>
<!--_REPORT_TABLE_END -->
<!-- _ITEM_TITLE_START --><!--Crosstabs_Age Group By Gender And Web Browser--><!-- _SOFASTATS_ITEM_DIVIDER -->



</body></html>

"""
