# these are standart python libraries requried for the code to run
import pandas
import numpy
import json

# these are custom libraries
import agent
import availability as available # import with alias to avoid naming conflicts

terms = {20243: 0, 20245: 1, 20251: 2}
filename = 'C:\\Users\\Martin\\Downloads\\Data Prep - Course Schedule 20223-20255 -- DD 12.18.23.xlsx'
sheet = '24-25 Course Details wDates'

# read excel file and store it with required format
available.create_availability(terms, filename, sheet)

# read static data files about programs, course prerequisites, and program requirements
with open('prereqs.json', 'r') as f:
	prereqs = json.load(f) # store prereqs.json as a dictionary
with open ('progreqs.json', 'r') as f:
	progreqs = json.load(f)	# store progreqs.json as a dictionary
with open('availability.json', 'r') as f:
	availability = json.load(f)	# store availability.json as a dictionary

program = 'Computer Science Transfer Pathway' # which program to make a sequence for
restrictions = [[], [], 0, 0, 0, 0, ''] # allows everything
# restrictions = [['1st Half of Term', 'Normal full term for any term'], ['Mostly Online', 'Completely Online-Asynchronous', 'Completely Online - Synchronous'], 20210101, 20231212, 1600, 2000, 'MWF']
# this example only allows courses that are:
# 1. in the first half of the term or full term
# 2. an online course
# 3. between 2021 jan 01 and 2023 dec 12
# 4. between 4:00pm and 8:00pm
# 5. only have classes on Monday, Wednesday, or Friday
# the inputs are in the same format as the input excel sheet, with the same possible values

log = [] # UNUSED: after the code runs, log will contain a list of all the errors that occured

error = [] # if a program is not completable with given restrictions,
# error will contain a list of all the courses that are missing
skipsummer = True # if True, the code will skip summer terms
start = 0 # which term to start with (0 fall, 1 spring, 2 summer)

# call main function
sequence = agent.makesequence(program, prereqs, progreqs, availability, restrictions, log, skipsummer, start, error = error)
# sequence = [] if the program is not completable with given restrictions
# error will contain courses that are not completable

# print the sequence
for term in sequence:
	print(term)

# print the error (if any)
print('unavailable courses:')
print(error)