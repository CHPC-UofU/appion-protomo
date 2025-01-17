<?php

/**
 *	The Leginon software is Copyright under 
 *	Apache License, Version 2.0
 *	For terms of the license agreement
 *	see  http://leginon.org
 */
ini_set('display_errors', '0');     # don't show any errors...
error_reporting(E_ALL | E_STRICT);

require_once dirname(__FILE__).'/../config.php';
require_once "inc/path.inc";
require_once "inc/leginon.inc";
require_once "inc/processing.inc";
require_once "inc/viewer.inc";
require_once "inc/project.inc";
require_once "inc/appionloop.inc";
require_once "inc/particledata.inc";

$page = $_SERVER['REQUEST_URI'];
header("Refresh: 300; URL=$page");

$outdir=$_GET['outdir'];
$runname=$_GET['runname'];
$tiltseries=$_GET['tiltseries'];

$defocus_gif_files = glob("$outdir/".$runname."/defocus_estimation/*/*/diagnostic.gif");
$ctf_gif_files = glob("$outdir/$runname/media/ctf_correction/s*.gif");
$dose_gif_files = glob("$outdir/$runname/media/dose_compensation/s*.gif");
$drift_gif_files = glob("$outdir/$runname/media/max_drift/s*.gif");
$qa_gif_file = "$outdir/$runname/media/quality_assessment/series".sprintf('%04d',$tiltseries)."_quality_assessment.gif";
$azimuth_gif_files = "$outdir/$runname/media/angle_refinement/series".sprintf('%04d',$tiltseries)."_azimuth.gif";
$orientation_gif_file = "$outdir/$runname/media/angle_refinement/series".sprintf('%04d',$tiltseries)."_orientation.gif";
$elevation_gif_files = "$outdir/$runname/media/angle_refinement/series".sprintf('%04d',$tiltseries)."_elevation.gif";

$defocus_gif = "loadimg.php?rawgif=1&filename=".$defocus_gif_files[0];
$ctfplot_gif = "loadimg.php?rawgif=1&filename=".$ctf_gif_files[0];
$ctfdefocus_gif = "loadimg.php?rawgif=1&filename=".$ctf_gif_files[1];
$dose_gif = "loadimg.php?rawgif=1&filename=".$dose_gif_files[0];
$dosecomp_gif = "loadimg.php?rawgif=1&filename=".$dose_gif_files[1];
$drift_gif = "loadimg.php?rawgif=1&filename=".$drift_gif_files[0];
$qa_gif = "loadimg.php?rawgif=1&filename=".$qa_gif_file;
$azimuth_gif = "loadimg.php?rawgif=1&filename=".$azimuth_gif_files;
$orientation_gif = "loadimg.php?rawgif=1&filename=".$orientation_gif_file;
$elevation_gif = "loadimg.php?rawgif=1&filename=".$elevation_gif_files;

$html .= "
	<center><H3><b>Tilt-Series #$tiltseries Quality Assessment Plots</b></H3></center>
	<hr />";

$html .= "
	<H4><center><b>CCMS Plot</b></center></H4>";
        
if (isset($qa_gif_file)) {
	$html .= '<center><img src="'.$qa_gif.'" alt="qa" /></center>
	<hr />';
} else {
        $html .= "<center><b>CCMS Plot for Tilt-Series ".$tiltseries." either failed to generate or is processing</b></center>";
}

$html .= "
	<H4><center><b>Tilt Azimuth Plot</b></center></H4>";
        
if (isset($azimuth_gif_files)) {
	$html .= '<center><img src="'.$azimuth_gif.'" alt="azimuth" /></center>
	<hr />';
} else {
        $html .= "<center><b>Tilt Azimuth Plot for Tilt-Series ".$tiltseries." either failed to generate or is processing</b></center>";
}

$html .= "
	<H4><center><b>Grid Orientation Plot</b></center></H4>";
        
if (isset($orientation_gif_file)) {
	$html .= '<center><img src="'.$orientation_gif.'" alt="theta" /></center>
	<hr />';
} else {
        $html .= "<center><b>Grid Orientation Plot for Tilt-Series ".$tiltseries." either failed to generate or is processing</b></center>";
}

$html .= "
	<H4><center><b>Tilt Elevation Plot</b></center></H4>";
        
if (isset($elevation_gif_files)) {
	$html .= '<center><img src="'.$elevation_gif.'" alt="theta" /></center>
	<hr />';
} else {
        $html .= "<center><b>Tilt Elevation Plot for Tilt-Series ".$tiltseries." either failed to generate or is processing</b></center>";
}

if (isset($defocus_gif_files[0])) {
	$html .= "
<center><H4>Defocus Estimation</H4></center>
<br />";
	$html .= '<table id="" class="display" cellspacing="0" border="1" align="center">';
	$html .= "<tr>";
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[2].'" alt="defocus_gif2" width="400" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[6].'" alt="defocus_gif6" width="580" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[10].'" alt="defocus_gif10" width="755" /></th>';
	$html .= "</tr><tr>";
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[0].'" alt="defocus_gif0" width="400" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[4].'" alt="defocus_gif4" width="580" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[8].'" alt="defocus_gif8" width="755" /></th>';
	$html .= "</tr><tr>";
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[1].'" alt="defocus_gif1" width="400" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[5].'" alt="defocus_gif5" width="580" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[9].'" alt="defocus_gif9" width="755" /></th>';
	$html .= "</tr><tr>";
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[3].'" alt="defocus_gif3" width="400" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[7].'" alt="defocus_gif7" width="580" /></th>';
	$html .= '<th><img src="loadimg.php?rawgif=1&filename='.$defocus_gif_files[11].'" alt="defocus_gif11" width="755" /></th>';
	$html .= '</tr><tr></table><br>';
}

if (isset($ctf_gif_files[0])) {
	$html .= "
<br />	
<center><H4>CTF Correction</H4></center>
<br />";
	$html .= '<center><table id="" class="display" cellspacing="0" border="0"><tr>';
	$html .= '<td><img src="'.$ctfdefocus_gif.'" alt="ctfdefocus_gif" />'."<br /></td>";
	$html .= '<td><img src="'.$ctfplot_gif.'" alt="ctfplot_gif" />'."<br /></td>";
	$html .= '</tr><tr></table></center><br>
	<hr />';
}

if (isset($dose_gif_files[0])) {
	$html .= "
<br />	
<center><H4>Dose Compensation</H4></center>
<br />";
	$html .= '<center><table id="" class="display" cellspacing="0" border="0"><tr>';
	$html .= '<td><img src="'.$dose_gif.'" alt="dose_gif" />'."<br /></td>";
	$html .= '<td><img src="'.$dosecomp_gif.'" alt="dosecomp_gif" />'."<br /></td>";
	$html .= '</tr><tr></table></center><br>';
}

if (isset($drift_gif_files[0])) {
	$html .= "
<br />	
<center><H4>Maximum Per-Tilt Image Frame Drift</H4></center>
<br />";
	$html .= '<center><table id="" class="display" cellspacing="0" border="0"><tr>';
	$html .= '<td><img src="'.$drift_gif.'" alt="drift_gif" />'."<br /></td>";
	$html .= '</tr><tr></table></center><br>';
}

echo $html
?>
</body>
</html>
