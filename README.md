# Dependencies:
These need to be installed:
python
pandas


# Usage:
1. run createreport.py
2. Select excel file when prompted
	- it assumes the last sheet contains the data
	- Required attributes:
		SUBJ
		COU_NBR
		Session_type
		YRTR
		SECT_NBR
		MEDIA_CODE
		BEGIN_DATE
		END_DATE
			- DATEs can use non zero dummy values
			- schedule building and completion length will be inaccurate for programs requiring consecutive courses in same semester
		BEGIN_TIME
		END_TIME
		DAYS
	- it uses the first full academic year available, although if only prior summer is available, that is substituted



# Results
What the program checks for:
	- can students complete a certain program with certain limitations, such as delivery method or time of day
		- if no, which courses can they not complete
		- if yes, how long does it take them
	- it considers course prerequisites as well
What it does NOT check for:
	- collisions in time of day offered
		- too many variables to be worth it
		- most of the time it shouldn't be an issue, as most programs require courses from the same department, with the same professors
		- consequently, it's rare, and when it does happen, it's much easier to catch it on a department level
	- corequisites:
		- again, usually not an issue, as corequites are usually scheduled together anyway, and issues should probably be caught there as well


## results.txt
1. Programs that are not completable at all
	- not all courses required for these programs appear in the dataset, and as such, it is not possible to complete them
	- programs appearing here will be excluded from the rest of the report
	- if the program is not intended to be completable, it can be added to the known_issues.json file's programs section, or removed manually from the progreqs.json file
	- if the program should be completable, but a few courses are missing from the data, they can either be:
		- added to the known_issues.json file's courses section
		- manually removed from the progreqs.json file (in this case, only remove the course, not the entire program)
		- added to the dataset (and possibly the prereqs.json file)
	- then rerun the program

2. Programs that take too long to complete with fall or spring start
	- also indicates if a program takes too long even if the students take summer courses to get ahead
	- if not indicated, summer courses can be used to complete the degree on time
	- if a program only takes longer with either fall or spring start, that still could be an issue, as students failing a course will be pushed back 2 semesters, not 1
	- when counting semesters, summer is also included, as well as semesters when students cannot take courses
	- ideally, a program should take up to 6 semesters - 2 years to complete

3. Which programs require courses that are only offered in the summer
	- this is usually intentional, such as with internships, but not always
	- this requires further manual checking

4. which programs can be completed online
	- indicates if it takes too long to complete
	- does not allow summer courses by default

5. programs where only 1,2,3 courses are not offered online
	- if a course is only offered online over the summer, it will appear here

6. Programs that require both day and nigth classes
	- it makes it hard for students to maintain a consistent schedule across semesters
	- if the majority (3<) of the courses are only offered in one schedule, only the outliers are shown
	- if the majority of courses can be taken either day or night, all courses that require a stricter schedule are shown


## folders
aggregate
	- contains all programs, grouped by how many semesters they require
	- negative numbers represent how many courses can not be completed with given restrictions
programs
	- contains detailed reports broken down by program
	- it has the actual course sequences, which can help in identifying an issue
	- format is the same as outlined in codeEXAMPLE.py


# Further readmes:
configREADME.md
how to edit the different config files to resolve errors
codeEXAMPLE.py
brief documentation and example code for the main function, so custom reports can be created

# files:
	- see configREADME.md on how to edit the following files
	- known_issues.json
		- contains known issues with the data
		- can be used to exclude programs or courses from the report
		- can be used to add courses to the dataset
		- can be used to add courses to the prereqs.json file
	- progreqs.json
		- contains courses required for each program
	- prereqs.json
		- contains prerequisites for each course
	- agent.py
		- contains the sequence creation algorithm
	- createreport.py
		- contains the main function that creates the report
	- availability.py
		- converts the excel data into a custom json format