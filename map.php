<?php

$default_engine = "dot";
if (isset($_GET["engine"])) {
  $effective_engine = $_GET["engine"];
}
elseif ($_GET["engine"] == "default") {
  $effective_engine = $default_engine;
}
else {
  $effective_engine = $default_engine;
}

?>

<html>
  <head>
    <meta charset="utf-8">
    <title>Viz.js</title>
    <style>
    body {
        background: black;
        color: white;
        font-family: Helvetica;
    }

    select {
        border: 1px solid #646464;
        color: white;
        background: #323232;
        width: 200px;
        padding: 5px 35px 5px 5px;
        font-size: 16px;
        border: 1px solid #ccc;
        height: 34px;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        border-radius: 10px;
        text-align: center;
    }  
    #selector {
        position: fixed;
        opacity: 0.7;
    }
    </style>
  </head>
  <body>
    <div id="selector">
        <form action="map.php" method="get">
            <select name="engine" onchange="this.form.submit()">
                <option value="default" selected>Rendering engine</option>
                <option value="dot">Dot</option> 
                <!--<option value="neato">Neato</option>-->
                <option value="circo">Circo</option>
                <!--<option value="twopi">TwoPi</option>-->
                <!--<option value="fdp">FDP</option>-->
                <!--<option value="osage">Osage</option>-->
            </select>
       </form>
    </div>
    <script type="text/vnd.graphviz" id="netgraph">
		<?php include("CHANGEME.dot"); ?>
	</script>
<script src="viz.js"></script>
    <script>

      function inspect(s) {
        return "<pre>" + s.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;") + "</pre>"
      }

      function src(id) {
        return document.getElementById(id).innerHTML;
      }

      function doGraph(id, format, engine) {
        var result;
        try {
          result = Viz(src(id), format, engine);
          if (format === "svg")
            return result;
          else
            return inspect(result);
        } catch(e) {
          return inspect(e.toString());
        }
      }

      document.body.innerHTML += doGraph("netgraph", "svg", "<?=$effective_engine?>");
</script>

  </body>
</html>

