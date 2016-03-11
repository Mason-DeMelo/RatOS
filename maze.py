import u3
try:
        from Tkinter import *
except:
        from tkinter import *
from threading import Thread
from time import sleep

class FIODevice():

    def __init__(self, events, root, U3Device, FIOPort):
        self.root = root
        self.events = events
        self.d = U3Device
        self.port = FIOPort
        self.Status = False

    def setStatus(self, status):
                if status:
                        self.Status = True
                else:
                        self.Status = False


class Dispenser(FIODevice):

    def __init__(self, root, events, U3Device, FIOPort):
        FIODevice.__init__(self, root, events, U3Device, FIOPort)
        self.pellet = False
        self.d.configDigital(self.port)
        self.d.setFIOState(self.port)

    def dispense(self):
        self.pellet = True
        self.Status = True
        self.d.configAnalog(self.port)
        self.events.put("<<dispensed>>")
        self.root.after(500, lambda: self.d.configDigital(self.port))
        self.root.after(500, lambda: self.setStatus(False))

    def removePellet(self):
        self.pellet = False

class Sensor(FIODevice):

    def __init__(self, root, events, U3Device, FIOPort, Threshold, Timeout, Name):
        FIODevice.__init__(self, root, events, U3Device, FIOPort)
        self.Threshold = Threshold
        self.Timeout = Timeout
        self.name = Name
        self.d.configAnalog(self.port)
        self.thread = Thread(target = self.startListener)
        self.thread.setDaemon(True)
        self.thread.start()

    def updateThreshold(self, value):
        self.Threshold = value
    
    def startListener(self):
        while True:
            if self.d.getAIN(self.port) < self.Threshold:
                    print(self.name, self.d.getAIN(self.port))
                    #self.root.event_generate("<<sensor"+self.name+"Tripped>>")
                    self.events.put("<<sensor"+self.name+"Tripped>>")
                    self.Status = True
                    sleep(self.Timeout)
                    while self.d.getAIN(self.port) < self.Threshold:
                        pass
            self.Status = False

class Rat():

    def __init__(self, pos = 2):
        self.pos = pos
        self.comingFrom = None

    def setPos(self, pos):
        self.pos = pos

    def getPos(self):
        return self.pos

    def setComingFrom(self, side):
        self.comingFrom = side

    def getComingFrom(self):
        return self.comingFrom


class Maze():

        def __init__(self, events, root, dispenserAPort, dispenserBPort, sensorAPort, sensorBPort, Threshold, Timeout, simulated):
            if simulated: 
                self.d = fakeU3(root)
            else:
                self.d = u3.U3()
            self.root = root
            self.rat = Rat()
            self.dispenserA = Dispenser(root, events, self.d, dispenserAPort)
            self.dispenserB = Dispenser(root, events, self.d, dispenserBPort)
            self.sensorA = Sensor(root, events, self.d, sensorAPort, Threshold, Timeout, "A")
            self.sensorB = Sensor(root, events, self.d, sensorBPort, Threshold, Timeout, "B")

        def pelletExists(self):
            return self.dispenserA.pellet or self.dispenserB.pellet

        def updateThreshold(self, newThreshold):
            self.sensorA.Threshold = newThreshold
            self.sensorB.Threshold = newThreshold


class fakeU3():
    
    def __init__(self,root,*args):
        pass

    def configDigital(*args):
        pass

    def configAnalog(*args):
        pass

    def setFIOState(*args):
        pass

    def getAIN(self,*args):
        return .5

