#!/usr/bin/python

#Import Tkinter
try:
		from Tkinter import *
except:
		from tkinter import *

import u3
import maze
import time
import random
import Queue

#Simulated Bool
simulated = False

#create Tk Root
root = Tk()

#Maze Variables
dispenserAPort = 1
dispenserBPort = 0
sensorAPort = 5
sensorBPort = 4
threshold = .19
timeout = 1

running = False

#Functions
def toggleStart():
	global running 
	running = not running

def feedA():
	#manual feedA
		maze.dispenserA.dispense()

def feedB():
	#manual feedB
		maze.dispenserB.dispense()

def a(arg):
	if not running: 
		return
	if maze.rat.comingFrom != "a":
			maze.rat.setPos(1)
			root.after(500, lambda: maze.rat.setPos(0))
			feedA()
			maze.rat.comingFrom = "a"
	else:
			maze.rat.setPos(1)
			root.after(500, lambda: maze.rat.setPos(2))
	root.after(500, lambda: maze.dispenserA.removePellet())
				
def b(arg):
	if not running: 
		return
	if maze.rat.comingFrom != "b":
			maze.rat.setPos(3)
			root.after(500, lambda: maze.rat.setPos(4))
			feedB()
			maze.rat.comingFrom = "b"
	else:
			maze.rat.setPos(3)
			root.after(500, lambda: maze.rat.setPos(2))
	root.after(500, lambda: maze.dispenserB.removePellet())

#Graphics
#Create Tk Window
root.title("RatOS")

#Load Photos
headerPhoto = PhotoImage(file="res/ratOS.gif")
floor = PhotoImage(file="res/floor.gif")
dispenser = PhotoImage(file="res/pelletDispenser.gif")
dispenserActive = PhotoImage(file="res/pelletDispenserActive.gif")
sensor = PhotoImage(file="res/sensor.gif")
sensorTripped = PhotoImage(file="res/sensorTripped.gif")
ratOnFloor = PhotoImage(file="res/ratOnFloor.gif")
pellet = PhotoImage(file="res/pelletOnFloor.gif")

#Create Labels and Buttons Needed For GUI
dispenserA = Label(root, image= dispenser)
dispenserB = Label(root, image= dispenser)

sensorA = Label(root, image=sensor)
sensorB = Label(root, image=sensor)

sampleRat = Label(root, image=ratOnFloor)

flooring = list()
for i in range(0,5):
		flooring.append(Label(root, image=floor))
header = Label(root, image=headerPhoto)

manualFeederA = Button(root, command=feedA, text="Feeder A")
manualFeederB = Button(root, command=feedB, text="Feeder B")

startStop = Button(root, text="Start", command = toggleStart)
reset = Button(root, text="Placeholder")

listbox = Listbox(root, width=65)

thresholdSliderA = Scale(root, from_=100, to=0, command = lambda x: maze.sensorA.updateThreshold(float(x)/100))
thresholdSliderB = Scale(root, from_=100, to=0, command = lambda x: maze.sensorB.updateThreshold(float(x)/100))

#Place Rat In Center on Floor
flooring[2].configure(image=ratOnFloor)

#Setup GUI Layout
header.grid(row=0, columnspan=5)

dispenserA.grid(row=1, column=0)
manualFeederA.grid(row=1, column=1)
manualFeederB.grid(row=1, column=3)
dispenserB.grid(row=1, column=4)

flooring[0].grid(row=2, column=0)
flooring[1].grid(row=2, column=1)
flooring[2].grid(row=2, column=2)
flooring[3].grid(row=2, column=3)
flooring[4].grid(row=2, column=4)

sensorA.grid(row=3, column=1)
sensorB.grid(row=3, column=3)

startStop.grid(row=4, column=0)
reset.grid(row=5, column=0)

listbox.grid(row=4, column=1, columnspan=3, rowspan=2)
thresholdSliderA.grid(row=4, column = 4)
thresholdSliderB.grid(row=4, column = 5)

#Function Declarations
def log(text):
		text = time.strftime("[%d/%m/%Y %H:%M:%S] ") + text
		listbox.insert(0, text)

def updateGraphics():
		
		#Floor
		for i in flooring:
			i.configure(image= floor)

		#Dispenser A
		if maze.dispenserA.Status:
			dispenserA.configure(image = dispenserActive)
		else:
			dispenserA.configure(image = dispenser)

		#Pellet A
		if maze.dispenserA.pellet:
			flooring[0].configure(image = pellet)
		else:
			flooring[0].configure(image = floor)
		
		#Dispenser B
		if maze.dispenserB.Status:
			dispenserB.configure(image = dispenserActive)
		else:
			dispenserB.configure(image = dispenser)

		#Pellet B
		if maze.dispenserB.pellet:
			flooring[4].configure(image = pellet)
		else:
			flooring[4].configure(image = floor)

		#Sensor A
		if maze.sensorA.Status:
			sensorA.configure(image = sensorTripped)
		else:
			sensorA.configure(image = sensor)

		#Sensor B
		if maze.sensorB.Status:
			sensorB.configure(image = sensorTripped)
		else:
			sensorB.configure(image = sensor)

		#Rat (Overrides anything else that might be in it's square)
		flooring[maze.rat.getPos()].configure(image = ratOnFloor)

		root.after(25, updateGraphics)

#Event Queue
events = Queue.Queue()

#Update Events
def updateEvents():
    while events.qsize() > 0:
        thing = events.get()
        print thing
        root.event_generate(thing)
    root.after(23, updateEvents)
        
    

#Bind Events
root.bind("<<sensorATripped>>", a)
root.bind("<<sensorBTripped>>", b)

#Initialize Maze
maze = maze.Maze(root, events, dispenserAPort, dispenserBPort, sensorAPort, sensorBPort, threshold, timeout, simulated)

#Begin Updating Graphics and Start Main Loop
updateGraphics()
updateEvents()
root.mainloop()

