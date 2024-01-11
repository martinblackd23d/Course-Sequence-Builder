known_issues.json
	-**skipped programs** contains programs that are not offered and should be removed from the dataset temporarily
	-**skipped courses** contains courses that are missing from the dataset and should be added temporarily, either because they are not offered intentionally or they are not required at the moment

permanent changes should be made to the following 2 files or the excel file:

prereqs.json
	- contains prerequisites for each course
	- first element in each list is whether all prereqs must be met (and) or if any one prereq is enough (or)
	- the other elements are the courses that must be completed with the format [coursename, pre/co], depending on if its a corequisite or prerequisite

progreqs.json
	- contains courses required for each program's completion