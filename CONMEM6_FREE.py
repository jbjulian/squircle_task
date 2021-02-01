#!/usr/bin/env python

"""
Script for free exploration in the Square and Circle contexts following the start of training.

Will ask for subject # as input.
Make sure required 3D objects (osgb files, in the objects directory) in the assets folder and feedback smile images (tif files, in the smiles directory) are in the path. Note that the osgb files are too large to host on github; they are available on Mendeley Data (doi:10.17632/jvm3fhpjwn.1).
No data are output.
Participant's freely explore the square and circle contexts (in different trials), and manually advance between the contexts at their own pace
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

runs = 2
ITI = 2

subject = int(subject)

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


	##############################
	## ENVIRONMENT AND CONTROLS ##
	##############################

	##distal cues: add some trees

	#distal cues
	if runNum < 2:
		global cue1
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

	#boundary elements - may need to adjust x,y positions slightly in the Square to get rid of line between segments (this seems monitor dependent)
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
vizcam.WalkNavigate(forward='w',
						backward='s',
						left='æ',
						right='¨',
						moveScale=1.1,
						turnScale=0.35)

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


##################
## INSTRUCTIONS ##
##################

def StartRun(runNum,openMess,closeMess):
	
	if openMess:
		viz.MainWindow.setScene(2)
		if runNum%2 == 0:
			con = 2
		else: 
			con = 1
		Message = 'Press t to start exploration of Arena ' + str(con)
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
			Message = 'Free Exploration Complete. Please get experimenter'
			#info
			info = viz.addText(Message,viz.SCREEN,scene=2)
			info.fontSize(36)
			info.color(viz.WHITE)
			info.setPosition([0.3,0.5,0])
			info.visible(1)
			yield viztask.waitTime(ITI)
			info.visible(0)

#####################################
#######FREE PHASE FUNCTION #######
#####################################
def Replace():

		viz.MainWindow.setScene(1)

		#teleport to new location each trial
		x , y = pol2cart(numpy.random.randint(10,radius), numpy.random.randint(0,360))
		viz.MainView.setPosition(x,0,y) 
		viz.MainView.setEuler(numpy.random.randint(0,360),0,0)

		#wait for response
		yield viztask.waitKeyDown(['b','B'])


##############################
#!! MAIN EXPERIMENTAL LOOP !!#
##############################
def EXPERIMENT(ITI,runs):

	for r in range(runs):
		runNum = r+1
		context = ContextGen(runNum)
		yield StartRun(runNum,1,0)
		yield Replace()

	yield StartRun(runNum,0,1)
	viz.quit()


##################################
##WRITE OUT PATH DATA FUNCTION####
##################################

##LAUNCH EXPERIMENT####
global startTime
startTime = time.clock()
viztask.schedule( EXPERIMENT(ITI,runs))




