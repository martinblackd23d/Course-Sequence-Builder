import json
import re

def isfree(course, doublecheck, log):
	for line in doublecheck:
		if line[9:18] == course:
			if len (re.findall(r'[A-Z]{4} [1-9]\d{3}', line)) == 1:
				return True
			break
	raise Exception(f'P1 Error {course} not found in doublecheck')
	return True


def makesequence(program, prereqs, progreqs, availability, restrictions, log, skipsummer = False, start = 0, error = []):
	'''
	makes course sequence for a single program
	program = "Computer Science Transfer Pathway"
	prereqs = {	CSCI 1100: [], 
				CSCI 1200: ['and', [CSCI 1100, 'pre'], [MATH 1400, 'pre']],
				...}
	progreqs = {"Computer Science Transfer Pathway": [CSCI 1100, CSCI 1200, ...],
	availability = [
			1. semester		{CSCI 1100: {01: ['First half', 'in person', 'yyyymmdd', 'yyyymmdd', '1800', '1900', 'MWF', '5', '10'], ...}, ...},

					]
	'''
	log.append(f'P1 Start {program} makesequence')
	# makes course sequence for a single program
	# format: [[[course1, section], [course2, section]], [semester2], [] ...]
	sequence = []

	# get list of prereqs for each course
	# including prereqs of prereqs
	# prereqs format:
	# {course1: [and/or, [prereq1, pre/co], [prereq2, pre/co] ...], ...}
	coursesleft = progreqs[program].copy()
	flag = True
	c = 0
	while flag:
		c += 1
		if c > 100:
			raise Exception('Infinite loop while flag')
		flag = False
		for course in coursesleft:

			'''
			if course not in prereqs:
				# if course is not in prereqs, doublecheck if it's free from the raw scraped data
				# if yes, add it
				#log.append(f'P1 Error {course} not found in prereqs makesequence')
				with open('scrape3.txt', 'r') as f:
					doublecheck = f.readlines()
				if isfree(course, doublecheck, log):
					prereqs[course] = []
					print(f'{course} is free')
					#log.append(f'P1 Error {course} is free makesequence')
					continue
			'''

			for prereq in prereqs[course][1:]:
				# if a prerequisite for a course is not already in coursesleft,
				# add it
				if prereq[0] not in coursesleft:
					coursesleft.append(prereq[0])
					flag = True

	a = isimpossible(coursesleft, restrictions, availability, skipsummer, log)
	if not a == []:
		for i in a:
			if i not in error:
				error.append(i)
		return []

	# while there are still courses left to add,
	# add all possible courses to the next semester
	for i in range(start):
		sequence.append([])
	c = 0
	while len(coursesleft) > 0:
		c += 1
		if c > 100:
			print(coursesleft)
			print(sequence)
			raise Exception('Infinite loop while len(coursesleft) > 0')
		sequence.append([])
		if skipsummer and len(sequence) % 3 == 0:
			continue
		#try:
		fillsemester(sequence, coursesleft, prereqs, availability, restrictions, log)
		#except:
		#	return []
	return sequence



def fillsemester(sequence, coursesleft, prereqs, availability, restrictions, log):
	#course format: [course, end]
	#restrictions format: []
	sem = (len(sequence) - 1) % len(availability)
	flag = True
	templog = []
	# loop until there are no changes to the semester
	c = 0
	while flag:
		c += 1
		if c > 100:
			raise Exception('Infinite loop while flag')
		flag = False
		for course in coursesleft:
			# check if prereqs are met for a course
			# if yes, return the earliest date a course can be taken
			start = areprereqsmet(course, sequence, availability, prereqs, log)
			# if no, continue
			if not start:
				continue
			# find all possible sections for a course
			available = findavailable(course, sequence, availability, restrictions, log, start)
			if available == []:
				continue
			# out of the available courses, choose the earliest one
			earliest = available[0]
			if earliest[1] == -1:
				sequence[-1].append(earliest)
				coursesleft.remove(course)
				flag = True
				raise Exception("nonexistent course") # take this out to allow nonexistent courses
				break
			for i in available:
				if availability[sem][i[0]][i[1]][3] != 0:
					earliest = i
			if availability[sem][earliest[0]][earliest[1]][3] == 0:
				templog.append(f'P1 Error course dates not found for {course} in any section for semester {sem} fillsemester')
				continue
			for i in available:
				if availability[sem][i[0]][i[1]][3] == 0:
					templog.append(f'P1 Error course dates not found for {course} section {i[1]} in semester {sem} fillsemester')
					continue
				if availability[sem][i[0]][i[1]][3] < availability[sem][earliest[0]][earliest[1]][3]:
					earliest = i

			sequence[-1].append(earliest)
			coursesleft.remove(course)
			flag = True
			break
	# log everything, after removing duplicates
	templog = set(templog)
	for i in templog:
		log.append(i)

def findavailable(course, sequence, availability, restrictions, log, start):
	sem = (len(sequence) - 1) % len(availability)
	available = []
	if course not in availability[sem]:
		return []
	
	for i in availability[sem][course]:
		if availability[sem][course][i][3] == 0:
			raise Exception(f'P1 Error course dates not found for {course} for section {i} in semester {sem} findavailable')
		if availability[sem][course][i][2] < start:
			continue
		if not checkrestrictions(sem, course, i, availability, restrictions):
			continue
		available.append([course, i])
	#if available == []:
	#	print(course, sem, start, availability[sem][course])
	return available

def areprereqsmet(course, sequence, availability, prereqs, log):
	aremet = False
	bydate = -1
	p = prereqs[course]
	if len(p) == 0:
		return 1
	if p[0] == 'or':
		# TODO: deal with coreqs in 'or'
		for i in p[1:]:
			date = insequence(i[0], sequence, availability)
			if date:
				aremet = True
				if bydate == -1:
					bydate = date
				elif date < bydate:
					bydate = date
	elif p[0] == 'and':
		aremet = True
		for i in p[1:]:
			if i[1] == 'co' or i[1] == 'either':
				continue
			date = insequence(i[0], sequence, availability)
			if not date:
				aremet = False
				break
			if bydate == 1 or date > bydate:
				bydate = date
	if aremet:
		return bydate
	return False

#returns end date of course if it's in sequence
def insequence(course, sequence, availability):
	for i in range(len(sequence)):
		for j in sequence[i]:
			if j[0] == course:
				if i != (len(sequence) - 1):
					return 1
				return availability[i % len(availability)][j[0]][j[1]][3]
	return False


def isimpossible(coursesleft, restrictions, availability, skipsummer, log):
	l = []
	for i in range(len(availability)):
		if skipsummer and i % 3 == 2:
			continue
		l.append(i)

	found = False
	final = []
	for course in coursesleft:
		for sem in l:
			if course not in availability[sem]:
				continue
			for section in availability[sem][course]:
				if checkrestrictions(sem, course, section, availability, restrictions):
					found = True
					break
			if found:
				break
		if not found:
			final.append(course)
			continue
		found = False
	return final


def checkrestrictions(sem, course, section, availability, restrictions):
	c = availability[sem][course][section]
	if restrictions[0] != [] and c[0] not in restrictions[0]:
		return False
	if restrictions[1] != [] and c[1] not in restrictions[1]:
		return False
	if restrictions[2] != 0 and c[2] < restrictions[2] and c[2] != 0:
		return False
	if restrictions[3] != 0 and c[3] > restrictions[3] and c[3] != 0:
		return False
	if restrictions[4] != 0 and c[4] < restrictions[4] and c[4] != 0:
		return False
	if restrictions[5] != 0 and c[5] > restrictions[5] and c[5] != 0:
		return False
	if restrictions[6] != '':
		for i in c[6]:
			if i not in restrictions[6]:
				return False
	return True


def checkcoreqs(sequence, prereqs, log):
	error = []
	for sem in range(len(sequence)):
		for course in sequence[sem]:
			co = []
			either = []
			for i in prereqs[course[0]]:
				if i[1] == 'co':
					co.append(i[0])
				if i[1] == 'either':
					either.append(i[0])

			for i in co:
				found = False
				for j in sequence[sem]:
					if i == j[0]:
						found = True
						break
				if not found:
					error.append(course[0])
					break

			for i in either:
				found = False
				for s in sequence[:sem+1]:
					for j in s:
						if i == j[0]:
							found = True
							break
					if found:
						break
				if not found:
					error.append(course[0])
					break
	return error




def main():
	pass

if __name__ == '__main__':
	main()