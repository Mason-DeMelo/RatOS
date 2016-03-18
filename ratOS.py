#!/usr/bin/python

#Import Tkinter, Queue and Maze.py
from Tkinter import *
import Queue
import maze

#Toggles U3 device.
simulated = True

#create Tk Root
root = Tk()
running = False

#Functions
def toggleStart():
	global running 
	running = not running
	maze.rat.reset()
	startStop.configure(text = "Stop" if running else "Start")

def aTripped(arg):
	if not running: 
		return
	if maze.rat.comingFrom != "a":
			maze.rat.setPos(1)
			root.after(500, lambda: maze.rat.setPos(0))
			maze.dispenserA.dispense()
			maze.rat.atePellet()
			maze.rat.comingFrom = "a"
	else:
			maze.rat.setPos(1)
			root.after(500, lambda: maze.rat.setPos(2))
	root.after(500, lambda: maze.dispenserA.removePellet())
				
def bTripped(arg):
	if not running: 
		return
	if maze.rat.comingFrom != "b":
			maze.rat.setPos(3)
			root.after(500, lambda: maze.rat.setPos(4))
			maze.dispenserB.dispense()
			maze.rat.catePellet()
			maze.rat.comingFrom = "b"
	else:
			maze.rat.setPos(3)
			root.after(500, lambda: maze.rat.setPos(2))
	root.after(500, lambda: maze.dispenserB.removePellet())

def log(text):
		text = time.strftime("[%d/%m/%Y %H:%M:%S] ") + text
		listbox.insert(0, text)

#Graphics
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


#Labels
#Header Label
header = Label(root, image=headerPhoto)
#Dispenser Labels
dispenserA = Label(root, image= dispenser)
dispenserB = Label(root, image= dispenser)
#Sensor Labels
sensorA = Label(root, image=sensor)
sensorB = Label(root, image=sensor)
#Flooring Labels
flooring = list()
for i in range(0,5):
		flooring.append(Label(root, image=floor))


#Buttons
#Feeder Buttons
manualFeederA = Button(root, command= lambda:maze.dispenserA.dispense(), text="Feeder A")
manualFeederB = Button(root, command= lambda:maze.dispenserB.dispense(), text="Feeder B")
#Experiment Control Buttons
startStop = Button(root, text="Start", command = toggleStart)
reset = Button(root, text="Placeholder")


#Listbox for visual text output.
listbox = Listbox(root, width=65)


#Scales
#Threshold Scales
thresholdSliderA = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Threshold A", command=lambda x: maze.sensorA.updateThreshold(float(x)/100))
thresholdSliderB = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Threshold B", command=lambda x: maze.sensorB.updateThreshold(float(x)/100))



#Setup GUI Layout
#Place Header
header.grid(row=0, columnspan=5)
#Place Dispensers and Feeders
dispenserA.grid(row=1, column=0)
dispenserB.grid(row=1, column=4)
manualFeederA.grid(row=1, column=1)
manualFeederB.grid(row=1, column=3)
#Place Flooring
for i in range(5):
	flooring[i].grid(row=2, column=i)
#Place Sensors
sensorA.grid(row=3, column=1)
sensorB.grid(row=3, column=3)
#Place Threshold Sliders
thresholdSliderA.grid(row=4, column = 1)
thresholdSliderB.grid(row=4, column = 3)
#Place Buttons
startStop.grid(row=5, column=0)
reset.grid(row=6, column=0)
#listbox.grid(row=4, column=1, columnspan=3, rowspan=2)

#Update Graphics
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

		#Rat (Overrides anything else that might be in its square if running.)
		if running: flooring[maze.rat.getPos()].configure(image = ratOnFloor)

		root.after(25, updateGraphics)

#Event Queue
events = Queue.Queue()

#Update Events
def updateEvents():
    while events.qsize() > 0:
        thing = events.get()
        listbox.insert(0, thing.strip("<").strip(">"))
        root.event_generate(thing)
    root.after(23, updateEvents)
        
    

#Bind Events
root.bind("<<sensorATripped>>", aTripped)
root.bind("<<sensorBTripped>>", bTripped)

#Initialize Maze
maze = maze.Maze(root, events, simulated)

#Begin Updating Graphics and Start Main Loop
updateGraphics()
updateEvents()
root.mainloop()