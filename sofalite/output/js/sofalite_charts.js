//Details on ticks etc http://www.ibm.com/developerworks/web/library/wa-moredojocharts/

// BAR ***************************************************************************************
makeBarChart = function(chartname, series, conf){
    nChart = conf["n_records"];
    nChartFontColour = conf["plot_font_colour"]
    /*chartwide function setting - have access to val.element (Column), val.index (0), val.run.data (y_vals), shape, x, y, chart, plot, hAxis, eventMask, type, event
    val.run has chart, group, htmlElements, dirty, stroke, fill, plot, data, dyn, name
    val.run = val.run.chart.series[0]
    val.run.chart has margins, stroke, fill, delayInMs, theme, axes, stack, plots, series, runs, dirty,coords,node,surface,dim,offsets,plotArea AND any other variables I put in with the options - the third parameter of addSeries().
    val.run.data has 0,1,2,3,4 etc such that val.run.data[0] is the y-val for the first item  */
    var getTooltip = function(val){
        var tip = val.run.yLbls[val.index];
        return tip;
    };
    var dc = dojox.charting;
    var mychart = new dc.Chart2D(
        chartname,
        {margins:
            {l: conf["left_margin_offset"],
             t: 10,
             r: 10,
             b: 10+conf["axis_lbl_drop"]},
        yTitleOffset: conf["y_title_offset"]});
    var sofa_theme = new dc.Theme({
        chart:{
	        stroke: null,
        	fill: conf["chart_bg_colour"],
	        pageStyle: null // suggested page style as an object suitable for dojo.style()
	    },
	    plotarea:{
	        stroke: null,
	        fill: conf["plot_bg_colour"]
	    },
	    axis:{
	        stroke:	{ // the axis itself
	            color: null,
	            width: null
	        },
            tick: {	// used as a foundation for all ticks
	            color:     conf["axis_font_colour"],
	            position:  "center",
	            fontColor: conf["axis_font_colour"]
	        },
	        majorTick:	{ // major ticks on axis, and used for major gridlines
	            width:  conf["grid_line_width"],
	            length: 6, 
                color: conf["major_grid_line_colour"]
	        },
	        minorTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.8,
	            length: 3
	        },
	        microTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.5,
	            length: 1
	        }
	    }
    });

    mychart.setTheme(sofa_theme);
    mychart.addAxis("x",
        {title: conf["x_title"],
         labels: conf["x_axis_lbls"],
         minorTicks: conf["has_minor_ticks"], 
         font: "normal normal normal " + conf["x_font_size"] + "pt Arial",
         rotation: conf["axis_lbl_rotate"]
    });
    mychart.addAxis("y",
       {title: conf["y_title"],
        vertical: true,
        includeZero: true, 
        max: conf["y_max"],
        font: "normal normal normal 10pt Arial",
        fontWeight: 12
    });
    mychart.addPlot("grid",
        {type: "Grid",
         hMajorLines: true,
         hMinorLines: false,
         vMajorLines: false,
         vMinorLines: false }
    );
    mychart.addPlot("default",
        {type: "ClusteredColumns",
         gap: conf["x_gap"],
         shadows: {dx: 12, dy: 12}}
    );
    var i
    for (i in series){
        mychart.addSeries(series[i]["lbl"], series[i]["vals"], series[i]["options"]);
    }
    var anim_a = new dc.action2d.Highlight(mychart, "default", {
        highlight: conf["highlight"],
        duration: 450,
        easing:   dojo.fx.easing.sineOut
    });
    var anim_b = new dc.action2d.Shake(mychart, "default");
    var anim_c = new dc.action2d.Tooltip(mychart, "default", {text: getTooltip, 
        tooltipBorderColour: conf["tooltip_border_colour"],
        connectorStyle: conf["connector_style"]});
    mychart.render();
    var legend = new dojox.charting.widget.Legend({chart: mychart, horizontal: 6}, "legend_for_" + chartname);
}

// PIE ***************************************************************************************
makePieChart = function(chartname, slices, conf){
    nChartFontColour = conf["plot_font_colour_filled"]
    nChart = conf["n_records"];
    var pieStroke = "#8b9b98";
    var dc = dojox.charting;
    var mychart = new dc.Chart2D(chartname);
    var sofa_theme = new dc.Theme({
		colors: conf["slice_colours"],
        chart: {
	        stroke: null,
        	fill: null,
	        pageStyle: null // suggested page style as an object suitable for dojo.style()
	    },
		plotarea: {
			fill: conf["plot_bg_colour_filled"]
		},
	    axis:{
	        stroke:	{ // the axis itself
	            color: null,
	            width: null
	        }
	    }
    });
    mychart.setTheme(sofa_theme);
    mychart.addPlot("default", {
            type: "Pie",
            font: "normal normal " + conf["slice_font_size"] + "px Arial",
            fontColor: conf["plot_font_colour_filled"],
            labelOffset: conf['lbl_offset'],
            radius: conf['radius']
        });

    var pieSeries = Array();
    var i;
    for (i in slices){
        pieSeries[i] = 
        {
            y: slices[i]["val"],
            text: slices[i]["lbl"],
            stroke: pieStroke,
            tooltip: slices[i]["tooltip"]
        }
    }
    mychart.addSeries("Series A", pieSeries);
    var anim_a = new dc.action2d.MoveSlice(mychart, "default");
    var anim_b = new dc.action2d.Highlight(mychart, "default", {
        highlight: conf["highlight"],
        duration: 450,
        easing:   dojo.fx.easing.sineOut
    });
    var anim_c = new dc.action2d.Tooltip(mychart, "default", 
        {tooltipBorderColour: conf['tooltip_border_colour'],
         connectorStyle: conf['connector_style']});
    mychart.render();
}

function zeropad_date(num){
    if (num < 10) {
        return "0" + num
    } else {
        return num
    }   
}

// A single parameter function to get labels from epoch milliseconds
function labelfTime(o)
{
   var dt = new Date();
   dt.setTime(o);
   var d = dt.getFullYear() + "-" + zeropad_date(dt.getMonth()+1) + "-" + zeropad_date(dt.getDate());
   //console.log(o+"="+d);
   return d;
}

// LINE ***************************************************************************************
makeLineChart = function(chartname, series, conf){
    nChartFontColour = conf["plot_font_colour"]
    nChart = conf["n_records"];
    var getTooltip = function(val){
        var tip = val.run.yLbls[val.index];
        return tip;
    };
    var dc = dojox.charting;
    var mychart = new dc.Chart2D(chartname,
        {margins: {
            l: conf['left_margin_offset'],
            t: 10,
            r: 10,
            b: 10+conf['axis_lbl_drop']},
            yTitleOffset: conf['y_title_offset']});
    var sofa_theme = new dc.Theme({
        chart:{
	        stroke: null,
        	fill: conf["chart_bg_colour"],
	        pageStyle: null // suggested page style as an object suitable for dojo.style()
	    },
	    plotarea:{
	        stroke: null,
	        fill: conf["plot_bg_colour"]
	    },
	    axis:{
	        stroke:	{ // the axis itself
	            color: null,
	            width: null
	        },
            tick: {	// used as a foundation for all ticks
	            color:     conf["axis_font_colour"],
	            position:  "center",
	            fontColor: conf["axis_font_colour"]
	        },
	        majorTick:	{ // major ticks on axis, and used for major gridlines
	            width:  conf['grid_line_width'],
	            length: 6, 
                color: conf["major_grid_line_colour"]
	        },
	        minorTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  2,
	            length: 4,
                color: conf["major_grid_line_colour"]
	        },
	        microTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  1.7,
	            length: 3,
                color: null
	        }
	    }
    });
    mychart.setTheme(sofa_theme);
    // x-axis
    var xaxis_conf = {
        title: conf['x_title'],
        font: "normal normal normal " + conf["x_font_size"] + "pt Arial",
        rotation: conf['axis_lbl_rotate'],
        minorTicks: conf['has_minor_ticks'],
        microTicks: conf['has_micro_ticks'],
        minorLabels: conf['has_minor_ticks']
    };
    if (conf['is_time_series']) {
        xaxis_conf.labelFunc = labelfTime;
    } else {
        xaxis_conf.labels = conf["x_axis_lbls"];
    };
    mychart.addAxis("x", xaxis_conf);
    // y-axis
    mychart.addAxis("y", {title: conf['y_title'],
                    vertical: true, includeZero: true, 
                    max: conf["y_max"],
                    font: "normal normal normal 10pt Arial", fontWeight: 12
    });
    mychart.addPlot("default", {type: "Lines", markers: true, shadows: {dx: 2, dy: 2, dw: 2}});
    mychart.addPlot("unmarked", {type: "Lines", markers: false});
    mychart.addPlot("curved", {type: "Lines", markers: false, tension: "S"});
    mychart.addPlot("grid", {type: "Grid", vMajorLines: false});
    var i
    for (i in series){
        mychart.addSeries(series[i]["lbl"], series[i]["vals"], series[i]["options"]);
    }
    var anim_a = new dc.action2d.Magnify(mychart, "default");
    var anim_b = new dc.action2d.Tooltip(mychart, "default", {text: getTooltip, 
        tooltipBorderColour: conf['tooltip_border_colour'], connectorStyle: conf['connector_style']});
    mychart.render();
    var legend = new dojox.charting.widget.Legend({chart: mychart}, "legend_for_" + chartname);
}

// AREA ***************************************************************************************
makeAreaChart = function(chartname, series, conf){
    nChartFontColour = conf["plot_font_colour"]
    nChart = conf["n_records"];
    var getTooltip = function(val){
        var tip = val.run.yLbls[val.index];
        return tip;
    };
    var dc = dojox.charting;
    var mychart = new dc.Chart2D(chartname,
        {margins: {
            l: conf['left_margin_offset'],
            t: 10,
            r: 10,
            b: 10+conf['axis_lbl_drop']},
        yTitleOffset: conf['y_title_offset']});
    var sofa_theme = new dc.Theme({
        chart:{
	        stroke: null,
        	fill: null,
	        pageStyle: null // suggested page style as an object suitable for dojo.style()
	    },
	    plotarea:{
	        stroke: null,
	        fill: conf["plot_bg_colour"]
	    },
	    axis:{
	        stroke:	{ // the axis itself
	            color: null,
	            width: null
	        },
            tick: {	// used as a foundation for all ticks
	            color:     conf["axis_font_colour"],
	            position:  "center",
	            fontColor: conf["axis_font_colour"]
	        },
	        majorTick:	{ // major ticks on axis, and used for major gridlines
	            width:  conf['gridline_width'],
	            length: 6, 
                color: conf["major_grid_line_colour"]
	        },
	        minorTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  2,
	            length: 4,
                color: conf["major_grid_line_colour"]
	        },
	        microTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  1.7,
	            length: 3,
                color: "black"
	        }
	    }
    });
    mychart.setTheme(sofa_theme);
    // x-axis
    var xaxis_conf = {
        title: conf['x_title'],
        font: "normal normal normal " + conf["x_font_size"] + "pt Arial",
        rotation: conf['axis_lbl_rotate'],
        minorTicks: conf['has_minor_ticks'],
        microTicks: conf['has_micro_ticks'],
        minorLabels: conf['has_minor_ticks']
    };
    if (conf['time_series']) {
        xaxis_conf.labelFunc = labelfTime;
    } else {
        xaxis_conf.labels = conf["x_axis_lbls"];
    };
    mychart.addAxis("x", xaxis_conf);
    // y-axis
    mychart.addAxis("y", {title: conf['y_title'],  // normal normal bold
                    vertical: true, includeZero: true, 
                    max: conf["y_max"], 
                    font: "normal normal normal 10pt Arial", fontWeight: 12
    });
    mychart.addPlot("default", {type: "Areas", lines: true, areas: true, markers: true});
    mychart.addPlot("unmarked", {type: "Areas", lines: true, areas: true, markers: false});
    mychart.addPlot("grid", {type: "Grid", vMajorLines: false});
    var i
    for (i in series){
        mychart.addSeries(series[i]["lbl"], series[i]["vals"], series[i]["options"]);
    }
    var anim_a = new dc.action2d.Magnify(mychart, "default");
    var anim_b = new dc.action2d.Tooltip(mychart, "default",
        {text: getTooltip, 
         tooltipBorderColour: conf['tooltip_border_colour'],
         connectorStyle: conf['connector_style']});
    mychart.render();
}

// HISTOGRAM ***************************************************************************************
makeHistogram = function(chartname, data_spec, conf){
    nChartFontColour = conf["plot_font_colour"]
    nChart = conf["n_records"];
    // chartwide function setting - have access to val.element (Column), val.index (0), val.run.data (y_vals)
    var getTooltip = function(val){
        return "Values: " + data_spec["bin_lbls"][val.index] + "<br>" + conf['y_title'] + ": " + val.y;
    };
    var dc = dojox.charting;
    var mychart = new dc.Chart2D(chartname,
       {margins: {
            l: conf['left_margin_offset'],
            t: 10,
            r: 10,
            b: 10},
        yTitleOffset: conf['y_title_offset']});

    var sofa_theme = new dc.Theme({
        chart:{
	        stroke: null,
            fill: null,  //conf["chart_bg"],
	        pageStyle: null // suggested page style as an object suitable for dojo.style()
	    },
	    plotarea:{
	        stroke: null,
	        fill: conf["plot_bg_colour"]
	    },
	    axis:{
	        stroke:	{ // the axis itself
	            color: null,
	            width: null
	        },
            tick: {	// used as a foundation for all ticks
	            color:     conf["axis_font_colour"],
	            position:  "center",
	            fontColor: conf["axis_font_colour"]
	        },
	        majorTick:	{ // major ticks on axis, and used for major gridlines
	            width:  conf['grid_line_width'],
	            length: 6, 
                color: conf["major_grid_line_colour"]
	        },
	        minorTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.8,
	            length: 3
	        },
	        microTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.5,
	            length: 1
	        }
	    }
    });
    mychart.setTheme(sofa_theme);
    mychart.addAxis("x", {title: data_spec["series_lbl"],
                    labels: conf["blank_x_axis_lbls"], minorTicks: false, microTicks: false,
                    font: "normal normal normal " + conf["x_axis_font_size"] + "pt Arial"
    });
    mychart.addAxis("x2", {
        min: conf["min_x_val"],
        max: conf["max_x_val"],
        minorTicks: conf['has_minor_ticks'], 
        font: "normal normal normal " + conf["x_axis_font_size"] + "pt Arial"
    });
    mychart.addAxis("y", {title: conf['y_title'],  // normal normal bold
                    vertical: true, includeZero: true, font: "normal normal normal 10pt Arial", fontWeight: 12
    });
    mychart.addPlot("normal", {type: "Lines", markers: true, shadows: {dx: 2, dy: 2, dw: 2}}); // must come first to be seen!
    mychart.addPlot("default", {type: "Columns", gap: 0, shadows: {dx: 12, dy: 12}});
    mychart.addPlot("grid", {type: "Grid", vMajorLines: false});
    mychart.addPlot("othergrid", {type: "Areas", hAxis: "x2", vAxis: "y"});
    mychart.addSeries(data_spec["series_lbl"], data_spec["y_vals"], data_spec["style"]);
    if(conf['show_normal_curve'] == true){
        mychart.addPlot("normal", {type: "Lines", markers: false, shadows: {dx: 2, dy: 2, dw: 2}});
        mychart.addSeries("Normal Dist Curve", data_spec["norm_y_vals"], data_spec["norm_style"]);
    }
    var anim_a = new dc.action2d.Highlight(mychart, "default", {
        highlight: conf["highlight"],
        duration: 450,
        easing:   dojo.fx.easing.sineOut
    });
    var anim_b = new dc.action2d.Shake(mychart, "default");
    var anim_c = new dc.action2d.Tooltip(
        mychart,
        "default",
        {text: getTooltip, 
         tooltipBorderColour: conf['tooltip_border_colour'],
         connectorStyle: conf['connector_style']});
    mychart.render();
}

// SCATTERPLOT ***************************************************************************************
makeScatterplot = function(chartname, series, conf){
    nChartFontColour = conf["plot_font_colour_filled"]
    nChart = conf["n_chart"];
    // chartwide function setting - have access to val.element (Column), val.index (0), val.run.data (y_vals)
    var getTooltip = function(val){
        return "(x: " + val.x + ", y: " + val.y + ")";
    };
    var dc = dojox.charting;
    var mychart = new dc.Chart2D(
        chartname,
        {margins:
            {l: conf['margin_offset_l'],
             t: 10,
             r: 10,
             b: 10+conf['axis_lbl_drop']},
         yTitleOffset: conf['y_title_offset']});
    var sofa_theme = new dc.Theme({
        chart:{
	        stroke: null,
        	fill: conf['chart_bg'],
	        pageStyle: null // suggested page style as an object suitable for dojo.style()
	    },
	    plotarea:{
	        stroke: null,
	        fill: conf["plot_bg"]
	    },
	    axis:{
	        stroke:	{ // the axis itself
	            color: null,
	            width: null
	        },
            tick: {	// used as a foundation for all ticks
	            color:     conf["axis_font_colour"],
	            position:  "center",
	            fontColor: conf["axis_font_colour"]
	        },
	        majorTick:	{ // major ticks on axis, and used for major gridlines
	            width:  conf["gridline_width"],
	            length: 6, 
                color: conf["major_gridline_colour"]
	        },
	        minorTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.8,
	            length: 3
	        },
	        microTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.5,
	            length: 1
	        }
	    }
    });
    mychart.setTheme(sofa_theme);
    mychart.addAxis("x", {title: conf['x_title'],
                    min: conf["xmin"], max: conf["xmax"],
                    minorTicks: conf['has_minor_ticks'], microTicks: false,
                    font: "normal normal normal " + conf["xfontsize"] + "pt Arial"
    });
    mychart.addAxis("y", {title: conf['y_title'],
                    min: conf["ymin"], max: conf["ymax"],
                    vertical: true, font: "normal normal normal 10pt Arial", fontWeight: 12
    });
    // plot line first so on top
    if(conf['inc_regression_js'] == true){
        mychart.addPlot("regression", {type: "Lines", markers: false, shadows: {dx: 2, dy: 2, dw: 2}});
        for (i in series){
            try {
                mychart.addSeries(series[i]["lineLabel"], series[i]["xyLinePairs"], series[i]["lineStyle"]);
            } catch(err) {
                /*do nothing*/
            }
        }
    }
    mychart.addPlot("default", {type: "Scatter"});
    mychart.addPlot("grid", {type: "Grid", vMajorLines: true});
    var i
    for (i in series){
        mychart.addSeries(series[i]["seriesLabel"], series[i]["xyPairs"], series[i]["style"]);
    }
    var anim_a = new dc.action2d.Magnify(mychart, "default");
    var anim_b = new dc.action2d.Tooltip(mychart, "default",
       {text: getTooltip, 
        tooltipBorderColour: conf['tooltip_border_colour'],
        connectorStyle: conf['connector_style']});
    mychart.render();
    var legend = new dojox.charting.widget.Legend({chart: mychart}, "legend_for_" + chartname);
    var anim_a = new dc.action2d.Highlight(mychart, "default", {
        highlight: conf["highlight"],
        duration: 450,
        easing:   dojo.fx.easing.sineOut
    });
    var anim_b = new dc.action2d.Shake(mychart, "default");
    var anim_c = new dc.action2d.Tooltip(mychart, "default", {text: getTooltip, 
        tooltipBorderColour: conf['tooltip_border_colour'],
        connectorStyle: conf['connector_style']});
    mychart.render();
}

// BOX ***************************************************************************************
makeBoxAndWhisker = function(chartname, series, seriesconf, conf){
    nChartFontColour = conf["plot_font_colour"]
    nChart = conf["n_chart"];
    // chartwide function setting - have access to val.element (Column), val.index (0), val.run.data (y_vals)
    var getTooltip = function(val){
        return val.y;
    };
    var dc = dojox.charting;
    var mychart = new dc.Chart2D(
        chartname,
        {margins:
            {l: conf['margin_offset_l'],
             t: 10,
             r: 10,
             b: 10+conf['axis_lbl_drop']},
         yTitleOffset: conf['y_title_offset']});
    var sofa_theme = new dc.Theme({
        chart:{
	        stroke:    null,
        	fill:      conf['chart_bg'],
	        pageStyle: null // suggested page style as an object suitable for dojo.style()
	    },
	    plotarea:{
	        stroke: null,
	        fill:   conf["plot_bg"]
	    },
	    axis:{
	        stroke:	{ // the axis itself
	            color: conf['plot_font_colour'],
	            width: null
	        },
            tick: {	// used as a foundation for all ticks
	            color:     conf["axis_font_colour"],
	            position:  "center",
	            fontColor: conf['axis_font_colour']
	        },
	        majorTick:	{ // major ticks on axis, and used for major gridlines
	            width:  conf['gridline_width'],
	            length: 6, 
                color:  conf['axis_font_colour'] // we have vMajorLines off so we don't need to match grid color e.g. null
	        },
	        minorTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.8,
	            length: 3
	        },
	        microTick:	{ // minor ticks on axis, and used for minor gridlines
	            width:  0.5,
	            length: 1
	        }
	    }
    });
    mychart.setTheme(sofa_theme);
    mychart.addPlot("default", {type: "Boxplot", markers: true});
    mychart.addPlot("grid", {type: "Grid", vMajorLines: false});
    mychart.addAxis(
        "x",
        {title: conf['x_title'],
         min: conf["xmin"],
         max: conf["xmax"], 
         majorTicks: true,
         minorTicks: conf['has_minor_ticks'],
         labels: conf["xaxis_lbls"],
         font: "normal normal normal " + conf["xfontsize"] + "pt Arial",
         rotation: conf['axis_lbl_rotate']});
    mychart.addAxis(
        "y",
        {title: conf['y_title'],
         vertical: true,
         min: conf["ymin"],
         max: conf["ymax"], 
         majorTicks: true,
         minorTicks: true,
         font: "normal normal normal " + conf["yfontsize"] + "pt Arial"});
    var i
    for (i in series){
        mychart.addSeries(series[i]["seriesLabel"], [], series[i]["boxDets"]);
    }
    var anim_a = new dc.action2d.Highlight(mychart, "default", {
        highlight: conf["highlight"],
        duration: 450,
        easing:   dojo.fx.easing.sineOut
    });
    var anim_b = new dc.action2d.Tooltip(
        mychart,
        "default",
        {text: getTooltip,
         tooltipBorderColour: conf['tooltip_border_colour'], 
         connectorStyle: conf['connector_style']});
    mychart.render();

    var dummychart = new dc.Chart2D("dum" + chartname);
    dummychart.addPlot("default", {type: "ClusteredColumns"});
    for (i in seriesconf){
        dummychart.addSeries(seriesconf[i]["seriesLabel"], [1,2], seriesconf[i]["seriesStyle"]);
    }
    dummychart.render();
    var legend = new dojox.charting.widget.Legend({chart: dummychart}, "legend_for_" + chartname);
}
