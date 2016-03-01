import u3
from threading import Thread
from time import sleep

class FIODevice():

    def __init__(self, root, U3Device, FIOPort):
        self.root = root
        self.d = U3Device
        self.port = FIOPort
        self.Status = False

    def setStatus(self, status):
                if status:
                        self.Status = True
                else:
                        self.Status = False


class Dispenser(FIODevice):

    def __init__(self, root, U3Device, FIOPort):
        FIODevice.__init__(self, root, U3Device, FIOPort)
        self.pellet = False
        self.d.configDigital(self.port)
        self.d.setFIOState(self.port)

    def dispense(self):
        self.pellet = True
        self.Status = True
        self.d.configAnalog(self.port)
        self.root.event_generate("<<dispensed>>")
        self.root.after(500, lambda: self.d.configDigital(self.port))
        self.root.after(500, lambda: self.setStatus(False))

    def removePellet(self):
        self.pellet = False

class Sensor(FIODevice):

    def __init__(self, root, U3Device, FIOPort, Threshold, Timeout, Name):
        FIODevice.__init__(self, root, U3Device, FIOPort)
        self.Threshold = Threshold
        self.Timeout = Timeout
        self.name = Name
        self.d.configAnalog(self.port)
        thread = Thread(target = self.startListener)
        thread.setDaemon(True)
        thread.start()
    
    def startListener(self):
                while True:
                        if self.d.getAIN(self.port) < self.Threshold:
                                print(self.name, self.d.getAIN(self.port))
                                self.root.event_generate("<<sensor"+self.name+"Tripped>>")
                                self.Status = True
                                sleep(self.Timeout)
                                while self.d.getAIN(self.port) < self.Threshold:
                                        pass
                        self.Status = False

class Rat():

    def __init__(self, pos = 2):
        self.pos = pos

    def setPos(self, pos):
        self.pos = pos

    def getPos(self):
                return self.pos


class Maze():

        def __init__(self, root, dispenserAPort, dispenserBPort, sensorAPort, sensorBPort, Threshold, Timeout):
                self.d = u3.U3()
                self.rat = Rat()
                self.dispenserA = Dispenser(root, self.d, dispenserAPort)
                self.dispenserB = Dispenser(root, self.d, dispenserBPort)
                self.sensorA = Sensor(root, self.d, sensorAPort, Threshold, Timeout, "A")
                self.sensorB = Sensor(root, self.d, sensorBPort, Threshold, Timeout, "B")

        def pelletExists(self):
                return self.dispenserA.pellet or self.dispenserB.pellet
