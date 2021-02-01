#!/usr/bin/env python

"""
Script for Squircle contextual memory behavioral task used during fMRI scanning.

Script needs to be run separately for each scan run, and will ask for subject # and run #s as input.
Make sure required 3D objects (osgb files, in the objects directory), feedback smile images (tif files, in the smiles directory), and textures (jpg, in the textures directory) are in the path. Note that the osgb files are too large to host on github; they are available on Mendeley Data (they are available on Mendeley Data (doi:10.17632/jvm3fhpjwn.1). 
Data are output as text files in the dpath directory, defined below (line 51). It's currently set as '..\Data\TestingData\\', and this directory must exist.
Output files are named TEST_tracking_<subject number>_<runNum number>.txt.
Output files have four columns: [time since session start, x-pos, y-pos, and orientation], and each trial's start, end, and target object are indicated in separate rows.
Participants controlled movement in the VR environment using a button box. The mapping between the button box and movements is defined in lines 231-240
Note that for distal cue counterbalancing, distal cues need to be manually flipped across contexts (lines 111-167)
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
viz.vsync(viz.ON)

###################
##OPEN DATA FILE ##
###################

global runNum
subject = vizinput.input('What is the sub number?') 
runNum = vizinput.input('What is the run rumber?') 
dpath = '..\Data\TestingData\\'
runNum = int(runNum)
runLength = 8.075*60 #in seconds

fname = dpath + 'TEST_tracking_'+str(subject)+'_'+ str(runNum)+'.txt'

###check for existing data file <-uncomment for actual testing, along with input function above
if os.path.isfile(fname):
	print('file name already exists')
	viz.quit()

#open data file
tracking_data = open(fname, 'a')



###############
## VARIABLES ##
###############

#tuple of test objects
TestObjects = ['cone', 'beachball', 'plant','pumpkin']
TestObjectLocs = [[(-4,0.07,9),(2,0.29,5),(-7,0.07,-4),(10,0.05,-5)] , [(4,0.07,9),(-2,0.29,5),(7,0.07,-4),(-10,0.05,-5)]]
scaleFactors = [0.15,1.8,1.25,1.8]

#trials per object
trials_per_context = 20 #just generate a lot, as participants won't get through this many / run

#timing
ITI=2 #intertrial interval, in seconds

##env shape
global radius
radius = 14.5 #in meters, made global for convenience so be careful 

##############################
## ENVIRONMENT AND CONTROLS ##
##############################

##ground
ground = vizshape.addPlane(size=(40.0,40.0),axis=vizshape.AXIS_Y)
ground.setPosition(0,0,0)
t1 = viz.addTexture('tex2.jpg',wrap=viz.REPEAT)
ground.texture(t1)
ground.texmat( viz.Matrix.scale(20,20,1) )

ground2 = vizshape.addPlane(size=(40.0,40.0),axis=vizshape.AXIS_Y,scene=viz.Scene2)
ground2.setPosition(0,0,0)
ground2.texture(t1)
ground2.texmat( viz.Matrix.scale(20,20,1) )

ground3 = vizshape.addPlane(size=(40.0,40.0),axis=vizshape.AXIS_Y,scene=viz.Scene3)
ground3.setPosition(0,0,0)
ground3.texture(t1)
ground3.texmat( viz.Matrix.scale(20,20,1) )

##sky color
viz.clearcolor(0.1, 0.1, 0.2)


##distal cues: add some trees

#scene 1 is circle world
cue1 = viz.add('tree4.osgb')
cue1.setPosition(-20,-10,70)
cue1.setScale([2,2,2])
cue2 = viz.add('tree6.osgb')
cue2.setPosition(20,-1,-50)
cue2.setScale([3,3,3])
cue5 = viz.add('tree10.osgb')
cue5.setPosition(60,0,20)
cue5.setScale([2.5,2.5,2.5])
cue6 = viz.add('tree11.osgb')
cue6.setPosition(-60,0,-20)
cue6.setScale([5,5,5])


# scene 2 is square world
cue3 = viz.add('tree2.osgb',scene=viz.Scene2)
cue3.setPosition(20,-2,60)
cue3.setScale([3,3,3])
cue4 = viz.add('tree5.osgb',scene=viz.Scene2)
cue4.setPosition(-20,-1,-60)
cue4.setScale([3,3,3])
cue7 = viz.add('tree12.osgb',scene=viz.Scene2)
cue7.setPosition(60,-5,-20)
cue7.setScale([4,4,4])
cue8 = viz.add('tree13.osgb',scene=viz.Scene2) 
cue8.setPosition(-60,-5,20)
cue8.setScale([4,4,4])

#scene 3 is squircle
cue9 = viz.add('tree4.osgb',scene=viz.Scene3)
cue9.setPosition(-20,-10,70)
cue9.setScale([2,2,2])
cue10 = viz.add('tree6.osgb',scene=viz.Scene3)
cue10.setPosition(20,-1,-50)
cue10.setScale([3,3,3])
cue11 = viz.add('tree2.osgb',scene=viz.Scene3)
cue11.setPosition(20,-2,60)
cue11.setScale([3,3,3])
cue12 = viz.add('tree5.osgb',scene=viz.Scene3) 
cue12.setPosition(-20,-1,-60)
cue12.setScale([3,3,3])
cue13 = viz.add('tree10.osgb',scene=viz.Scene3)
cue13.setPosition(60,0,20)
cue13.setScale([2.5,2.5,2.5])
cue14 = viz.add('tree11.osgb',scene=viz.Scene3)
cue14.setPosition(-60,0,-20)
cue14.setScale([5,5,5])
cue15 = viz.add('tree12.osgb',scene=viz.Scene3)
cue15.setPosition(60,-5,-20)
cue15.setScale([4,4,4])
cue16 = viz.add('tree13.osgb',scene=viz.Scene3) 
cue16.setPosition(-60,-5,20)
cue16.setScale([4,4,4])

##add boundary

#context 1 is circle world 
boundary1 = viz.add('CIRCLE.osgb')
boundary1.setPosition(0.05,0,-0.05) 
boundary2 = viz.add('CIRCLE.osgb')
boundary2.setPosition(-0.05,0,-0.05) 
boundary2.setEuler( [ 90, 0, 0 ] ) 
boundary3 = viz.add('CIRCLE.osgb')
boundary3.setEuler( [ -90, 0, 0 ] ) 
boundary3.setPosition(0.05,0,0.05) 
boundary4 = viz.add('CIRCLE.osgb')
boundary4.setEuler( [ 180, 0, 0 ] ) 
boundary4.setPosition(-0.05,0,0.05) 

#context 2 is square world - may need to adjust x,y positions slightly to get rid of line between segments (this seems monitor dependent)
boundary5 = viz.add('SQUARE.osgb',scene=viz.Scene2)
boundary5.setPosition(0.0001,0,-0.0001) 
boundary6 = viz.add('SQUARE.osgb',scene=viz.Scene2)
boundary6.setEuler( [ 90, 0, 0 ] ) 
boundary6.setPosition(-0.0001,0,-0.00010) 
boundary7 = viz.add('SQUARE.osgb',scene=viz.Scene2)
boundary7.setEuler( [ -90, 0, 0 ] ) 
boundary7.setPosition(0.0001,0,0.00010) 
boundary8 = viz.add('SQUARE.osgb',scene=viz.Scene2)
boundary8.setEuler( [ 180, 0, 0 ] )
boundary8.setPosition(-0.0001,0,0.0001) 

#context 3 is squircle world 
boundary9 = viz.add('CIRCLE.osgb',scene=viz.Scene3)
boundary9.setPosition(0.05,0,-0.05) 
boundary10 = viz.add('SQUARE.osgb',scene=viz.Scene3)
boundary10.setEuler( [ 90, 0, 0 ] ) 
boundary10.setPosition(-0.05,0,-0.05) 
boundary11 = viz.add('SQUARE.osgb',scene=viz.Scene3)
boundary11.setEuler( [ -90, 0, 0 ] ) 
boundary11.setPosition(0.05,0,0.05) 
boundary12 = viz.add('CIRCLE.osgb',scene=viz.Scene3)
boundary12.setEuler( [ 180, 0, 0 ] ) 
boundary12.setPosition(-0.05,0,0.05) 


##lighting
intense = 2.5
mylight = viz.addLight() 
mylight.enable() 
mylight.position(0, 10, 0)
mylight.spread(180) ##uniform ambient lighting 
mylight.intensity(intense)

mylight2 = viz.addLight(scene=viz.Scene2) 
mylight2.enable() 
mylight2.position(0, 10, 0)
mylight2.spread(180) ##uniform ambient lighting 
mylight2.intensity(intense)

mylight3 = viz.addLight(scene=viz.Scene3) 
mylight3.enable() 
mylight3.position(0, 10, 0)
mylight3.spread(180) ##uniform ambient lighting 
mylight3.intensity(intense)


#setup keyboard controls
vizcam.KeyboardCamera(forward='c',
						turnRight='d',
						turnLeft='b',
						backward='´',
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
	return(error)


##################
## INSTRUCTIONS ##
##################
def Instruction(objName,ITI,endMessage):

		viz.MainWindow.setScene(4)

		if endMessage!=1:
			collectMessage = 'Replace ' + objName
			#info
			info = viz.addText(collectMessage,viz.SCREEN,scene=4)
			info.fontSize(36)
			info.color(viz.WHITE)
			info.setPosition([0.4,0.5,0])
			info.visible(1)

			#wait for iti
			yield viztask.waitTime(ITI)
			yield viztask.waitTime(numpy.random.randint(4)) #add random jitter, eventually add a wait for t here as well
			info.visible(0)
		else:
			error = objName
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
			smile = viz.add('smile' + str(feedback) + '.tif')
			feed = viz.addTexQuad(parent=viz.SCREEN,scene=4,size=[500,400])
			feed.setPosition([0.5, 0.5, 0]) #put quad in view 
			feed.texture(smile)
			yield viztask.waitTime(ITI+2)
			viz.quit()



#####################################
#######REPLACE PHASE FUNCTION #######
#####################################
def Replace(context):

		viz.MainWindow.setScene(context)

		#teleport to new location each trial
		x , y = pol2cart(numpy.random.randint(10,radius), numpy.random.randint(0,360))
		viz.MainView.setPosition(x,0,y)
        startAng = numpy.random.randint(0,360)
		viz.MainView.setEuler(startAng,0,0)

		#ADD rotation here
		deg = 0
		while deg < 360:
			viz.MainView.setPosition(x,0,y) 
			viz.MainView.setEuler(startAng + deg,0,0)
			deg = deg + 0.5
			yield viztask.waitTime(1 / 720)

		#wait for response
		yield viztask.waitKeyDown(['a','A'])


#####################################
########WAIT FOR TRIGGERS############
#####################################
def WaitForTrig(Quick):

	if Quick!=1:
		viz.MainWindow.setScene(4)
		#wait for trigger
		message= 'Run ' + str(runNum) +', waiting for T'
		waitT = viz.addText(message,viz.SCREEN,scene=4)
		waitT.fontSize(18)
		waitT.color(viz.RED)
		waitT.setPosition([0,0,0])
		waitT.visible(1)
		yield viztask.waitKeyDown(['s','S']) #trigger
		waitT.visible(0)
		startTime = time.clock()

	else: 
		yield viztask.waitKeyDown(['s','S']) #trigger


##############################
#!! MAIN EXPERIMENTAL LOOP !!#
##############################
def EXPERIMENT(trials_per_context,TestObjects,TestObjectLocs,ITI,scaleFactors,runLength):

	#replace phases
	Trials = []
	C = []

	c1 = [0, 0, 0, 0]
	c2 = c1
	c3 = c1
	for n in range(trials_per_context):
		if n%2==1: 
			tmp = numpy.random.permutation(3)+1
		else:
			tmp = numpy.random.permutation(2)+1
		C = C+tmp.tolist()

		for t in tmp.tolist():

			if t==1:
				min_n = min(c1)
				min_objs = [i for i, x in enumerate(c1) if x == min_n]
				obj = min_objs[random.randint(0,len(min_objs)-1)]
				c1[obj]=c1[obj]+1

			elif t==2:
				min_n = min(c2)
				min_objs = [i for i, x in enumerate(c2) if x == min_n]
				obj = min_objs[random.randint(0,len(min_objs)-1)]
				c2[obj]=c2[obj]+1

			else:
				min_n = min(c3)
				min_objs = [i for i, x in enumerate(c3) if x == min_n]
				obj = min_objs[random.randint(0,len(min_objs)-1)]
				c3[obj]=c3[obj]+1

			Trials = Trials + [obj]


	#allocate replaceError array and wait for trigger
	replaceError = []
	yield WaitForTrig(0)

	count = 0;

	for nn in Trials:

		#get context for replace
		context = C[count]
		if context==1:
			Cname = 'circle'
		elif context==2:
			Cname = 'square'
		else:
			Cname = 'squircle'

		#get target object for replace
		objName = TestObjects[nn]
		if context!=3:
			TOL = TestObjectLocs[context-1]
			objLoc = TOL[nn]

		#show instructions
		yield Instruction(objName,ITI,0)
		data = 'Start replace, ' + Cname + '\n' 
		tracking_data.write(data)

		#replace phase
		yield Replace(context)

		if context !=3:
			error = computeError(viz.MainView.getPosition(),objLoc)

		if context !=3:
			data = 'Replaced ' + Cname + ', ' + objName + ', ' + str(error) + '\n' 
			tracking_data.write(data)
			replaceError.append(error) #store replace error in a list, just to compute the mean at the end
		else:
			TOL = TestObjectLocs[0]
			objLoc = TOL[nn]
			pos = viz.MainView.getPosition()
			error1 = computeError(pos,objLoc)
			TOL = TestObjectLocs[1]
			objLoc = TOL[nn]
			error2 = computeError(pos,objLoc)
			if error1 < error2: 
				data = 'Replaced squircle, ' + objName + ', ' + str(1) + ', ' + str(error1) + ', ' + str(error2) + '\n'
			else:
				data = 'Replaced squircle, ' + objName + ', ' + str(2) + ', ' + str(error1) + ', ' + str(error2) + '\n'
			tracking_data.write(data)

		count += 1

		#show end message
		if time.clock() - startTime >= runLength:
			objName = numpy.mean(replaceError) #not really object name, actually average error for end message
			yield Instruction(objName,ITI,1)




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
viztask.schedule( EXPERIMENT(trials_per_context,TestObjects,TestObjectLocs,ITI,scaleFactors,runLength))
vizact.ontimer(0.05, getData)

######### SCREEN SHOTS ########
#counterScreenShots=0;
# Method for taking screenshots
#def takeScreenshot():
#	global counterScreenShots
#	ScreenshotName='TestenvironmentScreenShotTraining_' + str(counterScreenShots)+'.jpg';
#	viz.window.screenCapture(ScreenshotName);
#	counterScreenShots=counterScreenShots+1;
#	
#vizact.onkeydown('s', takeScreenshot)
