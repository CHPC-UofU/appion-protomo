<?php

/**
 *	The Leginon software is Copyright under 
 *	Apache License, Version 2.0
 *	For terms of the license agreement
 *	see  http://leginon.org
 *
 */

ini_set('session.gc_maxlifetime', 604800);
session_set_cookie_params(604800);

session_start();
$sessionname=$_SESSION['sessionname'];
$imageinfo=$_SESSION['imageinfo'];
$runname=$_GET['runname'];
$tiltseries=$_GET['tiltseries'];
$log=$_GET['log'];
$rundir=dirname($log);

$html .= "
	<center><H2><b>Tilt-Series #".ltrim($tiltseries, '0')."<br><font size=3>($runname)</font></b></H2></center>
	";

if ((file_exists($log)) and (filesize($log) !== 0)) {
	$logfile = file($log);
	
	foreach($logfile as $line) {
		$description_line = explode(' ', $line);
		if ($description_line[0] == 'Description:') {
			$html .= "
				<H3><center><hr>Description</b></H3></center>
				<hr /></br>";
			$html .= substr(strstr($line," "), 1);
		}
	}
	$html .= "<br><br>
		<center><H3><b><hr>Image List</b></H3></center>
		<hr /></br>";
	$images = glob("$rundir/raw/original/*");
	foreach($images as $image) {
		$html .= basename($image).'<br>';
	}
	$html .= "<br>
		<center><H3><b><hr>Alignment Log File</b></H3></center>
		<hr /></br>";
	foreach($logfile as $line) {
		$html .= $line.'<br>';
	}
}else{
	$html .= "<center><b>Log file not found...</b><br>(not visible until tilt-series alignment finishes)</center>";
}

$reconstruction_logs = glob("$rundir/protomo2reconstruction*.log");
if (count($reconstruction_logs) > 0) {
	$html .= "
		<br><H3><center><hr>Reconstruction Log Files</b></H3></center>
		<hr /></br>";
	foreach($reconstruction_logs as $reconstruction_log) {
		if ((file_exists($reconstruction_log)) and (filesize($reconstruction_log) !== 0)) {
			$html .= "
				<H4><center><hr>$reconstruction_log</b></H4></center>
				<hr /></br>";
			$reconstruction_log_file = file($reconstruction_log);
			foreach($reconstruction_log_file as $line) {
				$html .= $line.'<br>';
			}
		}
	}
}


echo $html

?>
</body>
</html>