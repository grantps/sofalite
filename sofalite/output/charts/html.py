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
<script src="{{sofalite_web_resources_root}}/sofastatsdojo_minified.js"></script>
<script src="{{sofalite_web_resources_root}}/sofastats_charts.js"></script>

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
{{common_css}}
{{styled_misc_css}}
{{styled_dojo_css}}
-->
</style>

<script type="text/javascript">

function getAllFunctions(){
    var allFunctions = [];
    for (var i in window) {
      if((typeof window[i]).toString()=="function"){
        fn_name = window[i].name;
        if (fn_name.startsWith('make_bar_chart')) {
            allFunctions.push(fn_name);
        }
      }
   }
   return allFunctions;
}

makeObjects = function(){
    functions = getAllFunctions();
    functions.forEach(fn_name => window[fn_name]());
};
dojo.addOnLoad(makeObjects);

var DEFAULT_SATURATION  = 100,
DEFAULT_LUMINOSITY1 = 75,
DEFAULT_LUMINOSITY2 = 50,

c = dojox.color,

cc = function(colour){
    return function(){ return colour; };
},

hl = function(colour){

    var a = new c.Color(colour),
        x = a.toHsl();
    if(x.s == 0){
        x.l = x.l < 50 ? 100 : 0;
    }else{
        x.s = DEFAULT_SATURATION;
        if(x.l < DEFAULT_LUMINOSITY2){
            x.l = DEFAULT_LUMINOSITY1;
        }else if(x.l > DEFAULT_LUMINOSITY1){
            x.l = DEFAULT_LUMINOSITY2;
        }else{
            x.l = x.l - DEFAULT_LUMINOSITY2 > DEFAULT_LUMINOSITY1 - x.l
                ? DEFAULT_LUMINOSITY2 : DEFAULT_LUMINOSITY1;
        }
    }
    return c.fromHsl(x);
}

getfainthex = function(hexcolour){
    var a = new c.Color(hexcolour)
    x = a.toHsl();
    x.s = x.s * 1.5;
    x.l = x.l * 1.25;
    return c.fromHsl(x);
}

makefaint = function(colour){
    var fainthex = getfainthex(colour.toHex());
    return new dojox.color.Color(fainthex);
}

</script>
</head>

<body class="tundra">
"""
