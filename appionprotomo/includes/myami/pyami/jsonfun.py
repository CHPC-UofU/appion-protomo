#!/usr/bin/env python
import os
import sys
import json
import numpy
import sinedon
from sinedon import dbconfig

class DataJsonLoader(object):
	def __init__(self, sinedon_data_module):
		self.db = sinedon_data_module
		self.alldata = []

	def makequery(self,classname,kwargs):
		'''
		Make SQL query of leginondata from class name and keyword arguments.
		'''
		q = getattr(self.db,classname)()
		for key in kwargs.keys():
			# leginondata keys never contains '_'
			realkey = key.replace('_',' ')
			if type(kwargs[key]) == type([]):
				if len(kwargs[key]) > 0:
					if type(kwargs[key][0]) == type([]):
						# json export saves coordinate tuple as list.  Need to change back in import
						kwargs[key] = map((lambda x: tuple(x)),kwargs[key])
			q[realkey] = kwargs[key]
		return q

	def readJsonFile(self,filename='test.json'):
		f =open(filename,'r')
		self.alldata = json.loads(f.read())
		# convert list of list to numpy 2D array
		for i,datadict in enumerate(self.alldata):
			classname = datadict.keys()[0]
			# field and value
			for key in datadict[classname]:
				value = datadict[classname][key]
				if isinstance(value,list) and all(isinstance(elem,list) for elem in value):
					self.alldata[i][classname][key] = numpy.array(value)

class DataJsonMaker(object):
	def __init__(self, sinedon_data_module):
		self.db = sinedon_data_module
		print 'jsonmaker __init__'
		self.alldata = []
		self.ignorelist = ['session',]
		pass

	def makequery(self,classname,kwargs):
		'''
		Make SQL query of leginondata from class name and keyword arguments.
		'''
		q = getattr(self.db,classname)()
		for key in kwargs.keys():
			# leginondata keys never contains '_'
			realkey = key.replace('_',' ')
			q[realkey] = kwargs[key]
		return q

	def makeTimeStringFromTimeStamp(self,timestamp):
		t = timestamp
		return '%04d%02d%02d%02d%02d%02d' % (t.year,t.month,t.day,t.hour,t.minute,t.second)

	def research(self,q,most_recent=False):
		'''
		Query results from source database. Sorted by entry time. Oldest fist
		'''
		if most_recent:
			r = q.query(results=1)
			if r:
				return r[0]
		else:
			r = q.query()
			r.reverse()
		return r

	def publish(self,results):
		'''
		Publish query results to export list without ignored reference
		'''
		if not results:
			return
			
		for r in results:
			classname = r.__class__.__name__
			data = {}
			for k in r.keys():
				if k not in self.ignorelist:
					# also ignore any reference ?
					if hasattr(r[k],'dbid'):
						pass
					else:
						if type(r[k]).__module__=='numpy':
							data[k] = r[k].tolist()
						else:
							data[k] = r[k]
			self.alldata.append({classname:data})

	def writeJsonFile(self,filename='test.json'):
		print 'writing %d records into %s' % (len(self.alldata),filename)
		jstr = json.dumps(self.alldata, indent=2, separators=(',',':'))
		f = open(filename,'w')
		f.write(jstr)
		f.close()

def testWrite():
	from leginon import leginondata
	app = DataJsonMaker(leginondata)
	q = app.makequery('UserData',{'firstname':'Anchi'})
	r = app.research(q)
	app.publish(r)
	app.writeJsonFile('test.json')

def testLoad():
	from leginon import leginondata
	app = DataJsonLoader(leginondata)
	app.readJsonFile('test.json')
	for item in app.alldata:
		# each item is a single key dictionary
		classname = item.keys()[0]
		key_value_pair = item[classname]
		q = app.makequery(classname,key_value_pair)
		print q
		print q.query()

if __name__ == '__main__':
	testLoad()
