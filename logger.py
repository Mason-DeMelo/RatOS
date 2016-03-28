import openpyxl

class Logger():
	def __init__(self):
		self.fileLocation = "data/"
		self.log = self.fileLocation + "ratLog.xlsx"
		self.detailedLog = list()

	def addToLog(self, side, time):
		self.detailedLog.append([side, time])

	def updateLog(self, number, date, time, duration, cycles, comment, experimenter):
		#Update Log Book
		if number == "" or experimenter == "":
			raise RuntimeError("The form was incomplete!")
		
		try:
			wb = openpyxl.load_workbook(self.log)
		except:
			wb = openpyxl.Workbook()

		wsTitle = "Rat "+str(number)

		if wsTitle in wb:
			ws = wb[wsTitle]
		else:
			ws = wb.active
			ws.title = wsTitle
			ws['A1'] = "Date"
			ws['B1'] = "Time"
			ws['C1'] = "Duration (sec)"
			ws['D1'] = "Cycles"
			ws['E1'] = "Comments"
			ws['F1'] = "Experimienter"

		row = str(ws.max_row + 1)
		ws['A'+row] = date
		ws['B'+row] = time
		ws['C'+row] = duration
		ws['D'+row] = cycles
		ws['E'+row] = comment
		ws['F'+row] = experimenter

		wb.save(self.log)

		#Update individual Rat Log
		individualLog = self.fileLocation + "Rat " + str(number) +".xlsx"
		try:
			wb = openpyxl.load_workbook(individualLog)
		except:
			wb = openpyxl.Workbook()

		wsTitle = date.replace("/","-")

		if wsTitle in wb:
			ws = wb[wsTitle]
		else:
			ws = wb.active
			ws.title = wsTitle
			ws['A1'] = "Side"
			ws['B1'] = "Time"

		for event in self.detailedLog:
			row = str(ws.max_row + 1)
			ws['A'+row] = event[0]
			ws['B'+row] = event[1]

		wb.save(individualLog)
		self.detaileLog = list()
