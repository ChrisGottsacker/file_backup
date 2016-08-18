import datetime
from os import listdir
from os.path import abspath, basename, dirname, exists, getmtime, getsize, isfile, isdir, join
import inspect
import logging
from math import pow
from shutil import copytree, rmtree, copy
import sys


#used for naming backup folder and file comparisons
namingFormat = '%Y%j%H%M'
curDate = datetime.datetime.now()
curDateFormatted = curDate.strftime(namingFormat)

# used to calculate maxSizeToKeep
bytesPerMB = pow(2,20)

fromPath = []
toPath = []

pathIndex = 0

# exits if isErr
def sendError(errMsg):
	if(errMsg != ''):
		print "ERROR: " + errMsg
	sys.exit(0)

def addOriginPath(path):
	path = abspath(path)
	global pathIndex
	fromPath.insert(pathIndex,path)
	pathIndex+=1

def bkup():
	#check that each path is part of a pair
	if len(fromPath) != len(toPath):
		sendError('Uneven # of to/from paths: ')

	# copy file/dir fromPath[i] to toPath[i], del current @ toPath[i]
	i=0
	while(i<len(fromPath)):
		if exists(fromPath[i]):
			if isdir(toPath[i]) and exists(toPath[i]):	#del existing dir
				try:
					rmtree(toPath[i])
					print 'rmtree loop '+ str(i)
				except:
					print 'failed to remove dir during bkup(), loop ' +str(i)
			#copytree() to be used only with non-existing destination path
			if isdir(fromPath[i]) and exists(toPath[i])==False:
				try:
					copytree(fromPath[i],toPath[i])
					print 'copytree loop ' +str(i)
				except:
					print 'failed to copy dir, loop '+str(i)
					pass
			elif (isfile(fromPath[i])):
				# make necessary directory tree for file
				if not exists(dirname(toPath[i])):
					os.makedirs(dirname(toPath[i]))
				try:
					copy(fromPath[i],toPath[i])
					print 'copy loop '+str(i)
				except IOError as e:
					if e[0] == 2:
						print 'no such file/dir'
					print 'failed to copy file, loop '+str(i)
			i+=1
			print 'finsihed loop '+ str(i-1)
		else:
			sendError('path "'+fromPath[i]+'" does not exist.')

def rmBkups():
	#static reference to the list of files in directory destinationDir
	backups=listdir(destinationDir)

	print '\n#backups before removal loop: '+str(len(listdir(destinationDir)))

	i=0
	while i<len(backups):
		print 'on removal loop '+ str(i)
		bkupDirPath = join(destinationDir,backups[i])
		if isExcessive(backups[i]):
			if exists(bkupDirPath) and isdir(join(bkupDirPath)):
				#del the directory that was at this position at
				#the time that this loop started
				rmtree(bkupDirPath)
				print 'rmtree in backups loop '+ str(i)

		i+=1
	print '#backups after removal loop: '+str(len(listdir(destinationDir)))

def isExcessive(dirName):
	try:
		# convert directory name to datetime
		bkupDate = datetime.datetime.strptime(dirName,namingFormat)

		# get current size of backup directory
		size = getDirSize(destinationDir)

		# print 'size > maxSizeToKeep: ' + str(size > maxSizeToKeep)

		numBkups = len(listdir(destinationDir))
		# Always keep a minimum number of backups (minBkupsToKeep)
		# file/dir age and sum-total size of all backups are used as secondary conditions, files will be kept until a certain age unless the accumulated size of all backups exceeds the specified max. size, and vice versa
		if (numBkups > minBkupsToKeep) and ((curDate - bkupDate > ageToKeep) or (size > maxSizeToKeep)):
			return True
		else:
			return False
	except ValueError:
		print 'Invalid directory name: ' + dirName
		# skips removing directories with unexpected names
		return False

def genToPaths():
	i=0
	while i<len(fromPath):
		toPath.insert(i,destinationDir+'\\'+curDateFormatted+'\\'+basename(fromPath[i]))
		i+=1

def getDirSize(dirPath):
	dirSize = getsize(dirPath)

	for item in listdir(dirPath):
		if isdir(join(dirPath,item)):
			dirSize+=getsize(join(dirPath,item))
			dirSize+=getDirSize(join(dirPath,item))
			# print 'is dir',item, dirSize
		elif isfile(join(dirPath,item)):
			dirSize+=getsize(join(dirPath,item))
			# print 'is file',item,dirSize

	return dirSize


# choose destination parent directory for all backups
# \...\destinationDir\YYYYDDDHHMM\backup folder
# calling abspath() ensures proper formatting
destinationDir = abspath('C:\path\to\where\destination\directory')


#First pair
addOriginPath('C:\path\to\directory\or\file')

#Second pair
addOriginPath('C:\path\to\directory\or\file')

#Third pair...

# always keep this many backups, regardless of numMBtoKeep or ageToKeep
minBkupsToKeep = 10
# don't delete backups until their total size exceeds this value, or age exceeded
numMBtoKeep = 200
# don't delete backups until the backup is at least this old, or the total size of backups is exceeded
ageToKeep = datetime.timedelta(
	weeks = 0	,
	days = 10	,
	hours = 0	,
	minutes = 0	)



maxSizeToKeep = bytesPerMB*numMBtoKeep

genToPaths()
bkup()
rmBkups()




# TODO:
# -check filenames for proper format before assuming they are actually using namingFormat
# -test file(vs dir) backup
# -give destination dir potential to be unique for each origin dir
# -print error log to file in folder using Logging module
# -make sure Task scheduler knows if script fails so it can retry
