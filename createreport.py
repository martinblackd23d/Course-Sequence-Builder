import agent
import json
import availability as available
import tkinter
import tkinter.filedialog
import pandas
import numpy

def create_report():
	fullpath = '.\\'	# file path to aggregate reports
	filename = '' # file name of excel file
	sheetname = '24-25 Course Details wDates'	# sheet name of excel file
	terms = {}
	print('Select file')
	tkinter.Tk().withdraw()
	filename = tkinter.filedialog.askopenfilename()
	print('Selected: ' + filename)

	sheets = pandas.ExcelFile(filename).sheet_names
	sheetname = sheets[len(sheets) - 1]

	#uncomment the following lines to select a sheet
	#otherwise the last sheet will be used
	#for i in range(len(sheets)):
	#	print(f'{i}: {sheets[i]}')
	#print('Select sheet: ')
	#sheetname = sheets[int(input())]
	print('Selected: ' + sheetname)
	df = pandas.read_excel(filename, sheet_name=sheetname)
	t = df['YRTR'].unique()
	t = t[~pandas.isnull(t)]
	t.sort()
	if t[0] % 10 == 1:
		t = numpy.append(t, t[0])
		t = t[1:]
	terms = {int(t[i]): i for i in range(3)}
	#uncomment the following lines to select terms
	#otherwise the first full academic year appearing in the file will be used

	#print('Available terms:')
	#for i in range(len(t)):
	#	print(f'\t{int(t[i])}')
	#print('Enter terms to include, separated by commas: ')
	#print(f'(press enter for default: {int(t[0])}, {int(t[1])}, {int(t[2])})')
	#ip = input()
	#if ip != '':
	#	terms = {}
	#	temp = ip.split(',')
	#	for i in range(len(temp)):
	#		terms[int(temp[i].strip())] = i
	#if len(terms) % 3 != 0:
	#	print('Invalid terms')
	#	return
	#for key, value in terms.items():
	#	if [3,5,1][value % 3] != key % 10:
	#		print('Invalid terms')
	#		return

	print('Selected terms: ' + str(terms))

    #manually overwrite params
    #terms = {20243: 0, 202455: 1, 20251: 2}
    #filename = 'data.xlsx'
    #sheetname = 'sheet1'

	available.create_availability(terms, filename, sheetname)

	with open('prereqs.json', 'r') as f:
		prereqs = json.load(f)
	with open ('progreqs.json', 'r') as f:
		progreqs = json.load(f)
	with open('availability.json', 'r') as f:
		availability = json.load(f)

	#process known errors
	with open("known_issues.json", "r") as f:
		known_issues = json.load(f)

	impossible = known_issues['skipped programs'] # programs in this list will be excluded from the report

	#add dummy courses for specified courses in known_issues.json, so they don't throw errors
	for c in known_issues['skipped courses']:
		prereqs[c] = []
		for i in range(len(availability)):
			availability[i][c] = {}
			availability[i][c][-2] = ["", "Completely Online-Asychronous", 1, 1, 0, 0, ""]
	

	#semesters = [0,1,3,4]
	#if you only want to look at a certain year, uncomment the following line and change the list
	#availability = [availability[3], availability[4], availability[5]]
	semesters = [0,1] # semesters to start in


	bylengthstart = [{}, {}, {}, {}, {}, {}]
	bylengthstartexsummer = [{}, {}, {}, {}, {}, {}]
	bylengthonline = [{}, {}, {}, {}, {}, {}]
	bylengthstartexsummeronline = [{}, {}, {}, {}, {}, {}]
	day = {}
	night = {}


	for p in progreqs:
		with open(f'{fullpath}programs\\{p.replace("/", "")}.txt', 'w') as f:
			log = []

			# offline, including summer
			for i in semesters:
				skipsummer = False
				start = i
				restrictions = [[], [], 0, 0, 0, 0, '']
				error = []
				s = agent.makesequence(p, prereqs, progreqs, availability, restrictions, log, skipsummer, start, error = error)
				f.write(f'\nStart in {["fall", "spring"][start]}\n')
				length = len(s) - start
				if length <= 0:
					length = len(error) * -1
					f.write(f'Program not completable\n{len(error)} missing courses:\n')
					f.write(str(error))
					f.write('\n')
				else:
					f.write(f'Length: {length}\n')
					for l in s:
						f.write(str(l))
						f.write('\n')

				if length not in bylengthstart[i]:
					bylengthstart[i][length] = []
				bylengthstart[i][length].append(p)

			# offline, excluding summer
			for i in semesters:
				skipsummer = True
				start = i
				restrictions = [[], [], 0, 0, 0, 0, '']
				error = []
				s = agent.makesequence(p, prereqs, progreqs, availability, restrictions, log, skipsummer, start, error = error)
				f.write(f'\nStart in {["fall", "spring"][start]}, excluding summer\n')
				length = len(s) - start
				if length <= 0:
					length = len(error) * -1
					f.write(f'Program not completable\n{len(error)} missing courses:\n')
					f.write(str(error))
					f.write('\n')
				else:
					f.write(f'Length: {length}\n')
					for l in s:
						f.write(str(l))
						f.write('\n')
				f.write('\n')

				if length not in bylengthstartexsummer[i]:
					bylengthstartexsummer[i][length] = []
				bylengthstartexsummer[i][length].append(p)

			#online, including summer
			for i in semesters:
				skipsummer = False
				start = i
				restrictions = [[], ['Mostly Online', 'Completely Online-Asynchronous', 'Completely Online - Synchronous'], 0, 0, 0, 0, '']#'Completely Online - Synchronous'
				error = []
				s = agent.makesequence(p, prereqs, progreqs, availability, restrictions, log, skipsummer, start, error = error)
				f.write(f'\nStart in {["fall", "spring"][start]}, online\n')
				length = len(s) - start
				if length <= 0:
					f.write(f'Program not completable\n{len(error)} missing courses:\n')
					f.write(str(error))
					f.write('\n')
					length = len(error) * -1
				else:
					f.write(f'Length: {length}\n')
					for l in s:
						f.write(str(l))
						f.write('\n')
				f.write('\n')

				if length not in bylengthonline[i]:
					bylengthonline[i][length] = []
				bylengthonline[i][length].append(p)

			# online, excluding summer
			for i in semesters:
				skipsummer = True
				start = i
				restrictions = [[], ['Mostly Online', 'Completely Online-Asynchronous', 'Completely Online - Synchronous'], 0, 0, 0, 0, '']
				error = []
				s = agent.makesequence(p, prereqs, progreqs, availability, restrictions, log, skipsummer, start, error = error)
				f.write(f'\nStart in {["fall", "spring"][start]}, excluding summer, online\n')
				length = len(s) - start
				if length <= 0:
					length = len(error) * -1
					f.write(f'Program not completable\n{len(error)} missing courses:\n')
					f.write(str(error))
					f.write('\n')
				else:
					f.write(f'Length: {length}\n')
					for l in s:
						f.write(str(l))
						f.write('\n')
				f.write('\n')


				if length not in bylengthstartexsummeronline[i]:
					bylengthstartexsummeronline[i][length] = []
				bylengthstartexsummeronline[i][length].append(p)

			# day
			skipsummer = False
			start = 0
			restrictions = [[], [], 0, 0, 0, 1800, '']
			error = []
			s = agent.makesequence(p, prereqs, progreqs, availability, restrictions, log, skipsummer, start, error = error)
			length = len(s) - start
			if length <= 0:
				length = len(error) * -1
			if length not in day:
				day[length] = []
			day[length].append(p)
			f.write(f'\nDay\n')
			f.write(f'Length: {length}\n')
			for l in s:
				f.write(str(l))
				f.write('\n')
			if l == 0:
				f.write('Program not completable\n')
				for e in error:
					f.write(e)
					f.write('\n')

			# night
			skipsummer = False
			start = 0
			restrictions = [[], [], 1800, 0, 0, 0, '']
			error = []
			s = agent.makesequence(p, prereqs, progreqs, availability, restrictions, log, skipsummer, start, error = error)
			length = len(s) - start
			if length <= 0:
				length = len(error) * -1
			if length not in night:
				night[length] = []
			night[length].append(p)
			f.write(f'\nNight\n')
			f.write(f'Length: {length}\n')
			for l in s:
				f.write(str(l))
				f.write('\n')
			if l == 0:
				f.write('Program not completable\n')
				for e in error:
					f.write(e)
					f.write('\n')
	############################################################################
	report = '# Programs that are not completable at all:\n'
	report += 'WARNING: If a program appears here, it will be excluded from the rest of the report. If the course that is flagged as missing does in fact exist, please add it to the known_issues.json file and run the program again to include it\n'
	d = {}
	for p in progreqs:
		error = []
		agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, False, 0, error = error)
		if len(error) > 0:
			d[p] = error
	for key, value in sorted(d.items()):
		if key in impossible:
			continue
		impossible.append(key)
		report += f'\t{key}:\n'
		value.sort()
		for v in value:
			report += f'\t\t{v}\n'
	report += '\n\n'

	report += '# Programs that take too long to complete\n'
	report += 'with fall start:\n'
	d = {}
	s = []
	for p in progreqs:
		if p in impossible:
			continue
		error = []
		agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, True, 0, error = error)
		if len(error) > 0:
			s.append(p)
			l = len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, False, 0, error = error))
		else:
			l = len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, True, 0, error = error))
			if len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, False, 0, error = error)) > 6:
				s.append(p)
		if l > 6:
			if l not in d:
				d[l] = []
			d[l].append(p)
	for key, value in sorted(d.items()):
		report += f'{key} semesters:\n'
		value.sort()
		for v in value:
			report += f'\t{v}'
			if v in s:
				report += ' - too long even with summer courses'
			report += '\n'
	report += '\n'

	report += 'with spring start:\n'
	d = {}
	s = []
	for p in progreqs:
		if p in impossible:
			continue
		error = []
		agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, True, 1, error = error)
		if len(error) > 0:
			s.append(p)
			l = len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, False, 1, error = error)) - 1
		else:
			l = len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, True, 1, error = error)) - 1
			if len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, False, 1, error = error)) - 1 > 6:
				s.append(p)
		if l > 6:
			if l not in d:
				d[l] = []
			d[l].append(p)
	for key, value in sorted(d.items()):
		report += f'{key} semesters:\n'
		value.sort()
		for v in value:
			report += f'\t{v}'
			if v in s:
				report += ' - too long even with summer courses'
			report += '\n'
	report += '\n\n'


	report += '# programs with courses only offered in the summer:\n'
	d = {}
	l = []
	for p in progreqs:
		if p in impossible:
			continue
		error = []
		agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 0, ''], log, True, 0, error = error)
		if len(error) > 0:
			d[p] = error.copy()
	for key, value in sorted(d.items()):
		if key in l:
			continue
		report += f'\t{key}'
		l.append(key)
		for key2, value2 in sorted(d.items()):
			if key == key2 or key2 in l:
				continue
			if sorted(value) == sorted(value2):
				report += f' -- {key2}'
				l.append(key2)
		report += '\n'
		for v in value:
			report += f'\t\t{v}\n'
	report += '\n\n'


	online = []
	onlineerror = [{}, {}, {}]
	for p in progreqs:
		if p in impossible:
			continue
		error = []
		agent.makesequence(p, prereqs, progreqs, availability, [[], ['Mostly Online', 'Completely Online-Asynchronous', 'Completely Online - Synchronous'], 0, 0, 0, 0, ''], log, True, 0, error = error)
		if len(error) == 0:
			online.append(p)
		elif len(error) < 4:
			onlineerror[len(error) - 1][p] = error.copy()

	report += '# programs that are completable online:\n'
	for p in sorted(online):
		report += f'\t{p}'
		error = []
		l = len(agent.makesequence(p, prereqs, progreqs, availability, [[], ['Mostly Online', 'Completely Online-Asynchronous', 'Completely Online - Synchronous'], 0, 0, 0, 0, ''], log, True, 0, error = error))
		if l > 6:
			report += f'\t - {l} semesters with fall start'
		l = len(agent.makesequence(p, prereqs, progreqs, availability, [[], ['Mostly Online', 'Completely Online-Asynchronous', 'Completely Online - Synchronous'], 0, 0, 0, 0, ''], log, True, 1, error = error)) - 1
		if l > 6:
			report += f'\t - {l} semesters with spring start'
		report += '\n'
	report += '\n'

	report += '# programs that are mostly completable online, except for a few courses\n'
	for i in range(3):
		report += f'{i + 1} missing course:\n'
		l = []
		for key, value in sorted(onlineerror[i].items()):
			if key in l:
				continue
			report += f'\t{key}'
			l.append(key)
			for key2, value2 in sorted(onlineerror[i].items()):
				if key == key2 or key2 in l:
					continue
				if sorted(value) == sorted(value2):
					report += f' -- {key2}'
					l.append(key2)
			report += '\n'
			for v in value:
				report += f'\t\t{v}'
				error = []
				agent.makesequence(key, prereqs, progreqs, availability, [[], ['Mostly Online', 'Completely Online-Asynchronous', 'Completely Online - Synchronous'], 0, 0, 0, 0, ''], log, False, 0, error = error)
				if v not in error:
					report += '\t - course available over summer'
				report += '\n'
		report += '\n'

	report += '\n\n'
	report += '# programs that require both day and night courses:\n'
	for p in progreqs:
		errorday = []
		errornight = []
		if p in impossible:
				continue
		if len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 0, 1800, ''], log, False, 0, error = errorday)) <= 0 and len(agent.makesequence(p, prereqs, progreqs, availability, [[], [], 0, 0, 1700, 0, ''], log, False, 0, error = errornight)) <= 0:
			errordaytemp = errorday.copy()
			errornighttemp = errornight.copy()
			for d in errordaytemp:
				if d in errornighttemp:
					errorday.remove(d)
					errornight.remove(d)
			if len(errorday) == 0 and len(errornight) == 0:
				continue
			report += f'\t{p}\n'
			if len(errorday) > 3 and len(errornight) > 3:
				report += '\t\tOnly available at night:\n'
				report += f'\t\t\t{len(errorday)} courses {errorday}\n'
				report += '\t\tOnly available during day:\n'
				report += f'\t\t\t{len(errornight)} courses {errornight}\n'
			if len(errorday) < 4 and len(errorday) > 0:
				report += '\t\tOnly available at night:\n'
				for e in errorday:
					report += f'\t\t\t{e}\n'
			if len(errornight) < 4 and len(errornight) > 0:
				report += '\t\tOnly available during day:\n'
				for e in errornight:
					report += f'\t\t\t{e}\n'
			report += '\n'

	with open('report.txt', 'w') as f:
		f.write(report)
		
	for i in [0,1]:
		with open(f'{fullpath}aggregate\\start_in_{["fall", "spring"][start]}.json', 'w') as f:
			json.dump(bylengthstart[i], f, indent=4, sort_keys=True)
		with open(f'{fullpath}aggregate\\start_in_{["fall", "spring"][start]}_no_summer.json', 'w') as f:
			json.dump(bylengthstartexsummer[i], f, indent=4, sort_keys=True)
		with open(f'{fullpath}aggregate\\start_in_{["fall", "spring"][start]}_online.json', 'w') as f:
			json.dump(bylengthonline[i], f, indent=4, sort_keys=True)
		with open(f'{fullpath}aggregate\\start_in_{["fall", "spring"][start]}_no_summer_online.json', 'w') as f:
			json.dump(bylengthstartexsummeronline[i], f, indent=4, sort_keys=True)

if __name__ == '__main__':
	create_report()
