#
# COPYRIGHT:
#       The Leginon software is Copyright under
#       Apache License, Version 2.0
#       For terms of the license agreement
#       see  http://leginon.org
#

import calibrationclient
from leginon import leginondata
import event
import instrument
import imagewatcher
import mosaic
import threading
import node
import targethandler
from pyami import convolver, imagefun, mrc, ordereddict
import numpy
import pyami.quietscipy
import scipy.ndimage as nd
import gui.wx.MosaicClickTargetFinder
import os
import math
import polygon
import raster
import presets
import time
import targetfinder
import imagehandler

try:
	set = set
except NameError:
	import sets
	set = sets.Set


class MosaicClickTargetFinder(targetfinder.ClickTargetFinder, imagehandler.ImageHandler):
	panelclass = gui.wx.MosaicClickTargetFinder.Panel
	settingsclass = leginondata.MosaicClickTargetFinderSettingsData
	defaultsettings = dict(targetfinder.ClickTargetFinder.defaultsettings)
	defaultsettings.update({

		# unlike other targetfinders, no wait is default
		'wait for done': False,
		#'no resubmit': True,
		# maybe not
		'calibration parameter': 'stage position',
		'scale image': True,
		'scale size': 512,
		'create on tile change': 'all',
		'lpf': {
			'on': True,
			'size': 5,
			'sigma': 1.4,
		},
		'threshold': 100.0,
		'blobs': {
			'on': True,
			'border': 0,
			'max': 100,
			'min size': 10,
			'max size': 10000,
			'min mean': 1000,
			'max mean': 20000,
			'min stdev': 10,
			'max stdev': 500,
		},
	})

	eventoutputs = targetfinder.ClickTargetFinder.eventoutputs + [event.MosaicDoneEvent]
	targetnames = ['acquisition','focus','preview','reference','done','Blobs']
	def __init__(self, id, session, managerlocation, **kwargs):
		self.mosaicselections = {}
		targetfinder.ClickTargetFinder.__init__(self, id, session, managerlocation, **kwargs)
		self.calclients = {
			'image shift': calibrationclient.ImageShiftCalibrationClient(self),
			'stage position': calibrationclient.StageCalibrationClient(self),
			'modeled stage position':
												calibrationclient.ModeledStageCalibrationClient(self)
		}
		self.images = {
			'Original': None,
			'Extra Crispy': None,
			'Filtered': None,
			'Thresholded': None
		}
		parameter = self.settings['calibration parameter']
		self.mosaic = mosaic.EMMosaic(self.calclients[parameter])
		self.mosaicimagelist = None
		self.mosaicimage = None
		self.mosaicimagescale = None
		self.mosaicimagedata = None
		self.convolver = convolver.Convolver()
		self.currentposition = []
		self.mosaiccreated = threading.Event()
		self.presetsclient = presets.PresetsClient(self)

		self.mosaic.setCalibrationClient(self.calclients[parameter])

		self.existing_targets = {}
		self.clearTiles()

		self.reference_target = None

		if self.__class__ == MosaicClickTargetFinder:
			self.start()

	# not complete
	def handleTargetListDone(self, targetlistdoneevent):
		if self.settings['create on tile change'] == 'final':
			self.logger.debug('create final')
			self.createMosaicImage()
			self.logger.debug('done create final')

	def getTargetDataList(self, typename):
		'''
		Get positions of the typename targets from atlas, publish the new ones,
		and then update self.existing_position_targets with the published one added.
		'''
		displayedtargetdata = {}
		target_positions_from_image = self.panel.getTargetPositions(typename)
		for coord_tuple in target_positions_from_image:
			##  check if it is an existing position with database target.
			if coord_tuple in self.existing_position_targets and self.existing_position_targets[coord_tuple]:
				# pop so that it has a smaller dictionary to check
				targetdata = self.existing_position_targets[coord_tuple].pop()
			else:
				# This is a new position, publish it
				c,r = coord_tuple
				targetdata = self.mosaicToTarget(typename, r, c)
			if coord_tuple not in displayedtargetdata:
				displayedtargetdata[coord_tuple] = []
			displayedtargetdata[coord_tuple].append(targetdata)
		# update self.existing_position_targets,  This is still a bit strange.
		for coord_tuple in displayedtargetdata:
			self.existing_position_targets[coord_tuple] = displayedtargetdata[coord_tuple]

	def getDisplayedReferenceTarget(self):
		try:
			column, row = self.panel.getTargetPositions('reference')[-1]
		except IndexError:
			return None
		imagedata, delta_row, delta_column = self._mosaicToTarget(row, column)
		return self.newReferenceTarget(imagedata, delta_row, delta_column)

	def submitTargets(self):
		self.userpause.set()
		try:
			if self.settings['autofinder']:
				# trigger onTargetsSubmitted in the gui.
				self.panel.targetsSubmitted()
				return
		except:
			pass

		if self.targetlist is None:
			self.targetlist = self.newTargetList()
			self.publish(self.targetlist, database=True, dbforce=True)

		if self.hasNewImageVersion():
			self.logger.error('New version of images were acquired after this atlas is generated')
			self.logger.error('You must refresh the map and repick the targets')
			# trigger onTargetsSubmitted in the gui.
			self.panel.targetsSubmitted()
			return

		# self.existing_position_targets becomes empty on the second
		# submit if not refreshed. 
		self.refreshDatabaseDisplayedTargets()
		# create target list
		self.logger.info('Submitting targets...')
		self.getTargetDataList('acquisition')
		self.getTargetDataList('focus')
		self.getTargetDataList('preview')
		try:
			self.publish(self.targetlist, pubevent=True)
		except node.PublishError, e:
			self.logger.error('Submitting acquisition targets failed')
		else:
			self.logger.info('Acquisition targets submitted on %s' % self.getMosaicLabel())

		reference_target = self.getDisplayedReferenceTarget()
		if reference_target is not None:
			try:
				self.publish(reference_target, database=True, pubevent=True)
			except node.PublishError, e:
				self.logger.error('Submitting reference target failed')
			else:
				self.logger.info('Reference target submitted on %s' % self.getMosaicLabel())
		self.logger.info('Done target submission')
		# trigger onTargetsSubmitted in the gui.
		self.panel.targetsSubmitted()

	def clearTiles(self):
		self.tilemap = {}
		self.imagemap = {}
		self.targetmap = {}
		self.mosaic.clear()
		self.targetlist = None
		if self.settings['create on tile change'] in ('all', 'final'):
			self.clearMosaicImage()

	def addTile(self, imagedata):
		self.logger.debug('addTile image: %s' % (imagedata.dbid,))
		imid = imagedata.dbid
		if imid in self.tilemap:
			self.logger.info('Image already in mosaic')
			return

		self.logger.info('Adding image to mosaic')
		newtile = self.mosaic.addTile(imagedata)
		self.tilemap[imid] = newtile
		self.imagemap[imid] = imagedata
		self.targetmap[imid] = {}
		for type in ('acquisition','focus'):
			targets = self.researchTargets(image=imagedata, type=type)
			if targets and self.targetlist is None:
				self.targetlist = targets[0]['list']
			self.targetmap[imid][type] = targets
		self.logger.info('Image added to mosaic')
		if self.targetlist:
			self.logger.debug('add tile targetlist %d' % (self.targetlist.dbid,))
			self.logger.debug( 'add tile, imid %d %s' % (imid, imagedata['filename']))
			self.logger.debug( 'add targetmap %d'% (len(self.targetmap[imid]['acquisition']),))

	def hasNewImageVersion(self):
		for id, imagedata in self.imagemap.items():
			recent_imagedata = self.researchImages(list=imagedata['list'],target=imagedata['target'])[-1]
			if recent_imagedata.dbid != imagedata.dbid:
				return True
		return False

	def targetsFromDatabase(self):
		'''
		This function sets the most recent version of the targets in targetmap and reference target.
		'''
		for id, imagedata in self.imagemap.items():
			recent_imagedata = self.researchImages(list=imagedata['list'],target=imagedata['target'])[-1]
			self.targetmap[id] = {}
			for type in ('acquisition','focus'):
				targets = self.researchTargets(image=recent_imagedata, type=type)
				### set my target list to same as first target found
				if targets and self.targetlist is None:
					self.targetlist = targets[0]['list']
				self.targetmap[id][type] = targets
		self.reference_target = self.getReferenceTarget()

	def refreshCurrentPosition(self):
		self.updateCurrentPosition()
		self.setTargets(self.currentposition, 'position')

	def updateCurrentPosition(self):
		'''
		update current stage position on the mosaic.
		Does not work if calibration parameter is image shift
		'''
		try:
			image = self.imagemap.values()[0]
		except:
			self.logger.exception('Need tiles and mosaic image')
			return
		# should get tem from data
		try:
			stagepos = self.instrument.tem.StagePosition
		except:
			stagepos = None

		if stagepos is None:
			self.currentposition = []
			self.logger.exception('could not get current position')
			return
		self.setCalibrationParameter()

		## self.mosaic knows the center, and need stagepos to integrate
		## modeled stage position (row,col)
		delta = self.mosaic.positionByCalibration(stagepos)
		## this is unscaled and relative to center of mosaic image
		moshape = self.mosaic.mosaicshape
		pos = moshape[0]/2+delta[0], moshape[1]/2+delta[1]
		pos = self.mosaic.scaled(pos)
		vcoord = pos[1],pos[0]
		### this is a list of targets, in this case, one target
		self.currentposition = [vcoord]

	def refreshDatabaseDisplayedTargets(self):
		self.logger.info('Getting targets from database...')
		if not self.hasNewImageVersion():
			self.targetsFromDatabase()
		else:
			self.logger.error('Can not refresh with new image version')
		# refresh but not set display.  Thefefore does not care about the returned values
		self.createExistingPositionTargets()

	def createExistingPositionTargets(self):
		# start fresh
		self.existing_position_targets = {}
		targets = {}
		donetargets = []
		for ttype in ('acquisition','focus'):
			targets[ttype] = []
			for id, targetlists in self.targetmap.items():
				if ttype not in targetlists.keys():
					targetlist = []
				else:
					targetlist = targetlists[ttype]
				for targetdata in targetlist:
					tile = self.tilemap[id]
					#tilepos = self.mosaic.getTilePosition(tile)
					r,c = self.targetToMosaic(tile, targetdata)
					vcoord = c,r
					if vcoord not in self.existing_position_targets:
						# a position without saved target as default.
						self.existing_position_targets[vcoord] = []
					if targetdata['status'] in ('done', 'aborted'):
						self.existing_position_targets[vcoord].append(targetdata)
						donetargets.append(vcoord)
					elif targetdata['status'] in ('new','processing'):
						self.existing_position_targets[vcoord].append(targetdata)
						targets[ttype].append(vcoord)
					else:
						# other status ignored (mainly NULL)
						pass
		return targets, donetargets

	def displayDatabaseTargets(self):

		self.logger.info('Getting targets from database...')
		if not self.hasNewImageVersion():
			self.targetsFromDatabase()
		else:
			self.loadMosaicTiles(self.getMosaicName())
		self.displayTargets()

	def displayTargets(self):
		if self.mosaicimage is None:
			self.logger.error('Create mosaic image before displaying targets')
			return
		self.logger.info('Displaying targets...')
		donetargets = []
		if self.__class__ != MosaicClickTargetFinder:
			self.setTargets([], 'region')

		#
		targets, donetargets = self.createExistingPositionTargets()
		for ttype in targets.keys():
			self.setTargets(targets[ttype], ttype)
		self.setTargets(donetargets, 'done')

		# ...
		reference_target = []
		if self.reference_target is not None:
			id = self.reference_target['image'].dbid
			try:
				tile = self.tilemap[id]
				y, x = self.targetToMosaic(tile, self.reference_target)
				reference_target = [(x, y)]
			except KeyError:
				pass
		self.setTargets(reference_target, 'reference')

		self.updateCurrentPosition()
		self.setTargets(self.currentposition, 'position')
		self.setTargets([], 'preview')
		n = 0
		for type in ('acquisition','focus'):
			n += len(targets[type])
		ndone = len(donetargets)
		self.logger.info('displayed %s targets (%s done)' % (n+ndone, ndone))

	def getMosaicImageList(self, targetlist):
		self.logger.debug('in getMosaicImageList')
		'''
		if not targetlist['mosaic']:
			self.logger.debug('target list not mosaic')
			raise RuntimeError('TargetListData for mosaic ImageListData should have mosaic=True')
		'''
		if self.mosaicimagelist and self.mosaicimagelist['targets'] is targetlist:
			### same targetlist we got before
			self.logger.debug('same targets')
			self.setMosaicName(targetlist)
			return self.mosaicimagelist
		self.logger.debug('new image list data')

		### clear mosaic here
		self.clearTiles()

		self.mosaicimagelist = leginondata.ImageListData(session=self.session, targets=targetlist)
		self.logger.debug('publishing new mosaic image list')
		self.publish(self.mosaicimagelist, database=True, dbforce=True)
		self.logger.debug('published new mosaic image list')
		self.setMosaicName(targetlist)
		return self.mosaicimagelist

	def processImageData(self, imagedata):
		'''
		different from ClickTargetFinder because findTargets is
		not per image, instead we have submitTargets.
		Each new image becomes a tile in a mosaic.
		'''
		self.logger.info('Processing inbound image data')
		### create a new imagelist if not already done
		targets = imagedata['target']['list']
		if not targets:
			self.logger.info('No targets to process')
			return
		imagelist = self.getMosaicImageList(targets)
		self.logger.debug('creating MosaicTileData for image %d' % (imagedata.dbid,))
		tiledata = leginondata.MosaicTileData(image=imagedata, list=imagelist, session=self.session)
		self.logger.debug('publishing MosaicTileData')
		self.publish(tiledata, database=True)
		self.setMosaicNameFromImageList(imagelist)
		self.logger.debug('published MosaicTileData')
		self.addTile(imagedata)

		if self.settings['create on tile change'] == 'all':
			self.logger.debug('create all')
			self.createMosaicImage()
			self.logger.debug('done create all')

		self.logger.debug('Image data processed')

	def hasMosaicImage(self):
		
		if self.mosaicimage is None or  self.mosaicimagescale is None:
			return False
		return True

	def publishMosaicImage(self):
		if not self.hasMosaicImage():
			self.logger.info('Generate a mosaic image before saving it')
			return
		self.logger.info('Saving mosaic image data')
		mosaicimagedata = leginondata.MosaicImageData()
		mosaicimagedata['session'] = self.session
		mosaicimagedata['list'] = self.mosaicimagelist
		mosaicimagedata['image'] = self.mosaicimage
		mosaicimagedata['scale'] = self.mosaicimagescale
		filename = 'mosaic'
		lab = self.mosaicimagelist['targets']['label']
		if lab:
			filename = filename + '_' + lab
		dim = self.mosaicimagescale
		filename = filename + '_' + str(dim)
		mosaicimagedata['filename'] = filename
		self.publish(mosaicimagedata, database=True)
		self.mosaicimagedata = mosaicimagedata
		self.logger.info('Mosaic saved')

	def _researchMosaicTileData(self,imagelist=None):
		tilequery = leginondata.MosaicTileData(session=self.session, list=imagelist)
		mosaictiles = self.research(datainstance=tilequery)
		return mosaictiles

	def researchMosaicTileData(self,imagelist=None):
		tiles = self._researchMosaicTileData(imagelist)
		mosaiclist = ordereddict.OrderedDict()
		for tile in tiles:
			imglist = tile['list']
			key = self.makeMosaicNameFromImageList(imglist)
			if key not in mosaiclist:
				mosaiclist[key] = imglist
		self.mosaicselections = mosaiclist
		return mosaiclist

	def getMosaicNames(self):
		self.researchMosaicTileData()
		return self.mosaicselections.keys()

	def setMosaicName(self, mosaicname):
		self.mosaicname = mosaicname

	def setMosaicNameFromImageList(self,list):
		key = self.makeMosaicNameFromImageList(list)
		self.setMosaicName(key)

	def makeMosaicNameFromImageList(self,imglist):
		label = '(no label)'
		if imglist['targets'] is not None:
			if imglist['targets']['label']:
				label = imglist['targets']['label']
			elif imglist['targets']['image'] and imglist['targets']['image']['preset'] and imglist['targets']['image']['target']:
				label = '%d%s' % (imglist['targets']['image']['target']['number'],imglist['targets']['image']['preset']['name'])
		key = '%s:  %s' % (imglist.dbid, label)
		return key

	def getMosaicLabel(self):
		bits = self.getMosaicName().split(':')
		label = ':'.join(bits[1:]).strip()
		return label

	def getMosaicName(self):
		'''
		return a name that has both image list dbid and label in this format: dbid: label
		'''
		return self.mosaicname

	def getMosaicTiles(self, mosaicname):
		return tiles

	def loadMosaicTiles(self, mosaicname):
		self.logger.info('Clearing mosaic')
		self.clearTiles()
		self.logger.info('Loading mosaic images')
		try:
			tile_imagelist = self.mosaicselections[mosaicname]
		except KeyError:
			# new inbound mosaic is not in selectionmapping. Refresh the list and try again
			self.researchMosaicTileData()
			if mosaicname not in self.mosaicselections.keys():
				raise ValueError
			else:
				tile_imagelist = self.mosaicselections[mosaicname]
		self.mosaicimagelist = tile_imagelist
		mosaicsession = self.mosaicimagelist['session']
		tiles = self._researchMosaicTileData(tile_imagelist)
		ntotal = len(tiles)
		if not ntotal:
			self.logger.info('no tiles in selected list')
			return
		for i, tile in enumerate(tiles):
			# create an instance model to query
			self.logger.info('Finding image %i of %i' % (i + 1, ntotal))
			imagedata = tile['image']
			recent_imagedata = self.researchImages(list=imagedata['list'],target=imagedata['target'])[-1]
			self.addTile(recent_imagedata)
		self.reference_target = self.getReferenceTarget()
		self.logger.info('Mosaic loaded (%i of %i images loaded successfully)' % (i+1, ntotal))
		if self.settings['create on tile change'] in ('all', 'final'):
			self.createMosaicImage()

	def targetToMosaic(self, tile, targetdata):
		shape = tile.image.shape
		drow = targetdata['delta row']
		dcol = targetdata['delta column']
		tilepos = drow+shape[0]/2, dcol+shape[1]/2
		mospos = self.mosaic.tile2mosaic(tile, tilepos)
		scaledpos = self.mosaic.scaled(mospos)
		return scaledpos

	def scaleToMosaic(self, d):
		shape = tile.image.shape
		drow = targetdata['delta row']
		dcol = targetdata['delta column']
		tilepos = drow+shape[0]/2, dcol+shape[1]/2
		mospos = self.mosaic.tile2mosaic(tile, tilepos)
		scaledpos = self.mosaic.scaled(mospos)
		return scaledpos

	def _mosaicToTarget(self, row, col):
		'''
		Convert mosaic position to target position on a tile image.
		'''
		self.logger.debug('mosaicToTarget r %s, c %s' % (row, col))
		unscaled = self.mosaic.unscaled((row,col))
		tile, pos = self.mosaic.mosaic2tile(unscaled)
		shape = tile.image.shape
		drow,dcol = pos[0]-shape[0]/2.0, pos[1]-shape[1]/2.0
		imagedata = tile.imagedata
		self.logger.debug('target tile image: %s, pos: %s' % (imagedata.dbid,pos))
		return imagedata, drow, dcol

	def mosaicToTarget(self, typename, row, col):
		'''
		Convert and publish the mosaic position to targetdata of the tile image.
		'''
		imagedata, drow, dcol = self._mosaicToTarget(row, col)
		### create a new target list if we don't have one already
		'''
		if self.targetlist is None:
			self.targetlist = self.newTargetList()
			self.publish(self.targetlist, database=True, dbforce=True)
		'''
		# publish as targets on most recent version of image to preserve adjusted z
		recent_imagedata = self.researchImages(list=imagedata['list'],target=imagedata['target'])[-1]
		targetdata = self.newTargetForTile(recent_imagedata, drow, dcol, type=typename, list=self.targetlist)
		## can we do dbforce here?  it might speed it up
		self.publish(targetdata, database=True)
		return targetdata

	def createMosaicImage(self):
		self.logger.info('creating mosaic image')

		self.setCalibrationParameter()

		if self.settings['scale image']:
			maxdim = self.settings['scale size']
		else:
			maxdim = None
		self.mosaicimagescale = maxdim
		try:
			self.mosaicimage = self.mosaic.getMosaicImage(maxdim)
		except Exception, e:
			self.logger.error('Failed Creating mosaic image: %s' % e)
		self.mosaicimagedata = None

		self.logger.info('Displaying mosaic image')
		self.setImage(self.mosaicimage, 'Image')
		self.logger.info('image displayed, displaying targets...')
		## imagedata would be full mosaic image
		#self.clickimage.imagedata = None
		self.displayTargets()
		self.beep()

	def clearMosaicImage(self):
		self.setImage(None, 'Image')
		self.mosaicimage = None
		self.mosaicimagescale = None
		self.mosaicimagedata = None

	def uiPublishMosaicImage(self):
		self.publishMosaicImage()

	def setCalibrationParameter(self):
		calclient = self.calclients[self.settings['calibration parameter']]
		self.mosaic.setCalibrationClient(calclient)

	def storeSquareFinderPrefs(self):
		prefs = leginondata.SquareFinderPrefsData()
		prefs['image'] = self.mosaicimagedata
		prefs['lpf-sigma'] = self.settings['lpf']['sigma']
		prefs['threshold'] = self.settings['threshold']
		prefs['border'] = self.settings['blobs']['border']
		prefs['maxblobs'] = self.settings['blobs']['max']
		prefs['minblobsize'] = self.settings['blobs']['min size']
		prefs['maxblobsize'] = self.settings['blobs']['max size']
		prefs['mean-min'] = self.settings['blobs']['min mean']
		prefs['mean-max'] = self.settings['blobs']['max mean']
		prefs['std-min'] = self.settings['blobs']['min stdev']
		prefs['std-max'] = self.settings['blobs']['max stdev']
		self.publish(prefs, database=True)
		return prefs


	def findSquares(self):
		if self.mosaicimagedata is None:
			message = 'You must save the current mosaic image before finding squares on it.'
			self.logger.error(message)
			return
		original_image = self.mosaicimagedata['image']

		message = 'finding squares'
		self.logger.info(message)

		sigma = self.settings['lpf']['sigma']
		kernel = convolver.gaussian_kernel(sigma)
		self.convolver.setKernel(kernel)
		image = self.convolver.convolve(image=original_image)
		self.setImage(image, 'Filtered')

		## threshold grid bars
		squares_thresh = self.settings['threshold']
		image = imagefun.threshold(image, squares_thresh)
		self.setImage(image, 'Thresholded')

		## find blobs
		blobs = imagefun.find_blobs(original_image, image,
																self.settings['blobs']['border'],
																self.settings['blobs']['max'],
																self.settings['blobs']['max size'],
																self.settings['blobs']['min size'])

		# show blob target and stats
		targets = self.blobStatsTargets(blobs)
		self.logger.info('Number of blobs: %s' % (len(targets),))
		self.setTargets(targets, 'Blobs')

		## use stats to find good ones
		mean_min = self.settings['blobs']['min mean']
		mean_max = self.settings['blobs']['max mean']
		std_min = self.settings['blobs']['min stdev']
		std_max = self.settings['blobs']['max stdev']
		targets = []
		prefs = self.storeSquareFinderPrefs()
		rows, columns = image.shape
		if blobs:
			blob_sizes = numpy.array(map((lambda x: x.stats['n']),blobs))
			self.logger.info('Mean blob size is %.1f' % ( blob_sizes.mean(),))
		for blob in blobs:
			row = blob.stats['center'][0]
			column = blob.stats['center'][1]
			mean = blob.stats['mean']
			std = blob.stats['stddev']
			stats = leginondata.SquareStatsData(prefs=prefs, row=row, column=column, mean=mean, stdev=std)
			if (mean_min <= mean <= mean_max) and (std_min <= std <= std_max):
				stats['good'] = True
				## create a display target
				targets.append((column,row))
			else:
				stats['good'] = False
			self.publish(stats, database=True)

		## display them
		self.setTargets(targets, 'acquisition')

		message = 'found %s squares' % (len(targets),)
		self.logger.info(message)

	def checkSettings(self,settings):
		# always queuing. No need to check "wait for process" conflict
		return []
