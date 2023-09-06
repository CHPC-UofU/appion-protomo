<?php

/**
 *	The Leginon software is Copyright 2010 
 *	The Scripps Research Institute, La Jolla, CA
 *	For terms of the license agreement
 *	see  http://ami.scripps.edu/software/leginon-license
 *
 */
 
 /**
  *  Please visit http://yourhost/myamiwebfolder/setup
  *  for automatically setup this config file for the
  *  first time.
  */
 

require_once 'inc/config.inc';
define('WEB_ROOT',dirname(__FILE__));

// --- define myamiweb tools base --- //
define('PROJECT_NAME',"alexproject");
define('PROJECT_TITLE',"Alex's Appion and Leginon Tools<br><font size=5>version 1.2.2</font><br><font size=3><a href='https://github.com/nysbc/appion-protomo' target='_blank'><b>Check if there is an update!</a> | <a href='https://groups.google.com/forum/#!topic/appion-protomo' target='_blank'>Get help from the Google group!</a></b></font>");

// --- define site base path -- //
// --- This should be changed if the myamiweb directory is located -- //
// --- in a sub-directory of the Apache web directory. -- //
// --- ex. myamiweb is in /var/www/html/applications/myamiweb/ then -- //
// --- change "myamiweb to "applications/myamiweb" -- //
define('BASE_PATH',"alex/dev/myamiweb");

define('BASE_URL', "/".BASE_PATH."/");
define('PROJECT_URL', BASE_URL."project/");

// --- myamiweb login --- //
// Browse to the administration tools in myamiweb prior to 
// changing this to true to populate DB tables correctly.
define('ENABLE_LOGIN', true);

// --- Administrator email title and email address -- //
define('EMAIL_TITLE',"NYSBC EM Group");
define('ADMIN_EMAIL',"cnegro@nysbc.org");

// --- When 'ENABLE_SMTP set to true, email will send out -- //
// --- via ADMIN_EMIL's SMTP server. --// 
define('ENABLE_SMTP', true);
define('SMTP_HOST',"localhost");

// --- Check this with your email administrator -- //
// --- Set it to true if your SMTP server requires authentication -- //
define('SMTP_AUTH', false);

// --- If SMTP_AUTH is not required(SMTP_AUTH set to false, -- //
// --- no need to fill in 'SMTP_USERNAME' & SMTP_PASSWORD -- //
define('SMTP_USERNAME',"");
define('SMTP_PASSWORD',"");

// --- Set your MySQL database server parameters -- //
define('DB_HOST',"192.168.4.21");
define('DB_USER',"emg_user");
define('DB_PASS',"notsosuper");
define('DB_LEGINON',"ny_leginondb");
define('DB_PROJECT',"ny_projectdb");

// --- default URL for project section --- //
define('VIEWER_URL', BASE_URL."3wviewer.php?expId=");
define('SUMMARY_URL', BASE_URL."summary.php?expId=");
define('UPLOAD_URL', BASE_URL."processing/uploadimage.php");

// --- Set cookie session time -- //
define('COOKIE_TIME', 0);		//0 is never expire. 

// --- defaut user group -- //
define('GP_USER', 'users');

// --- XML test dataset -- //
$XML_DATA = "test/viewerdata.xml";

// --- Set Default table definition -- //
define('DEF_PROCESSING_TABLES_FILE', "defaultprocessingtables.xml");
define('DEF_PROCESSING_PREFIX',"nyap_");

// --- Set External SQL server here (use for import/export application) -- //
// --- You can add as many as you want, just copy and paste the block -- //
// --- to a new one and update the connection parameters -- //
// --- $SQL_HOSTS['example_host_name']['db_host'] = 'example_host_name'; -- //
// --- $SQL_HOSTS['example_host_name']['db_user'] = 'usr_object'; -- //
// --- $SQL_HOSTS['example_host_name']['db_pass'] = ''; -- //
// --- $SQL_HOSTS['example_host_name']['db'] = 'legniondb'; -- //

$SQL_HOSTS[DB_HOST]['db_host'] = DB_HOST;
$SQL_HOSTS[DB_HOST]['db_user'] = DB_USER;
$SQL_HOSTS[DB_HOST]['db_pass'] = DB_PASS;
$SQL_HOSTS[DB_HOST]['db'] = DB_LEGINON;

// --- path to main --- //
set_include_path(dirname(__FILE__).PATH_SEPARATOR
				.dirname(__FILE__)."/project".PATH_SEPARATOR
				.dirname(__FILE__)."/lib".PATH_SEPARATOR
				.dirname(__FILE__)."/lib/PEAR");

// --- add plugins --- //
// --- uncomment to enable processing web pages -- //
addplugin("processing");


// --- default appion base directory parallel to leginon --- //
define('DEFAULT_APPION_PATH',"/gpfs/appion");
// --- negative index of the directory before the leginon directory used to replace the element of DEFAULT_APPION_PATH --- //
define('APPION_PARENT_ADDITION',1); 
define('APPION_PARENT_REPLACEMENT',0); 

// --- Add as many processing hosts as you like -- //
// --- Please enter your processing host information associate with -- //
// --- Maximum number of the processing nodes									-- //
// --- $PROCESSING_HOSTS[] = array('host' => 'host1.school.edu', 'nproc' => 4); -- //
// --- $PROCESSING_HOSTS[] = array('host' => 'host2.school.edu', 'nproc' => 8); -- //

$PROCESSING_HOSTS[] = array('host' => 'SEMC-head',
'nodesdef' => '2',
'nodesmax' => '27',
'ppndef' => '4',
'ppnmax' => '23',
'reconpn' => '24',
'walltimedef' => '240',
'walltimemax' => '',
'cputimedef' => '2400',
'cputimemax' => '',
'memorymax' => '256',
'appionbin' => '/home/anoble/myami/appion/bin/',
'appionlibdir' => '/home/anoble/myami/appion/appionlib',
'baseoutdir' => DEFAULT_APPION_PATH,
'localhelperhost' => 'SEMC-head.nysbc.org',
'dirsep' => '/',
'queues' => array('shortq','longq'),
'wrapperpath' => '/home/anoble/myami/appion/bin/',
'loginmethod' => 'USERPASSWORD',
'loginusername' => '',
'passphrase' => '',
'publickey' => '',
'privatekey' => '' );

/*
$PROCESSING_HOSTS[] = array('host' => 'guppy',
'nodesdef' => '2',
'nodesmax' => '8',
'ppndef' => '4',
'ppnmax' => '8',
'reconpn' => '8',
'walltimedef' => '240',
'walltimemax' => '',
'cputimedef' => '2400',
'cputimemax' => '',
'memorymax' => '',
'appionbin' => '/opt/myamisnap/bin/',
'appionlibdir' => '/opt/myamisnap/lib/appionlib',
'baseoutdir' => DEFAULT_APPION_PATH,
'localhelperhost' => 'guppy.nysbc.org',
'dirsep' => '/',
'wrapperpath' => '/opt/myamisnap/bin/appion',
'loginmethod' => 'USERPASSWORD',
'loginusername' => '',
'passphrase' => '',
'publickey' => '',
'privatekey' => '' );
*/


// --- register your cluster configure file below i.e (default_cluster) --- //
// --- $CLUSTER_CONFIGS[] = 'cluster1'; -- //
// --- $CLUSTER_CONFIGS[] = 'cluster2'; -- //

#$CLUSTER_CONFIGS[] = 'garibaldi';
$CLUSTER_CONFIGS[] = 'guppy';

// --- Microscope spherical aberration constant
// --- Example : 2.0 --- //
define('DEFAULTCS',"2.0");

// --- Restrict file server if you want --- //
// --- Add your allowed processing directory as string in the array
$DATA_DIRS = array();

// --- Enable Image Cache --- //
define('ENABLE_CACHE', false);
// --- caching location --- //
// --- please make sure the apache user has write access to this folder --- //
// --- define('CACHE_PATH', "/srv/www/cache/"); --- //
define('CACHE_PATH',"/srv/cache/dbem/");
define('CACHE_SCRIPT', WEB_ROOT.'/makejpg.php');

// --- define Flash player base url --- //
define('FLASHPLAYER_URL', "/flashplayer/");

// --- define python commands - path --- //

// to download images as TIFF or JPEG
// $pythonpath="/your/site-packages";
// putenv("PYTHONPATH=$pythonpath");

// To use mrc2any, you need to install the pyami package which is part
// of myami.  See installation documentation for help.
// --- define('MRC2ANY', "/usr/bin/mrc2any" --- //
define('MRC2ANY',"/usr/bin/mrc2any");

// --- Check if IMAGIC is installed and running, otherwise hide all functions --- //
define('HIDE_IMAGIC', false);

// --- Check if MATLAB is installed and running, otherwise hide all functions --- //
define('HIDE_MATLAB', false);

// --- hide processing tools still under development. --- //
define('HIDE_FEATURE', false);

// --- hide processing tools requiring GPU - this is a temporary fix
// --  processingHost should be modified in the future ---//

define('HIDE_GPU_FEATURE',false);

// --- temporary images upload directory --- //
define('TEMP_IMAGES_DIR',"/emg/data15/temp");

// --- use appion warpper --- //
define('USE_APPION_WRAPPER', true);
define('APPION_WRAPPER_PATH',"/home/anoble/myami/appion/bin/");



// --- hide testing tools related to specific data sets. --- //
define('HIDE_TEST_TOOLS', false);

// --- define('SERVER_HOST', "redux.schools.edu"); --- //
// --- define('SERVER_PORT', "55123"); --- //
#define('SERVER_HOST', "cronus3");
define('SERVER_HOST', "localhost");
#define('SERVER_HOST', "cronus2");
define('SERVER_PORT', "55123");

// --- list specifc datasets that have test scripts associated with them --- //
$TEST_SESSIONS = array(
          'zz07jul25b'
          ,'zz06apr27c'
          ,'zz09feb12b'
          ,'zz09apr14b'
          ,'zz09feb18c');


// --- sample tracking ---//
define('SAMPLE_TRACK', false);
?>
