#!/usr/bin/env python
# This script wraps tilt-series upload to Appion to streamline the uploading of
# one or more TOMO4 tilt-series with one command.
# 
# Converts one or more TOMO4-formatted image stacks and txt files to be Appion-uploadable.
# A temporary directory is made and then removed for each stack.
# The stack is unstacked into the temp directory.
# Information is stripped from the txt to make a text file for upload to Appion.
# If the tilt-series is the first in a session, it is uploaded alone.
# Serially uploads each tilt-series if they are not the first in the session.
# Usage: Only use the webforms to generate commands because sessions are reserved.

import os
import sys
import time
import optparse
import subprocess
from glob import glob
from pyami import mrc
from datetime import datetime
from appionlib import apDisplay
from appionlib import apProTomo2Prep


def parseOptions():
	parser=optparse.OptionParser()
	parser.add_option('--session', dest='session',
		help= 'Session date, e.g. --sessionname=14sep04a')
	parser.add_option("--description", dest="description", default="",
		help="Run description")
	parser.add_option('--projectid', dest='projectid',
		help= 'Project id, e.g. --projectid=20')
	parser.add_option('--jobtype', dest='jobtype',
		help= 'Appion jobtype')
	parser.add_option('--expid', dest='expid',
		help= 'Appion experiment id, e.g. --expid=8514')
	parser.add_option('--voltage', dest='voltage', type="int",
		help= 'Microscope voltage in keV, e.g. --voltage=300')
	parser.add_option('--cs', dest='cs', type="float",
		help= 'Microscope spherical abberation, e.g. --cs=2.7')
	parser.add_option('--tomo4_stack', dest='tomo4_stack', default="",
		help= 'TOMO4 stack path, e.g. --tomo4_stack=<path_to_stack>')
	parser.add_option('--tomo4_txt', dest='tomo4_txt', default="",
		help= 'TOMO4-formatted txt file path, e.g. --tomo4_txt=<path_to_txt>')
	parser.add_option('--tomo4_rawtlt', dest='tomo4_rawtlt', default="",
		help= 'TOMO4 rawtlt file path, e.g. --tomo4_rawtlt=<path_to_rawtlt>')
	parser.add_option('--tomo4_dir', dest='tomo4_dir', default="",
		help= 'TOMO4 path to stack and txt files, e.g. --tomo4_txt=<path_to_dir>')
	parser.add_option('--per_image_dose', dest='per_image_dose', type="float",
		help= 'Per-tilt-image dose in e-/A^2, e.g. --per_image_dose=2')
	
	
	options, args=parser.parse_args()
	
	if len(args) != 0 or len(sys.argv) == 1:
		parser.print_help()
		sys.exit()
	
	return options


def tomo4toAppion(stack, txt, rawtlt, voltage, dose):
	'''
	Unstacks TOMO4 stack and creates Appion-formatted info file for upload from txt file.
	'''
	prefix = os.path.splitext(os.path.basename(stack))[0]
	prefix = prefix.replace('.','_')
	apDisplay.printMsg("Preparing %s for upload to Appion..." % prefix)
	stack_path = os.path.dirname(os.path.abspath(stack))
	temp_image_dir = "%s/%s_tmp" % (stack_path, prefix)
	os.system('mkdir %s 2>/dev/null' % temp_image_dir)
	stack_file = stack
	stack = mrc.read(stack)
	
	with open(rawtlt) as f:
		goniometer_angles = f.read().splitlines() 
	
	filename_angle_list=[]
	for tilt_image in range(1,len(stack)+1):
		filename = "%s/%s_%04d.mrc" % (temp_image_dir, prefix, tilt_image)
		mrc.write(stack[tilt_image-1], filename)
		filename_angle_list.append({'filename':filename, 'goniometer_angle':goniometer_angles[tilt_image-1]})
	
	cmd1="awk '/pixel /{print $5}' %s" % txt
	proc=subprocess.Popen(cmd1, stdout=subprocess.PIPE, shell=True)
	(pixelsize, err) = proc.communicate()
	pixelsize = float(pixelsize)
	if (pixelsize == 0.0):
		apDisplay.printWarning("The pixel size in the .txt file is 0.0. Using the pixelsize in the stack header instead...")
		cmd1b="header %s | grep spacing | awk '{print $4}'" % stack_file
		proc=subprocess.Popen(cmd1b, stdout=subprocess.PIPE, shell=True)
		(pixelsize, err) = proc.communicate()
		pixelsize = float(pixelsize)
		if (pixelsize == 0.0):
			apDisplay.printError("The pixel size in either the .txt file or stack header must not be 0! Edit the file to fix this and run the command again.")
	else:
		pixelsize = pixelsize*10
	cmd2="awk '/Binning/{print $2}' %s" % txt
	proc=subprocess.Popen(cmd2, stdout=subprocess.PIPE, shell=True)
	(binning, err) = proc.communicate()
	try:
		binning = float(binning)
	except:
		apDisplay.printWarning("Binning was not read properly. Binning has been set to 1 (this will affect your pixelsize if it's not 1!!!).")
		binning = 1
	cmd3="awk '/Microscope Magnification/{print $3}' %s" % txt
	proc=subprocess.Popen(cmd3, stdout=subprocess.PIPE, shell=True)
	(mag, err) = proc.communicate()
	mag = int(mag)
	cmd4="awk '/negative/{print $5}' %s" % txt
	proc=subprocess.Popen(cmd4, stdout=subprocess.PIPE, shell=True)
	(min_tilt, err) = proc.communicate()
	min_tilt = float(min_tilt)
	cmd5="awk '/positive/{print $5}' %s" % txt
	proc=subprocess.Popen(cmd5, stdout=subprocess.PIPE, shell=True)
	(max_tilt, err) = proc.communicate()
	max_tilt = float(max_tilt)
	cmd6="awk '/Low tilt step/{print $5}' %s" % txt
	proc=subprocess.Popen(cmd6, stdout=subprocess.PIPE, shell=True)
	(low_tilt_step, err) = proc.communicate()
	low_tilt_step = float(low_tilt_step)
	cmd7="awk '/High tilt switch/{print $5}' %s" % txt
	proc=subprocess.Popen(cmd7, stdout=subprocess.PIPE, shell=True)
	(high_tilt_switch, err) = proc.communicate()
	high_tilt_switch = float(high_tilt_switch)
	cmd8="awk '/High tilt step/{print $5}' %s" % txt
	proc=subprocess.Popen(cmd8, stdout=subprocess.PIPE, shell=True)
	(high_tilt_step, err) = proc.communicate()
	high_tilt_step = float(high_tilt_step)
	cmd9="awk '/Start tilt/{print}' %s | grep kipp | awk '{print $6}'" % txt
	proc=subprocess.Popen(cmd9, stdout=subprocess.PIPE, shell=True)
	(start_tilt, err) = proc.communicate()
	start_tilt = float(start_tilt)
	cmd10="awk '/efocus/{print $5}' %s" % txt
	proc=subprocess.Popen(cmd10, stdout=subprocess.PIPE, shell=True)
	(defocus, err) = proc.communicate()
	defocus = float(defocus)
	
	#Positive tilt-direction
	current_tilt = start_tilt
	counting_for_order = 1
	image_list=[]
	while current_tilt <= max_tilt:
		filename = "%s/%s_%04d.mrc" % (temp_image_dir, prefix, counting_for_order)
		
		for i in range(0,len(filename_angle_list)):
			goniometer_angle = float(filename_angle_list[i]['goniometer_angle'])
			if abs(current_tilt - goniometer_angle) < 0.3:
				tilt_angle = goniometer_angle
				filename = filename_angle_list[i]['filename']
		tilt_info = '%s\t%fe-10\t%d\t%d\t%d\t%fe-6\t%d\t%f\t%f\n' % (filename, pixelsize, binning, binning, mag, defocus, int(voltage)*1000, tilt_angle, dose)
		image_list.append({'order':counting_for_order, 'tilt_info':tilt_info})
		if current_tilt <= high_tilt_switch:
			current_tilt = current_tilt + low_tilt_step
		else:
			current_tilt = current_tilt + high_tilt_step
		counting_for_order = counting_for_order + 1
	
	#Negative tilt-direction
	current_tilt = start_tilt
	while current_tilt >= min_tilt:
		filename = "%s/%s_%04d.mrc" % (temp_image_dir, prefix, counting_for_order)
		
		if current_tilt <= high_tilt_switch:
			current_tilt = current_tilt - low_tilt_step
		else:
			current_tilt = current_tilt - high_tilt_step
		for i in range(0,len(filename_angle_list)):
			goniometer_angle = float(filename_angle_list[i]['goniometer_angle'])
			if abs(current_tilt - goniometer_angle) < 0.3:
				tilt_angle = goniometer_angle
				filename = filename_angle_list[i]['filename']
		tilt_info = '%s\t%fe-10\t%d\t%d\t%d\t%fe-6\t%d\t%f\t%f\n' % (filename, pixelsize, binning, binning, mag, defocus, int(voltage)*1000, tilt_angle, dose)
		image_list.append({'order':counting_for_order, 'tilt_info':tilt_info})
		counting_for_order = counting_for_order + 1
	
	time_sorted_image_list = sorted(image_list, key=lambda k: k['order'])
	info_file = os.path.join(temp_image_dir,'%s_info.txt' % prefix)
	info=open(info_file,'w')
	
	for image_number in range(0,len(stack)):
		info.write(time_sorted_image_list[image_number]['tilt_info'])
	info.close()
	
	return image_number+1, info_file, temp_image_dir


if __name__ == '__main__':
	options=parseOptions()
	
	if ((options.tomo4_stack != "" and options.tomo4_txt != "") or (options.tomo4_dir != "")):
		if ((options.tomo4_stack != "" and options.tomo4_txt != "") and (options.tomo4_dir == "")):
			#Uploading first tilt-series in a session
			tomo4_stack = apProTomo2Prep.cleanUpFilename(options.tomo4_stack)
			num_images, info_file, temp_image_dir = tomo4toAppion(tomo4_stack, options.tomo4_txt, options.tomo4_rawtlt, options.voltage, options.per_image_dose)
			
			cmd = 'imageloader.py --projectid='+options.projectid+' --session='+options.session+' --cs='+str(options.cs)+' --batchparams='+info_file+' --tiltgroup='+str(num_images)+' --description="'+options.description+'" --jobtype='+options.jobtype
			print cmd
			proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
			(out, err) = proc.communicate()
			os.system("rm -rf %s" % temp_image_dir)
		else: #Uploading one or more tilt-series to an existing session
			#Check that there are an equal number of .st/.mrc files and .txt files
			stack_files = glob("%s/*.st" % options.tomo4_dir)
			stack_files.extend(glob("%s/*.mrc" % options.tomo4_dir))
			stack_files = sorted(stack_files)
			txt_files = glob("%s/*.txt" % options.tomo4_dir)
			rawtlt_files = glob("%s/*.rawtlt" % options.tomo4_dir)
			if len(stack_files) == len(txt_files):
				if len(stack_files) == len(rawtlt_files):
					num_uploads = len(stack_files)
					for tiltseries in range(num_uploads):
						stack_file = stack_files[tiltseries]
						if os.path.exists(stack_file+'.txt'): #Check for file.st.txt
							txt_file = stack_file+'.txt'
						elif os.path.exists(os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0]+'.txt'): #Check for file.txt
							txt_file = os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0]+'.txt'
						elif os.path.exists(os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0].replace('_orig','')+'.txt'): #Check for file.txt without _orig
							txt_file = os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0].replace('_orig','')+'.txt'
						if os.path.exists(stack_file+'.rawtlt'): #Check for file.st.rawtlt
							rawtlt_file = stack_file+'.rawtlt'
						elif os.path.exists(os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0]+'.rawtlt'): #Check for file.rawtlt
							rawtlt_file = os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0]+'.rawtlt'
						elif os.path.exists(os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0].replace('_orig','')+'.rawtlt'): #Check for file.rawtlt without _orig
							rawtlt_file = os.path.dirname(os.path.abspath(stack_file))+'/'+os.path.splitext(os.path.basename(stack_file))[0].replace('_orig','')+'.rawtlt'
						stack_file = apProTomo2Prep.cleanUpFilename(stack_file)
						num_images, info_file, temp_image_dir = tomo4toAppion(stack_file, txt_file, rawtlt_file, options.voltage, options.per_image_dose)
						cmd = 'imageloader.py --projectid='+options.projectid+' --session='+options.session+' --cs='+str(options.cs)+' --batchparams='+info_file+' --tiltgroup='+str(num_images)+' --description="'+options.description+'" --expid='+options.expid+' --jobtype='+options.jobtype
						print cmd
						proc=subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
						(out, err) = proc.communicate()
						os.system("rm -rf %s" % temp_image_dir)
				else:
					apDisplay.printError("--tomo4_dir must contain an equal number of .st/.mrc and .rawtlt files.")
			else:
				apDisplay.printError("--tomo4_dir must contain an equal number of .st/.mrc and .txt files.")
	else:
		apDisplay.printError("You must provide either a path to a TOMO4 stack and txt file or to a directory with multiple stacks and txt files.")
	
