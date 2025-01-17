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

session_destroy();
$expId = $_GET['expId'];
$formAction=$_SERVER['PHP_SELF']."?expId=$expId";

processing_header("Align Tilt-Series","Align Tilt-Series Page", $javascript,False);

// Selection Header
echo "<table border='0' width='640'>\n";
echo "<tr><td>\n";
echo "  <h2>Indvidual Tilt-Series Alignment and Reconstruction Procedures</h2>\n";
echo "  <h4>\n";
echo "    Tilt-series may have been prepared with or without \n"
	."fiducial markers. Some tilt-series are amenable \n"
	."to automated alignment while others require (some) \n"
	."manual alignment. Here you will find automated tilt-series \n"
        ."alignment workflows.";
echo "  <h4>\n";
echo "    <i>(The following workflows use PHP sessions to keep track of \n"
        ."variables. They are designed to be used from start to finish \n"
        ."in a browser independent of all other Appion queries.)</i>";
echo "  </h4>\n";
echo "</td></tr>\n";
echo "</table>\n";


echo "<br/>\n";
echo "<table border='1' class='tableborder' width='640'>\n";

/*
** Protomo 2.4.1
*/

echo "<tr><td width='100' align='center'>\n";
echo "  <a href='runAppionLoop.php?expId=$expId&form=Protomo2CoarseAlignForm'><img src='img/protomo.png' width='120'>\n";
echo "</td><td>\n";
echo "  <h3><a href='runAppionLoop.php?expId=$expId&form=Protomo2CoarseAlignForm'>Protomo 2.4.1</a></h3>\n";
echo " <p> Protomo is a software package used in electron tomography for marker-free alignment and weighted back-"
	."projection (WBP) reconstruction of tilt-series. The marker-free alignment is based on cross-correlation methods and "
	."projection matching. Protomo also includes the refinement of geometric parameters of the tilt-series. "
	."Additionally there are CTF estimation and dose compensation procedures. The option to process tilt-series "
    ."that are not in the Appion/Leginon database is also available.<br><br>"
	."The idea with Protomo is for the user to work through aligning a single tilt-series in a session, then use the "
	."parameters that produce acceptable results on the entire tilt-series session using 'Batch Align Tilt-Series' "
	."from the left menu.<br><br>"
    ."In addition to Protomo WBP, the user can also choose to reconstruct tomograms with Tomo3D WBP and Tomo3D SIRT.<br><br>"
	."The <a href='https://www.ncbi.nlm.nih.gov/pubmed/26455557' target='_blank'> original research article is here</a>."
	."</p>\n";
echo "</td></tr>\n";


/*
** Old software
*/

//echo "<tr><td width='100' align='center'>\n";
//		echo "  <img src='img/other_software.png' width='125'>\n";
//echo "</td><td>\n";
//echo "  <h3><a href='runTomoAligner.php?expId=$expId'>Other Software Packages</a></h3>\n";
//echo " <p>Here you will find older implementations for aligning tilt-series, "
//	."including Leginon alignment, and Imod shift-only alignment. "
//	."These are only good for rough and quick alignment"
//	."</p>\n";
//echo "</td></tr>\n";



echo "</table>\n";
processing_footer();
exit;

