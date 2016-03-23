#!/usr/bin/python

#Import Tkinter, Queue and Maze.py
from Tkinter import *
import tkMessageBox
import Queue
import time
import maze
import logger

#Toggles U3 device.
simulated = True

#create Tk Root
root = Tk()
root.tk_setPalette(background='#D8D8D8')
root.title("RatOS")
root.wm_iconbitmap(r"res/Rat.ico")
running = False
saved = True

#Load Config
configFile = open("ratOS.cfg", "r")
config = dict()
for line in configFile:
	line = line.split()
	config[line[0]] = int(line[1])
configFile.close()

#Create Logger
logger = logger.Logger()

#Functions
def toggleStart():
	global running
	global saved

	if not saved and not running and not tkMessageBox.askokcancel("Are you sure?", "You haven't saved this data! This recording will be lost if you continue."):
		return

	running = not running
	saved = False

	if running:
		maze.rat.reset()
		maze.rat.startTimer()
	else:
		maze.rat.stopTimer()

	saveButton.configure(state= DISABLED if running else NORMAL, bg= "light grey" if running else "yellow")
	startStop.configure(text = "Stop" if running else "Start", bg = "Red" if running else "Green")

def save():
	global saved

	theRatNumber = ratNumber.get()
	date = time.strftime("%m/%d/%y")
	currentTime = time.strftime("%H:%M:%S")
	duration = maze.rat.getTime()
	cycles = maze.rat.pelletsEaten
	theComment = str(comments.get("1.0",END)).strip("\n")
	theExperimenter = experimenter.get()
	
	try:
		logger.updateLog(theRatNumber, date, currentTime, duration, cycles, theComment,theExperimenter)
	except RuntimeError:
		tkMessageBox.showerror("Failure","You did not complete the form!")
		return
	except Exception:
		tkMessageBox.showerror("Failure","Please close the excel document and try again.")
		return

	saved = True
	comments.delete("1.0",END)
	saveButton.configure(state= DISABLED, bg= "light grey")
	maze.rat.reset()

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
			maze.rat.atePellet()
			maze.rat.comingFrom = "b"
	else:
			maze.rat.setPos(3)
			root.after(500, lambda: maze.rat.setPos(2))
	root.after(500, lambda: maze.dispenserB.removePellet())

def log(text):
		text = time.strftime("[%d/%m/%Y %H:%M:%S] ") + text
		listbox.insert(0, text)

def on_close():
	#Update and save config file
	with open("ratOS.cfg", "w") as file_:
		file_.write("sensorAThreshold " + str(thresholdSliderA.get()) +"\n" +
					"sensorBThreshold " + str(thresholdSliderB.get()))
	#Close
	root.destroy()

#Graphics
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
startStop = Button(root, text="Start", command = toggleStart, bg="Green")
saveButton = Button(root, text="Save", command=save, state=DISABLED, bg="light grey")

#Listbox for visual text output.
listbox = Listbox(root, width=65)


#Scales
#Threshold Scales
thresholdSliderA = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Threshold A", command=lambda x: maze.sensorA.updateThreshold(float(x)/100), bg='#D8D8D8')
thresholdSliderB = Scale(root, from_=0, to=100, orient=HORIZONTAL, label="Threshold B", command=lambda x: maze.sensorB.updateThreshold(float(x)/100), bg='#D8D8D8')
thresholdSliderA.set(config['sensorAThreshold'])
thresholdSliderB.set(config['sensorBThreshold'])

#Entries and Their Labels
#Rat Number
ratNumber = Entry(root, width=4, borderwidth=3, bg="white")
ratNumberLabel = Label(text="Rat Number:")
#Experimenter Initials
experimenter = Entry(root, width = 4, borderwidth=3, bg="white")
experimenterLabel = Label(text="Experimenter:")
#Comments
comments = Text(root, width=35, height=5, borderwidth=3, wrap=WORD, bg="white")
commentsLabel = Label(text="Comments:")

#Uneditable Data
pelletsEatenLabel = Label(text="Pellets Eaten:   0")
timeElapsedLabel = Label(text="Time Elapsed: None")

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
thresholdSliderA.grid(row=4, column=1)
thresholdSliderB.grid(row=4, column=3)
#Place Buttons
startStop.grid(row=5, column=0)
saveButton.grid(row=7, column=0)

#Place User Input Fields
#RatNumber
ratNumberLabel.grid(row=5,column=1,sticky=E)
ratNumber.grid(row=5, column=2,sticky=W)
#Experimenter
experimenterLabel.grid(row=6,column=1,sticky=E)
experimenter.grid(row=6,column=2,sticky=W)
#Comments
commentsLabel.grid(row=7, column=1, sticky=E+N)
comments.grid(row=7,column=2, columnspan= 3, rowspan=2, sticky=W)

#Place Uneditable Data Fields
#Pellets Eaten
pelletsEatenLabel.grid(row=5, column=3, sticky=W)
#Time Elapsed
timeElapsedLabel.grid(row=6, column=3, sticky=W)


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

		#Pellets Eaten Label
		pelletsEatenLabel.configure(text="Pellets Eaten:   "+str(maze.rat.pelletsEaten))
		timeElapsedLabel.configure(text="Time Elapsed: "+str(maze.rat.getTime()))
		root.after(25, updateGraphics)

#Event Queue
events = Queue.Queue()

#Update Events
def updateEvents():
    while events.qsize() > 0:
        thing = events.get()
        root.event_generate(thing)
    root.after(23, updateEvents)
    
        
#Bind Events
root.bind("<<sensorATripped>>", aTripped)
root.bind("<<sensorBTripped>>", bTripped)
root.bind("<<dispenserADispensed>>", lambda a: maze.outA.signal())
root.bind("<<dispenserBDispensed>>", lambda a: maze.outB.signal())

root.protocol("WM_DELETE_WINDOW", on_close)

#Initialize Maze
maze = maze.Maze(root, events, simulated)

#Begin Updating Graphics and Start Main Loop
updateGraphics()
updateEvents()
root.mainloop()
