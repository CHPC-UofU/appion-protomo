#!/usr/bin/env python
# coding: utf8
# 
# This script provides the user access to the protomo command line interface,
# allowing for the manual alignment

from __future__ import division
import os
import re
import sys
import glob
import subprocess
import multiprocessing as mp
from pyami import mrc
from appionlib import basicScript
from appionlib import apDisplay
from appionlib import apProTomo2Aligner

try:
	import protomo
	print "\033[92m(Ignore the error: 'protomo: could not load libi3tiffio.so, TiffioModule disabled')\033[0m"
except:
	apDisplay.printError("Protomo did not get imported. Aborting.")
	sys.exit()


#=====================
class ProTomo2ManualAligner(basicScript.BasicScript):
	#=====================
	def setupParserOptions(self):
		self.parser.set_usage( "Usage: %prog --tiltseries=<#> --rundir=<rundir> --iteration=<iteration> [options]")
		
		self.parser.add_option("--tiltseries", dest="tiltseries", help="Name of Protomo series, e.g. --tiltseries=31")
		
		self.parser.add_option('-R', '--rundir', dest='rundir', help="Path of run directory")
		
		self.parser.add_option('--iteration', dest='iteration', help="Iteration to run manual alignment on. Either an integer > 0, 'Coarse', 'Coarse2', 'Imod', or 'Original'.")

		self.parser.add_option("--exclude_angles", dest="exclude_angles",  default="",
			help='Select specific tilt angles in the tilt-series to remove. Accuracy must be within +-0.1 degrees, e.g. --exclude_angles="-37.5,4.2,27"')
		
		self.parser.add_option("--negative", dest="negative", type="float",  default="-90",
			help="Tilt angle, in degrees, below which all images will be removed, e.g. --negative=-45", metavar="float")
		
		self.parser.add_option("--positive", dest="positive", type="float",  default="90",
			help="Tilt angle, in degrees, above which all images will be removed, e.g. --positive=45", metavar="float")
		
		self.parser.add_option("--max_image_fraction", dest="max_image_fraction", type="float",  default="0.75",
			help="Central fraction of the tilt images that will be samples for manual alignment, e.g. --max_image_fraction=0.5", metavar="float")
		
		self.parser.add_option("--sampling", dest="sampling", type="int",  default="4",
			help="Tilt image sampling factor for manual alignment, e.g. --sampling=8", metavar="int")
		
		self.parser.add_option("--center_all_images", dest="center_all_images",  default="False",
			help="Re-center all images with respect to the image dimensions. Used when there is significant overshifting either by Leginon or Protomo, e.g. --center_all_images=True")
		
		self.parser.add_option("--re-center_images", dest="re-center_images",  default="True",
			help="Re-center all images with respect to the alignment. This will increase the maximum allowed search area, which is useful in most cases, e.g. --re-center_images=False")
		
		self.parser.add_option("--shift_x", dest="shift_x", type="float", default=0,
			help="Shift all images with respect to the alignment center. This allows the user to shift the alignment center so that objects of the interest can be aligned to, e.g. --shift_x=500")
		
		self.parser.add_option("--shift_y", dest="shift_y", type="float", default=0,
			help="Shift all images with respect to the alignment center. This allows the user to shift the alignment center so that objects of the interest can be aligned to, e.g. --shift_y=-200")
		
		self.parser.add_option("--apply_corrs", dest="apply_corrs", type="float", default=0,
			help="Apply shifts and rotations based on the corr file for the iteration being aligned and scaled by the value provided, e.g. --apply_corrs=0.75")
		
		self.parser.add_option("--tilt_azimuth", dest="tilt_azimuth",  type="float",
			help='Override the tilt-azimuth as recorded in the .tlt file. Applied before alignment, e.g. --tilt_azimuth="-57"')
		
		self.parser.add_option("--create_videos", action='store_true',
			help="Creates a tilt-series and reconstruciton video after manual alignment, e.g. --create_videos")
		
		self.parser.add_option("--citations", dest="citations", action='store_true', help="Print citations list and exit.")
		
	
	#=====================
	def checkConflicts(self):
		pass
		
		#check if files exist
		#check if necessary options exist
		
		return True


	#=====================
	def onInit(self):
		"""
		Advanced function that runs things before other things are initialized.
		For example, open a log file or connect to the database.
		"""
		return

	#=====================
	def onClose(self):
		"""
		Advanced function that runs things after all other things are finished.
		For example, close a log file.
		"""
		return

	#=====================
	def start(self):
		###setup
		if self.params['citations']:
			apProTomo2Aligner.printCitations()
			sys.exit()
		os.chdir(self.params['rundir'])
		os.system('rm *i3t 2>/dev/null')
		
		seriesnumber = "%04d" % int(self.params['tiltseries'])
		base_seriesname='series'+seriesnumber
		if (self.params['iteration'] == 'Original') or (self.params['iteration'] == 'original') or (self.params['iteration'] == 'Initial') or (self.params['iteration'] == 'initial') or (self.params['iteration'] == 'O') or (self.params['iteration'] == 'o'):
			seriesname='coarse_'+base_seriesname
			tiltfilename='original.tlt'
			tiltfilename_full=self.params['rundir']+'/'+tiltfilename
		elif (self.params['iteration'] == 'Coarse') or (self.params['iteration'] == 'coarse') or (self.params['iteration'] == 'Coarse1') or (self.params['iteration'] == 'coarse1') or (self.params['iteration'] == 'C') or (self.params['iteration'] == 'c') or (self.params['iteration'] == 'C1') or (self.params['iteration'] == 'c1'):
			seriesname='coarse_'+base_seriesname
			tiltfilename=seriesname+'.tlt'
			tiltfilename_full=self.params['rundir']+'/'+tiltfilename
		elif (self.params['iteration'] == 'Coarse2') or (self.params['iteration'] == 'coarse2') or (self.params['iteration'] == 'C2') or (self.params['iteration'] == 'c2'):
			seriesname='coarse_'+base_seriesname+'_iter2'
			tiltfilename=seriesname+'.tlt'
			tiltfilename_full=self.params['rundir']+'/'+tiltfilename
		elif (self.params['iteration'] == 'Imod') or (self.params['iteration'] == 'imod') or (self.params['iteration'] == 'IMOD') or (self.params['iteration'] == 'I') or (self.params['iteration'] == 'i'):
			seriesname='imod_coarse_'+base_seriesname
			tiltfilename=seriesname+'.tlt'
			tiltfilename_full=self.params['rundir']+'/'+tiltfilename
		elif (self.params['iteration'] == 'Manual') or (self.params['iteration'] == 'manual') or (self.params['iteration'] == 'M') or (self.params['iteration'] == 'm'):
			seriesname='manual_'+base_seriesname
			tiltfilename=seriesname+'.tlt'
			tiltfilename_full=self.params['rundir']+'/'+tiltfilename
			seriesname2='manual_bak_'+base_seriesname
			tiltfilename2=seriesname2+'.tlt'
			tiltfilename_full2=self.params['rundir']+'/'+tiltfilename2
			os.system('mv %s %s;mv %s.param %s.param' % (tiltfilename_full, tiltfilename_full2, seriesname, seriesname2))
			seriesname=seriesname2
			tiltfilename=tiltfilename2
			tiltfilename_full=tiltfilename_full2
		elif float(self.params['iteration']).is_integer():
			seriesname=base_seriesname
			it="%03d" % (int(self.params['iteration'])-1)
			basename='%s%s' % (seriesname,it)
			tiltfilename=basename+'.tlt'
			tiltfilename_full=self.params['rundir']+'/'+tiltfilename
		else:
			apDisplay.printError("--iteration should be either an integer > 0, 'Coarse', 'Coarse2', 'Imod', 'Manual', or 'Original'. Aborting.")
			sys.exit()
		
		paramfilename=seriesname+'.param'
		paramfilename_full=self.params['rundir']+'/'+paramfilename
		if (self.params['iteration'] == 'Imod') or (self.params['iteration'] == 'imod') or (self.params['iteration'] == 'IMOD') or (self.params['iteration'] == 'I') or (self.params['iteration'] == 'i'):
			paramfilename='coarse_'+base_seriesname+'.param'
			paramfilename_full=self.params['rundir']+'/'+paramfilename
		
		raw_dir_mrcs = self.params['rundir']+'/raw/*mrc'
		image_list=glob.glob(raw_dir_mrcs)
		random_mrc=mrc.read(image_list[1])
		dimy, dimx = random_mrc.shape
		
		if isinstance(self.params['tilt_azimuth'],float):
				apDisplay.printMsg("Changing tilt azimuth to %s" % self.params['tilt_azimuth'])
				apProTomo2Aligner.changeTiltAzimuth(tiltfilename_full, self.params['tilt_azimuth'])
			
		if self.params['exclude_angles'] != '':
			temp_tlt_file = os.path.join(os.path.dirname(tiltfilename_full),'excluded_angles.tlt')
			os.system('cp %s %s' % (tiltfilename_full, temp_tlt_file))
			tiltfilename_full = temp_tlt_file
			remove_tilt_angles=self.params['exclude_angles'].split(',')
			remove_image_by_tilt_angle=[]
			with open(tiltfilename_full,'r') as f:
				for line in f:
					if 'TILT ANGLE' in line:
						tilt_angle=float(line.split()[[i for i,x in enumerate(line.split()) if x == 'ANGLE'][0]+1])
						for angle in remove_tilt_angles:
							if ((float(angle) + 0.1) > tilt_angle) and ((float(angle) - 0.1) < tilt_angle):
								remove_image_by_tilt_angle.append(line.split()[[i for i,x in enumerate(line.split()) if x == 'IMAGE'][0]+1])
								if angle in remove_tilt_angles: remove_tilt_angles.remove(angle)
			if len(remove_tilt_angles) > 0:
				for tilt in remove_tilt_angles:
					apDisplay.printWarning("Tilt angle %s was not found in the .tlt file and thus was not removed." % tilt)
				apDisplay.printWarning("Removal of tilt images by tilt angles requires angles accurate to +-0.1 degrees.")
			for imagenumber in remove_image_by_tilt_angle:
				apProTomo2Aligner.removeImageFromTiltFile(tiltfilename_full, imagenumber, remove_refimg="False")
			apProTomo2Aligner.findMaxSearchArea(os.path.basename(tiltfilename_full), dimx, dimy)
			apDisplay.printMsg("Images %s have been removed from the .tlt file by user request" % remove_image_by_tilt_angle)
			
		if (self.params['positive'] < 90) or (self.params['negative'] > -90):
			temp_tlt_file = os.path.join(os.path.dirname(tiltfilename_full),'excluded_range.tlt')
			os.system('cp %s %s' % (tiltfilename_full, temp_tlt_file))
			tiltfilename_full = temp_tlt_file
			removed_images, mintilt, maxtilt = apProTomo2Aligner.removeHighTiltsFromTiltFile(tiltfilename_full, self.params['negative'], self.params['positive'])
			apProTomo2Aligner.findMaxSearchArea(os.path.basename(tiltfilename_full), dimx, dimy)
			apDisplay.printMsg("Images %s have been removed before manual alignment" % removed_images)
		if self.params['apply_corrs'] != 0:
			if float(self.params['iteration']).is_integer:
				it="%03d" % (int(self.params['iteration'])-1)
			else:
				apDisplay.printError("Must provide an integer for --iteration.")
				sys.exit()
			seriesname=base_seriesname
			basename='%s%s' % (seriesname,it)
			corrfile=basename+'.corr'
			corrfilename_full=self.params['rundir']+'/'+corrfile
			apProTomo2Aligner.shiftAlignmentByCorrs(tiltfilename_full, dimx, dimy, corrfilename_full, self.params['apply_corrs'])
		
		if (self.params['shift_x'] != 0) or (self.params['shift_y'] != 0):
			shifted=True
			apProTomo2Aligner.shiftAlignment(tiltfilename_full, dimx, dimy, self.params['shift_x'], self.params['shift_y'])
		else:
			shifted=False
		
		if (self.params['re-center_images'] == "True") and (shifted != True):
			apProTomo2Aligner.centerAlignment(tiltfilename_full, dimx, dimy)
		
		#Print out Protomo IMAGE == TILT ANGLE pairs
		cmd1="awk '/ORIGIN /{print}' %s | wc -l" % (tiltfilename_full)
		proc=subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
		(numimages, err) = proc.communicate()
		numimages=int(numimages)
		cmd2="awk '/IMAGE /{print $2}' %s | head -n +1" % (tiltfilename_full)
		proc=subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
		(tiltstart, err) = proc.communicate()
		tiltstart=int(tiltstart)
		for i in range(tiltstart-1,tiltstart+numimages+100):
			try: #If the image isn't in the .tlt file, skip it
				cmd="awk '/IMAGE %s /{print}' %s | awk '{for (j=1;j<=NF;j++) if($j ~/TILT/) print $(j+2)}'" % (i+1, tiltfilename_full)
				proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
				(tilt_angle, err) = proc.communicate()
				if tilt_angle:
					print "Protomo Image #%d is %s degrees" % (i+1, tilt_angle.rstrip('\r\n'))
			except:
				pass
		
		print ""
		apDisplay.printMsg("\033[1mAlign images manually (to within ~5% accuracy), Save, & Quit.\033[0m")
		apDisplay.printMsg("\033[1mQuick Manual Alignment instructions:\033[0m")
		apDisplay.printMsg("\033[1m    1) View > image, Actions > Show movie. Identify an image in the center of the overall shift range.\033[0m")
		apDisplay.printMsg("\033[1m    2) View > overlay. Set the image in 1) to the reference.\033[0m")
		apDisplay.printMsg("\033[1m    3) First try Actions > Align all. Then 'show movie' again. If it aligned, then File > Save, File > Quit.\033[0m")
		apDisplay.printMsg("\033[1m    4) If 3) failed, then manually align each nearest-neighbor images by dragging and pressing 'A' to align.\033[0m")
		apDisplay.printMsg("\033[1mNote: If you get a popup error, then use the Reset button to reset the current image, or Actions > revert to reset all images.\033[0m")
		apDisplay.printMsg("\033[1mTip: Hold the 'A' button to continually align.\033[0m")
		print ""
		
		manualparam = '%s/manual_%s.param' % (self.params['rundir'], base_seriesname)
		manuali3t = '%s/manual_%s.i3t' % (self.params['rundir'], base_seriesname)
		os.system('rm %s 2>/dev/null' % manuali3t)
		
		maxsearch_file=glob.glob(tiltfilename_full+'.maxsearch.*')
		if not maxsearch_file == 0:
			apProTomo2Aligner.findMaxSearchArea(os.path.basename(tiltfilename_full), dimx, dimy)
			maxsearch_file=glob.glob(tiltfilename_full+'.maxsearch.*')
		maxsearch_x = int(maxsearch_file[0].split('.')[-2])
		maxsearch_y = int(maxsearch_file[0].split('.')[-1])
		
		manual_x_size = apProTomo2Aligner.nextLargestSize(int(self.params['max_image_fraction']*maxsearch_x)+1)
		manual_y_size = apProTomo2Aligner.nextLargestSize(int(self.params['max_image_fraction']*maxsearch_y)+1)
		if self.params['center_all_images'] == "True":
			temp_tlt_file = os.path.join(os.path.dirname(tiltfilename_full),'manual_centered.tlt')
			os.system('cp %s %s' % (tiltfilename_full, temp_tlt_file))
			tiltfilename_full = temp_tlt_file
			apProTomo2Aligner.centerAllImages(tiltfilename_full, dimx, dimy)
			manual_x_size = apProTomo2Aligner.nextLargestSize(int(self.params['max_image_fraction']*dimx)+1)
			manual_y_size = apProTomo2Aligner.nextLargestSize(int(self.params['max_image_fraction']*dimy)+1)
		
		os.system('cp %s %s' % (paramfilename_full, manualparam))
		if (self.params['iteration'] == 'Manual') or (self.params['iteration'] == 'manual') or (self.params['iteration'] == 'M') or (self.params['iteration'] == 'm'):
			os.system("sed -i '/ S = /c\ S = %d' %s" % (self.params['sampling'], manualparam))
			os.system("sed -i '/ W = {/c\ W = { %d, %d }' %s" % (manual_x_size, manual_y_size, manualparam))
		else:
			os.system("sed -i '/AP sampling/c\ S = %d' %s" % (self.params['sampling'], manualparam))
			os.system("sed -i '/AP orig window/c\ W = { %d, %d }' %s" % (manual_x_size, manual_y_size, manualparam))
			os.system("sed -i '/preprocessing/c\ preprocessing: false' %s" % manualparam)
		os.system("sed -i '/width/c\     width: { %d, %d }' %s" % (manual_x_size, manual_y_size, manualparam))
		#os.system("sed -i '/consider using N/c\     width: { %d, %d }' %s" % (manual_x_size, manual_y_size, manualparam))
		#os.system("sed -i '/AP width2/c\     width: { %d, %d }' %s" % (int(manual_x_size*0.5), int(manual_y_size*0.5), manualparam))
		print "\033[92m(Don't worry about the following potential error: 'tomoalign-gui: could not load libi3tiffio.so, TiffioModuleDisabled')\033[0m"
		process = subprocess.Popen(["tomoalign-gui", "-log", "-tlt", "%s" % tiltfilename_full, "%s" % manualparam], stdout=subprocess.PIPE)
		stdout, stderr = process.communicate()
		
		if self.params['create_videos']:
			os.system("sed -i '/ S = /c\ S = 8' %s" % manualparam)
		manualparam=protomo.param(manualparam)
		manualseries=protomo.series(manualparam)
		manualtilt=self.params['rundir']+'manual_'+base_seriesname+'.tlt'
		manualseries.geom(0).write(manualtilt)
		
		if (self.params['re-center_images'] == "True") and (shifted != True):
			apProTomo2Aligner.centerAlignment(manualtilt, dimx, dimy)
		
		apProTomo2Aligner.findMaxSearchArea(os.path.basename(manualtilt), dimx, dimy)
		
		if self.params['create_videos']:
			os.system('rm -f %s/media/tiltseries/manual_* %s/media/reconstructions/manual_*' % (self.params['rundir'], self.params['rundir']))
			jobs1=[]
			jobs2=[]
			raw_path = self.params['rundir'] + 'raw'
			cmd="awk '/FILE /{print}' %s | wc -l" % (manualtilt)
			proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
			(rawimagecount, err) = proc.communicate()
			rawimagecount=int(rawimagecount)
			apDisplay.printMsg("Creating Manual Alignment tilt-series video...")
			jobs1.append(mp.Process(target=apProTomo2Aligner.makeTiltSeriesVideos, args=(base_seriesname, 0, manualtilt, rawimagecount, self.params['rundir'], raw_path, 0, 8, 'mrc', 'html5vid', 'true', "True", "Manual",)))
			for job in jobs1:
				job.start()
			manualseries.mapfile('out/manual_%s.img' % base_seriesname)
			apDisplay.printMsg("Generating Coarse Alignment reconstruction...")
			jobs2.append(mp.Process(target=apProTomo2Aligner.makeReconstructionVideos, args=(seriesname, 0, self.params['rundir'], 0, 0, 'false', 'out', 0, 8, 8, 0, 0, 'html5vid', 'false', "True", "Manual")))
			for job in jobs2:
				job.start()
		if self.params['create_videos']:
			for job in jobs1:
				job.join()
			for job in jobs2:
				job.join()
		
		#cleanup
		os.system('rm %s 2>/dev/null' % manuali3t)
		os.system('rm -rf %s' % self.params['rundir']+'/cache/')
		if self.params['center_all_images'] == "True":
			os.system('rm -rf %s' % tiltfilename_full)
		
		apDisplay.printMsg("Finished Manual Alignment for Tilt-Series #%s!\n" % self.params['tiltseries'])
		
		apProTomo2Aligner.printTips("Alignment")
		
		apDisplay.printMsg('Did everything blow up and now you\'re yelling at your computer screen?')
		apDisplay.printMsg('If so, kindly post your issue on the following Appion-Protomo Google group or email Alex at anoble@nysbc.org explaining the issue and include this log file.')
		apDisplay.printMsg('https://groups.google.com/forum/#!topic/appion-protomo')
		apDisplay.printMsg('If everything worked beautifully and you publish, please use the appropriate citations listed on the Appion webpage! You can also print out all citations by typing: protomo2manualaligner.py --citations')
		
		
#=====================
#=====================
if __name__ == '__main__':
	protomo2manualaligner = ProTomo2ManualAligner()
	protomo2manualaligner.start()
	protomo2manualaligner.close()
