<?php

/**
 *	The Leginon software is Copyright under 
 *	Apache License, Version 2.0
 *	For terms of the license agreement
 *	see  http://leginon.org
 */
require_once "inc/leginon.inc";
require_once "inc/graph.inc";

$defaultId= 4828;
//$defaultpreset='en';
$sessionId= ($_GET[Id]) ? $_GET[Id] : $defaultId;
//$preset = ($_GET[preset]) ? $_GET[preset] : $defaultpreset;
$viewdata = ($_GET['vdata']==1) ? true : false;
$viewsql = $_GET['vs'];

$histogram= true;
$histaxis=($_GET['haxis']) ? $_GET['haxis'] : 'y';
$width=$_GET['w'];
$height=$_GET['h'];
$thicknessdata = $leginondata->getZeroLossIceThickness($sessionId);

foreach($thicknessdata as $t) {
	$data[] = $t['thickness'];
}
if ($viewsql) {
	$sql = $leginondata->mysql->getSQLQuery();
	echo $sql;
	exit;
}
if ($viewdata) {
	$keys = array("timestamp", "filename", "thickness");
	echo dumpData($thicknessdata, $keys);
	exit;
}

$display_x = 'timestamp';
$display_y = 'thickness';
$axes = array($display_x,$display_y);
if ($histogram == true && $histaxis == 'x') 
	$axes = array($display_y,$display_x);
$dbemgraph= new dbemgraph($thicknessdata, $axes[0], $axes[1]);
$dbemgraph->lineplot=False;
$dbemgraph->title="Ice Thickness histogram using zero loss peak";
$dbemgraph->yaxistitle="Thickness /nm";

if ($viewdata) {
	$keys = array("timestamp", "thickness");
	echo dumpData($thicknessdata, $keys);
	$dbemgraph->dumpData(array($display_x, $display_y));
}
if ($histogram) {
	$dbemgraph->histogram=true;
}

$dbemgraph->scalex(1e-3);
$dbemgraph->scaley(1e-3);
$dbemgraph->dim($width,$height);
$dbemgraph->graph();


?>
