try:
    import u3
except:
    pass
from Tkinter import *
from threading import Thread
from time import sleep
import time

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

    def __init__(self, root, events, U3Device, FIOPort, name):
        FIODevice.__init__(self, root, events, U3Device, FIOPort)
        self.pellet = False
        self.name = name
        self.d.configDigital(self.port)
        self.d.setFIOState(self.port)

    def dispense(self):
        self.pellet = True
        self.Status = True
        self.d.configAnalog(self.port)
        self.events.put("<<dispenser"+self.name+"Dispensed>>")
        self.root.after(500, lambda: self.d.configDigital(self.port))
        self.root.after(500, lambda: self.setStatus(False))

    def removePellet(self):
        self.pellet = False

class Sensor(FIODevice):

    def __init__(self, root, events, U3Device, FIOPort, threshold, timeout, name):
        FIODevice.__init__(self, root, events, U3Device, FIOPort)
        self.Threshold = threshold
        self.Timeout = timeout
        self.name = name
        self.d.configAnalog(self.port)
        self.thread = Thread(target = self.startListener)
        self.thread.setDaemon(True)
        self.thread.start()

    def updateThreshold(self, value):
        self.Threshold = value
    
    def startListener(self):
        while True:
            if self.d.getAIN(self.port) < self.Threshold:
                    self.events.put("<<sensor"+self.name+"Tripped>>")
                    self.Status = True
                    sleep(self.Timeout)
                    while self.d.getAIN(self.port) < self.Threshold:
                        pass
            self.Status = False

class NeuralynxWire(FIODevice):
    def __init__(self,root,events,U3Device,FIOPort,name):
        FIODevice.__init__(self,root,events,U3Device,FIOPort)
        self.name = name
        self.d.configDigital(self.port)
        self.d.setFIOState(self.port)
        self.d.configAnalog(self.port)

    def signal(self):
        self.d.configDigital(self.port)
        self.root.after(250, lambda: self.d.configAnalog(self.port))

class Rat():

    def __init__(self, pos = 2):
        self.pos = pos
        self.comingFrom = None
        self.pelletsEaten = 0
        self.startTime = None
        self.endTime = None

    def reset(self):
        self.__init__()

    def setPos(self, pos):
        self.pos = pos

    def getPos(self):
        return self.pos

    def setComingFrom(self, side):
        if side not in ["a", "b", None]:
            raise Exception("Not a valid side.")
        self.comingFrom = side

    def getComingFrom(self):
        return self.comingFrom

    def startTimer(self):
        self.startTime = time.time()

    def stopTimer(self):
        self.endTime = time.time()

    def getTime(self):
        if self.startTime == None:
            return "None"
        elif self.endTime == None:
            return round(time.time() - self.startTime,1)
        else:
            return round(self.endTime - self.startTime,1)

    def atePellet(self):
        self.pelletsEaten += 1


class Maze():

        def __init__(self, events, root, simulated):
            #Maze Variables
            dispenserAPort = 1
            dispenserBPort = 0
            sensorAPort = 5
            sensorBPort = 4
            threshold = .19
            timeout = 1
            NeuralynxWireAPort = 2
            NeuralynxWireBPort = 3

            if simulated: 
                self.d = fakeU3(root)
            else:
                self.d = u3.U3()
            self.root = root
            self.rat = Rat()
            self.dispenserA = Dispenser(root, events, self.d, dispenserAPort, "A")
            self.dispenserB = Dispenser(root, events, self.d, dispenserBPort, "B")
            self.outA = NeuralynxWire(root, events, self.d, NeuralynxWireAPort, "A")
            self.outB = NeuralynxWire(root, events, self.d, NeuralynxWireBPort, "B")
            self.sensorA = Sensor(root, events, self.d, sensorAPort, threshold, timeout, "A")
            self.sensorB = Sensor(root, events, self.d, sensorBPort, threshold, timeout, "B")

        def pelletExists(self):
            return self.dispenserA.pellet or self.dispenserB.pellet

        def updateThreshold(self, newThreshold):
            self.sensorA.Threshold = newThreshold
            self.sensorB.Threshold = newThreshold

#This class is only used when on a testing machine that is not connected to the U3 device.
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