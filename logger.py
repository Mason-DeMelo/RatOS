import openpyxl

log = "ratLog.xlsx"

def updateLog(number, date, time, duration, cycles, comment, experimenter):
	if number == "" or experimenter == "":
		raise RuntimeError("The form was incomplete!")
	
	try:
		wb = openpyxl.load_workbook(log)
	except:
		wb = openpyxl.Workbook()

	wsTitle = "Rat "+str(number)

	if wsTitle in wb:
		ws = wb[wsTitle]
	else:
		ws = wb.create_sheet(title=wsTitle)
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

	wb.save(log)
