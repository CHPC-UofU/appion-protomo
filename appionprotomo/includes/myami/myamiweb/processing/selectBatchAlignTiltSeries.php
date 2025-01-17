<?php
/**
 *	The Leginon software is Copyright under 
 *	Apache License, Version 2.0
 *	For terms of the license agreement
 *	see  http://leginon.org
 *
 */

require_once "inc/particledata.inc";
require_once "inc/leginon.inc";
require_once "inc/project.inc";
require_once "inc/processing.inc";

$expId = $_GET['expId'];
$formAction=$_SERVER['PHP_SELF']."?expId=$expId";

processing_header("Batch Align Tilt-Series","Batch align Tilt-Series Page", $javascript,False);

// Selection Header
echo "<table border='0' width='640'>\n";
echo "<tr><td>\n";
echo "  <h2>Batch Tilt-Series Alignment and Reconstruction Procedures</h2>\n";
echo "  <h4>\n";
echo "    Here you will find the same maintained software packages \n"
	."as in 'Align Tilt-Series', but configured to run in \n"
	."batch mode. Select multiple tilt-series that you wish to run in batch \n"
	."mode, input the parameters you wish to use in the alignment and \n"
	."reconstruction of the tilt-series, then copy & paste the command into a terminal window. \n"
	."Here you will also find a Screening Mode for use during Leginon data collection, \n"
	."a Fully Automated processing mode for Automatically aligning tilt-series to convergence \n"
	."in batch, batch CTF Estimation, and batch Dose Compensation. \n";
echo "  <h4>\n";
echo "    <i>(The following workflows use PHP sessions to keep track of \n"
        ."variables. They are designed to be used immediately following \n"
        ."a full 'Align Tilt-Series' run.)</i>";
echo "  </h4>\n";
echo "</td></tr>\n";
echo "</table>\n";

echo "<br/>\n";
echo "<table border='1' class='tableborder' width='640'>\n";

/*
** Protomo 2.4.1
*/

echo "<tr><td width='100' align='center'>\n";
echo "  <a href='runAppionLoop.php?expId=$expId&form=Protomo2BatchForm'><img src='img/protomo.png' width='120'>\n";
echo "</td><td>\n";
echo "  <h3><a href='runAppionLoop.php?expId=$expId&form=Protomo2BatchForm'>Protomo 2.4.1</a></h3>\n";
echo " <p> Protomo is a software package used in electron tomography for marker-free alignment and weighted back- "
	."projection reconstruction of tilt-series. The marker-free alignment is based on cross-correlation methods and "
	."projection matching. Protomo also includes the refinement of geometric parameters of the tilt-series. "
	."3D reconstruction is carried out by weighted back-projection with general weighting functions "
	."that allow varying tilt angle increments. "
	."<br/><br/>The <a href='https://www.ncbi.nlm.nih.gov/pubmed/26455557' target='_blank'> original research article is here</a>."
	."</p>\n";
echo "</td></tr>\n";


echo "</table>\n";
processing_footer();
exit;

