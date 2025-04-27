html_bottom = """\
</body>
</html>
"""

tpl_html_top = """\
<!DOCTYPE html>

<head>
<title>SOFALite Report 2022</title>

<link rel='stylesheet' type='text/css' href="{{sofalite_web_resources_root}}/tundra.css" />
<script src="{{sofalite_web_resources_root}}/dojo.xd.js"></script>
<script src="{{sofalite_web_resources_root}}/sofalitedojo_minified.js"></script>
<script src="{{sofalite_web_resources_root}}/sofalite_charts.js"></script>

<style type="text/css">
<!--
    .dojoxLegendNode {
        border: 1px solid #ccc;
        margin: 5px 10px 5px 10px;
        padding: 3px
    }
    .dojoxLegendText {
        vertical-align: text-top;
        padding-right: 10px
    }
    @media print {
        .screen-float-only{
        float: none;
        }
    }
    @media screen {
        .screen-float-only{
        float: left;
        }
    }
-->
</style>
<style type="text/css">
<!--
{{generic_unstyled_css}}
{{styled_dojo_chart_css}}
-->
</style>
</head>

<body class="tundra">
"""
