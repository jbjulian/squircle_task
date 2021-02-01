#!/usr/bin/env python

"""
Script for Squircle contextual memory behavioral training task

Script will ask for subject # as input.
Make sure required 3D objects (osgb files, in the objects directory), feedback smile images (tif files, in the smiles directory), and textures (jpg, in the textures directory) are in the path. Note that the osgb files are too large to host on github; they are available on Mendeley Data (they are available on Mendeley Data (doi:10.17632/jvm3fhpjwn.1). 
Data are output as text files in the dpath directory, defined below (line 51). It's currently set as '..\Data\TrainingData\\', and this directory must exist.
Output files are named TRAIN_tracking_<subject number>_<runNum number>.txt.
Output files have four columns: [time since session start, x-pos, y-pos, and orientation], and each trial's start, end, and target object are indicated in separate rows.
Participants control movement with wasd keys (can also be changed to arrows)
Note that for distal cue counterbalancing, distal cues need to be manually flipped across contexts (lines 115-173)
Requires Vizard VR toolkit.
"""

# Generic /Built-in
import os
import time

#Other libs
import viz
import viztask
import vizact
import vizinfo
import vizproximity
import vizshape
import vizcam
import numpy
import vizinput
import random

# Owned
__author__ = "Josh Julian"
__license__ = "MIT"

viz.fov(40)
viz.setMultiSample(4)
viz.go(viz.FULLSCREEN)
viz.mouse.setVisible(viz.OFF)
viz.antialias = 4


###############
## VARIABLES ##
###############

global subject
subject = vizinput.input('What is the sub number?') 
global runNum
#runNum = vizinput.input('What is the run rumber?') 
dpath = '..\Data\TrainingData\\'
runs = 6
#runNum = int(runNum)
subject = int(subject)

#tuple of test objects
TestObjects = ['cone', 'beachball', 'plant','pumpkin']
TestObjectLocs = [[(-4,0.07,9),(2,0.29,5),(-7,0.07,-4),(10,0.05,-5)] , [(4,0.07,9),(-2,0.29,5),(7,0.07,-4),(-10,0.05,-5)]]
scaleFactors = [0.15,1.8,1.25,1.8]


#trials per object
trials_per_object = 4
initial_collect_per_object = 2

#timing
ITI=2 #intertrial interval, in seconds

##env shape
global radius
radius = 14.5 #in meters, made global for convenience so be careful 

##ground
ground = vizshape.addPlane(size=(40.0,40.0),axis=vizshape.AXIS_Y)
ground.setPosition(0,0,0)
t1 = viz.addTexture('tex2.jpg',wrap=viz.REPEAT)
ground.texture(t1)
ground.texmat( viz.Matrix.scale(20,20,1) )

##sky color
viz.clearcolor(0.1, 0.1, 0.2)


###CONTEXT GEN FUNCTION####

def ContextGen(runNum):

	if runNum %2 == 0:
		if subject %2 == 0:
			context=1
		else:
			context=2 
	else:
		if subject %2 == 0:
			context=2
		else:
			context=1

	fname = dpath + 'TRAIN_tracking_'+str(subject)+'_'+ str(context) + '_' +str(runNum)+'.txt'

	#check for existing data file <-uncomment for actual testing, along with input function above
	if os.path.isfile(fname):
		print('file name already exists')
		viz.quit()

	#open data file
	global tracking_data
	tracking_data = open(fname, 'a')


	##############################
	## ENVIRONMENT AND CONTROLS ##
	##############################

	##distal cues: add some trees

	#distal cues
	if runNum < 2:
		global cue1 #sloppy making global but it works
		global cue2
		global cue3
		global cue4
		global cue5
		global cue6
		global cue7
		global cue8
		cue1 = viz.add('tree4.osgb')
		cue1.setPosition(-20,-10,70)
		cue1.setScale([2,2,2])
		cue2 = viz.add('tree6.osgb')
		cue2.setPosition(20,-1,-50)
		cue2.setScale([3,3,3])
		cue3 = viz.add('tree2.osgb')
		cue3.setPosition(20,-2,60)
		cue3.setScale([3,3,3])
		cue4 = viz.add('tree5.osgb') 
		cue4.setPosition(-20,-1,-60)
		cue4.setScale([3,3,3])

		cue5 = viz.add('tree10.osgb')
		cue5.setPosition(60,0,20)
		cue5.setScale([2.5,2.5,2.5])
		cue6 = viz.add('tree11.osgb')
		cue6.setPosition(-60,0,-20)
		cue6.setScale([5,5,5])
		cue7 = viz.add('tree12.osgb')
		cue7.setPosition(60,-5,-20)
		cue7.setScale([4,4,4])
		cue8 = viz.add('tree13.osgb') 
		cue8.setPosition(-60,-5,20)
		cue8.setScale([4,4,4])

	if context == 1: #context 1 is circle world
		cue3.visible(0)
		cue4.visible(0)
		cue1.visible(1)
		cue2.visible(1)

		cue5.visible(1)
		cue6.visible(1)
		cue7.visible(0)
		cue8.visible(0)

	else:
		cue3.visible(1)
		cue4.visible(1)
		cue1.visible(0)
		cue2.visible(0)

		cue5.visible(0)
		cue6.visible(0)
		cue7.visible(1)
		cue8.visible(1)

	#boundary elements - may need to adjust x,y positions of Square boundaries slightly to get rid of line between segments (this seems monitor dependent)
	if runNum < 2: 
		global boundary1
		global boundary2
		global boundary3
		global boundary4
		global boundary5
		global boundary6
		global boundary7
		global boundary8
		boundary1 = viz.add('CIRCLE.osgb')
		boundary1.setPosition(0.05,0,-0.05) 
		boundary2 = viz.add('CIRCLE.osgb')
		boundary2.setEuler( [ 90, 0, 0 ] ) 
		boundary2.setPosition(-0.05,0,-0.05) 
		boundary3 = viz.add('CIRCLE.osgb')
		boundary3.setEuler( [ -90, 0, 0 ] ) 
		boundary3.setPosition(0.05,0,0.05) 
		boundary4 = viz.add('CIRCLE.osgb')
		boundary4.setEuler( [ 180, 0, 0 ] )
		boundary4.setPosition(-0.05,0,0.05) 
		boundary5 = viz.add('SQUARE.osgb')
#		boundary5.setPosition(0.05,0,-0.05) 
		boundary6 = viz.add('SQUARE.osgb')
		boundary6.setEuler( [ 90, 0, 0 ] ) 
#		boundary6.setPosition(-0.05,0,-0.05) 
		boundary7 = viz.add('SQUARE.osgb')
		boundary7.setEuler( [ -90, 0, 0 ] ) 
#		boundary7.setPosition(0.05,0,0.05) 
		boundary8 = viz.add('SQUARE.osgb')
		boundary8.setEuler( [ 180, 0, 0 ] )
#		boundary8.setPosition(-0.05,0,0.05) 

##add boundary
	if (context == 1): #context 1 is circle world 
		boundary1.visible(1)
		boundary2.visible(1)
		boundary3.visible(1)
		boundary4.visible(1)
		boundary5.visible(0)
		boundary6.visible(0)
		boundary7.visible(0)
		boundary8.visible(0)

	else:#context 2 is square world:
		boundary5.visible(1)
		boundary6.visible(1)
		boundary7.visible(1)
		boundary8.visible(1)
		boundary1.visible(0)
		boundary2.visible(0)
		boundary3.visible(0)
		boundary4.visible(0)
		
	return context


##lighting
mylight = viz.addLight() 
mylight.enable() 
mylight.position(0, 10, 0)
mylight.spread(180) ##uniform ambient lighting 
mylight.intensity(2.5)

#setup keyboard controls
vizcam.KeyboardCamera(forward='w',
						turnRight='d',
						turnLeft='a',
						backward='s',
						left='æ',
						right='¨',
						moveMode=viz.REL_LOCAL,
						moveScale=1.1,
						turnScale=0.45)

#turn on collisions
viz.collision(viz.ON)

#######################
## PROXIMITY MANAGER ##
#######################

##Create proximity manager
global manager
manager = vizproximity.Manager()

#Add main viewpoint as proximity target'
global target
target = vizproximity.Target(viz.MainView)
manager.addTarget(target)

##################
##MATH FUNCTIONS##
##################

def pol2cart(rho, phi):
	x = rho * numpy.cos(phi)
	y = rho * numpy.sin(phi)
	return(x,y)


def computeError(corrLoc,actualLoc):
	error = numpy.sqrt(numpy.square(corrLoc[0]-actualLoc[0])+numpy.square(corrLoc[2]-actualLoc[2]))
#	#compute different feedback levels (1-5) for different levels of performance
	threshold = [3,5,7,9]
	if error < threshold[0]:
		feedback = 1
	elif error > threshold[0] and error < threshold[1]:
		feedback = 2
	elif error > threshold[1] and error < threshold[2]:
		feedback = 3
	elif error > threshold[2] and error < threshold[3]:
		feedback = 4
	elif error > threshold[3]:
		feedback = 5
	return(error,feedback)

##################
## INSTRUCTIONS ##
##################
##N.B. phase == 1 is collect, otherwise replace
def Instruction(objName,ITI,phase,feedback):

		viz.MainWindow.setScene(2)
		if phase:

			if feedback>0:
				smile = viz.add('smile' + str(feedback) + '.tif')
				feed = viz.addTexQuad(parent=viz.SCREEN,scene=2,size=[500,400])
				feed.setPosition([0.5, 0.5, 0]) #put quad in view 
				feed.texture(smile)
				yield viztask.waitTime(ITI-1)
				feed.visible(0)

			Message = 'Collect ' + objName

		else:
			Message = 'Replace ' + objName

		#info
		info = viz.addText(Message,viz.SCREEN,scene=2)
		info.fontSize(36)
		info.color(viz.WHITE)
		info.setPosition([0.4,0.5,0])
		info.visible(1)

		#wait for iti
		yield viztask.waitTime(ITI+1)
		info.visible(0)

def StartRun(runNum,openMess,closeMess):
	
	if openMess:
		viz.MainWindow.setScene(2)
		if runNum%2 == 0:
			con = 2
		else: 
			con = 1
		Message = 'Press t to start training in Arena ' + str(con)
		#info
		info = viz.addText(Message,viz.SCREEN,scene=2)
		info.fontSize(36)
		info.color(viz.WHITE)
		info.setPosition([0.3,0.5,0])
		info.visible(1)

		#wait for response
		yield viztask.waitKeyDown(['t','T'])
		info.visible(0)
		yield viztask.waitTime(ITI-1)
	else: 
		viz.MainWindow.setScene(2)
		Message = 'Good job!'
		#info
		info = viz.addText(Message,viz.SCREEN,scene=2)
		info.fontSize(36)
		info.color(viz.WHITE)
		info.setPosition([0.4,0.5,0])
		info.visible(1)
		yield viztask.waitTime(ITI)
		info.visible(0)
		if closeMess:
			Message = 'Training Complete. Please get experimenter'
			#info
			info = viz.addText(Message,viz.SCREEN,scene=2)
			info.fontSize(36)
			info.color(viz.WHITE)
			info.setPosition([0.3,0.5,0])
			info.visible(1)
			yield viztask.waitTime(ITI)
			info.visible(0)

#####################################
#######COLLECT PHASE FUNCTION #######
#####################################
def Collect(objName,objLoc,ScaleFac,tel):

		viz.MainWindow.setScene(1)
		
		#teleport to new location each trial?
		if tel:
			x , y = pol2cart(numpy.random.randint(12,radius), numpy.random.randint(0,360))
			viz.MainView.setPosition(x,0,y) 
			viz.MainView.setEuler(numpy.random.randint(0,360),0,0)

		#add object
		obj = viz.addChild(objName+'.osgb') 
		obj.setPosition(objLoc)
		obj.setScale([ScaleFac,ScaleFac,ScaleFac])

		sensor = vizproximity.addBoundingBoxSensor(obj,scale=(1.5,10,1.5))

		manager.addSensor(sensor)

		obj.visible(viz.ON)

		yield vizproximity.waitEnter(sensor)
		obj.remove()
		manager.removeSensor(sensor)

#####################################
#######COLLECT PHASE FUNCTION #######
#####################################
def Replace():

		viz.MainWindow.setScene(1)

		#teleport to new location each trial
		x , y = pol2cart(numpy.random.randint(10,radius), numpy.random.randint(0,360))
		viz.MainView.setPosition(x,0,y) 
		viz.MainView.setEuler(numpy.random.randint(0,360),0,0)

		#wait for response
		yield viztask.waitKeyDown(['p','P'])


##############################
#!! MAIN EXPERIMENTAL LOOP !!#
##############################
def EXPERIMENT(trials_per_object,initial_collect_per_object,TestObjects,TestObjectLocsALL,ITI,scaleFactors,runs):

	for r in range(runs):
		runNum = r+1
		context = ContextGen(runNum)
		#test object locations for this world
		TestObjectLocs = TestObjectLocsALL[context - 1]
		yield StartRun(runNum,1,0)

		#initial training, just collects
		if runNum < 3:
			Init_trials = []
			for n in range(initial_collect_per_object):
				Init_trials = numpy.random.permutation(len(TestObjects)).tolist()+Init_trials

			for nn in Init_trials:
				#get target object for collection
				objName = TestObjects[nn]
				objLoc = TestObjectLocs[nn]
				S=scaleFactors[nn]
				yield Instruction(objName,ITI,1,0)
				data = 'Start collect\n' 
				tracking_data.write(data)
				yield Collect(objName,objLoc,S,1)
				data = objName + ' Collected Initial' + '\n' 
				tracking_data.write(data)

		#post-initial training, replace/collect phases
		Trials = []
		for n in range(trials_per_object):
			Trials = numpy.random.permutation(len(TestObjects)).tolist()+Trials


		replaceError = []
		for nn in Trials:
			#get target object for replace/collect
			objName = TestObjects[nn]
			objLoc = TestObjectLocs[nn]
			S=scaleFactors[nn]
			#show instructions
			yield Instruction(objName,ITI,0,0)
			data = 'Start replace\n' 
			tracking_data.write(data)
			#replace phase
			yield Replace()
			error,feedback = computeError(viz.MainView.getPosition(),objLoc)
			data = 'Replaced ' + objName + ', ' + str(error) + '\n' 
			tracking_data.write(data)
			replaceError.append(error) #store replace error in a list, just to compute the mean at the end

			yield Instruction(objName,ITI,1,feedback)
			data = 'Start collect\n' 
			tracking_data.write(data)
			yield Collect(objName,objLoc,S,1) #have feedback every trial no matter what 
			data = 'Collected ' + objName + '\n' 
			tracking_data.write(data)

		#all done, shut down, printing mean error just for experimenter to check if needed
		print('Info: ' + str(numpy.mean(replaceError)))
		yield StartRun(runNum,0,0)
	
	yield StartRun(runNum,0,1)
	viz.quit()


##################################
##WRITE OUT PATH DATA FUNCTION####
##################################

#Get the tracking data. 
def getData():
	orientation = viz.MainView.getEuler()
	position = viz.MainView.getPosition()
	currTime = time.clock()
	#Make a string out of the data. 
	data = str(currTime-startTime) + '\t' + str(position[0]) + '\t' + str(position[2]) + '\t' +str(orientation[0]) + '\n' 
	#Write it to the tracking file.
	tracking_data.write(data)


##LAUNCH EXPERIMENT####
global startTime
startTime = time.clock()
viztask.schedule( EXPERIMENT(trials_per_object,initial_collect_per_object,TestObjects,TestObjectLocs,ITI,scaleFactors,runs))
vizact.ontimer(0.05, getData)


######### SCREEN SHOTS ########
#counterScreenShots=0;
# Method for taking screenshots
#def takeScreenshot():
#	global counterScreenShots
#	ScreenshotName='ScreenShotTraining_' + str(counterScreenShots)+'.jpg';
#	viz.window.screenCapture(ScreenshotName);
#	counterScreenShots=counterScreenShots+1;
#	
#vizact.onkeydown('s', takeScreenshot)
