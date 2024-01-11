import json
import pandas

def create_availability(terms, file, sheet):
	df = pandas.read_excel(file, sheet_name=sheet)
	output = []
	for i in terms:
		output.append({})
	#terms = {20223: 0, 20225: 1, 20231: 2, 20233: 3, 20235: 4, 20241: 5}
	log = []
	mediacheck = {0: 'In person', 3: 'Mostly Online', 9: 'Blended/Hybrid', 11: 'Arranged', 12: 'Completely Online-Asynchronous', 13: 'Completely Online - Synchronous', 14: 'HyFlex'}
	#0: 'In person'
	skipped = 0
	t = 0
	duplicates = 0
	partition = 0

	#[session, media, begindate, enddate, begintime, endtime, days
	def merge(a, b):
		log.append(f'P2 Merging at index {index:5}: {a} {b}')
		a = a.copy()
		b = b.copy()
		if a[0] != b[0]:
			a[0] = 'Mixed'
		#	print(f'P1 Error at index {index:5}: session {a[0]} {b[0]}')
		#	raise Exception('Session mismatch')
		if a[1] != b[1]:
			log.append(f'P2 Merge error at index {index:5}: media {a[1]} {b[1]}')
			a[1] = 'Mixed'
			b[1] = 'Mixed'
			#if a[1] == 'In person':
			#	a[1] = b[1]
			#elif b[1] == 'In person':
			#	b[1] = a[1]
			#elif a[1] == 'Blended/Hybrid':
			#	b[1] = a[1]
			#elif b[1] == 'Blended/Hybrid':
			#	a[1] = b[1]
			if a[1] != b[1]:
				print(f'P1 Error at index {index:5}: media {a[1]} {b[1]}')
				raise Exception('Media mismatch')
		'''
		if a[7] != b[7]:
			log.append(f'P2 Merge error at index {index:5}: enr {a[7]} {b[7]}')
			if a[7] < b[7]:
				a[7] = b[7]
			#print(f'P1 Error at index {index:5}: enr {a[7]} {b[7]}')
			#raise Exception('Enrollment mismatch')
		if a[8] != b[8]:
			log.append(f'P2 Merge error at index {index:5}: max {a[8]} {b[8]}')
			if a[8] == 0:
				a[8] = b[8]
			if b[8] == 0:
				b[8] = a[8]
			if a[8] > b[8]:
				a[8] = b[8]
			if a[8] != b[8]:
				print(f'P1 Error at index {index:5}: max {a[8]} {b[8]}')
				raise Exception('Max mismatch')
		'''
		if a[2] == 0:
			a[2] = b[2]
		if b[2] == 0:
			b[2] = a[2]
		if a[2] > b[2]:
			a[2] = b[2]
		
		if a[3] == 0:
			a[3] = b[3]
		if b[3] == 0:
			b[3] = a[3]
		if a[3] < b[3]:
			a[3] = b[3]

		if a[4] == 0:
			a[4] = b[4]
		if b[4] == 0:
			b[4] = a[4]
		if a[4] > b[4]:
			a[4] = b[4]
		
		if a[5] == 0:
			a[5] = b[5]
		if b[5] == 0:
			b[5] = a[5]
		if a[5] < b[5]:
			a[5] = b[5]

		if a[6] == '':
			a[6] = b[6]
		if b[6] == '':
			b[6] = a[6]
		if a[6] != b[6]:
			log.append(f'P2 Merge error at index {index:5}: days {a[6]} {b[6]}')
			r = ''
			for i in ['M', 'T', 'W', 'H', 'F', 'S', 'U']:
				if i in a[6] or i in b[6]:
					r += i
			a[6] = r
		
		return a


	#skipped issues:
	#if session nan, then rest of the row is nan
	#media code nan, media desc nan, day nan
	#begin or end date nan
	for index, row in df.iterrows():
		t += 1
		if row['SUBJ'] == 'nan' or row['COU_NBR'] == 'nan':
			print(f'P1 Error at index {index:5}: SUBJ {row["SUBJ"]} COU_NBR {row["COU_NBR"]}')
			raise Exception('Course not found')
		course = row['SUBJ'] + ' ' + str(row['COU_NBR'])

		session = str(row['Session_type'])
		if session == 'nan':
			log.append(f'P1 Error at index {index:5}: Session_type {session}')
			skipped += 1
			continue

		term = row['YRTR']
		if term == 'nan':
			print(f'P1 Error at index {index:5}: YRTR {term}')
			raise Exception('Term not found')
		if term not in terms:
			continue


		section = str(row['SECT_NBR'])
		if section == 'nan':
			print(f'P1 Error at index {index:5}: SECT_NBR {section}')
			raise Exception('Section not found')
		
		mediacode = row['MEDIA_CODE']
		if str(mediacode) == 'nan':
			mediacode = 0
		media = mediacheck[mediacode]
		#if str(mediacode) == 'nan':
		#	print(f'P1 Error at index {index:5}: MEDIA_CODE {mediacode}')
		#	raise Exception('Media code not found')
		'''
		media = str(row['Media_Desc'])
		#if media == 'nan':
		#	log.append(f'P2 Error at index {index:5}: Media_Desc {media}')

		if str(mediacode) == 'nan' and media == 'nan':
			if str(row['DAYS']) == 'nan':
				log.append(f'P2 Error at index {index:5}: Media_Desc {media} DAYS {row["DAYS"]}')
			mediacode = 0
			media = 'In person'
		
		else:
			if mediacheck[mediacode] != media:
				print(f'P1 Error at index {index:5}: MEDIA_CODE {mediacode} Media_Desc {media}')
				raise Exception('Media code and description do not match')
		'''
		begindate = row['BEGIN_DATE']
		enddate = row['END_DATE']
		if str(begindate) == 'nan' or str(enddate) == 'nan':
			continue



		begintime = row['BEGIN_TIME']
		endtime = row['END_TIME']
		if str(begintime) == 'nan' and str(endtime) == 'nan':
			begintime = 0
			endtime = 0
			if mediacode != 12:
				log.append(f'P2 Error at index {index:5}: MEDIA_CODE {mediacode} Media_Desc {media} BEGIN_TIME {begintime} END_TIME {endtime}')
		elif str(begintime) == 'nan' or str(endtime) == 'nan':
			print(f'P1 Error at index {index:5}: BEGIN_TIME {begintime} END_TIME {endtime}')
			raise Exception('Time mismatch')
		
		days = str(row['DAYS'])
		#if str(days) == 'nan' and mediacode != 12:
		#	log.append(f'P2 Error at index {index:5}: MEDIA_CODE {mediacode} Media_Desc {media} DAYS {days}')
		if str(days) == 'nan':
			days = ''
		days = ''.join(days.split())

		# course, session, term, section, mediacode, media, begindate, enddate, begintime, endtime, days
		if course not in output[terms[term]]:
			output[terms[term]][course] = {}

		if section in output[terms[term]][course]:
			try:
				duplicates += 1
				output[terms[term]][course][section] = merge(output[terms[term]][course][section], [session, media, begindate, enddate, begintime, endtime, days])
			except Exception as e:
				print(output[terms[term]][course][section])
				print([session, media, begindate, enddate, begintime, endtime, days])
				print(course, section)
				print(term)
				print(f'P1 Error at index {index:5}: {e}')
				raise Exception('Merge error')
		else:
			output[terms[term]][course][section] = [session, media, begindate, enddate, begintime, endtime, days]
		if str(term) == 'nan' or str(course) == 'nan' or str(section) == 'nan' or str(session) == 'nan' or str(media) == 'nan' or str(begindate) == 'nan' or str(enddate) == 'nan' or str(begintime) == 'nan' or str(endtime) == 'nan' or str(days) == 'nan':
			print(f'P1 Error at index {index:5}: term {term} course {course} section {section} session {session} media {media} begindate {begindate} enddate {enddate} begintime {begintime} endtime {endtime} days {days} enr {enr} max {max}')
			raise Exception('Unknown error')

		#format:
		#[
		#	{
		#		'AAAA 0000': {
		#			'01': ['First half', 'in person', 'yyyymmdd', 'yyyymmdd', 'hhmm', 'hhmm', 'MWF', '5', '10'],
		#		}
		#	}
		#]
	#print(t)
	#print(duplicates)
	#print(partition)
	#print(skipped)
	'''
	for i in range(len(output)):
		print(len(output[i]))
		c = 0
		for j in output[i]:
			c += len(output[i][j])
		print(c)'''
	with open('availability.json', 'w') as f:
		json.dump(output, f, indent=4)	


	#with open('availability.log', 'w') as f:
	#	f.write('\n'.join(log))


if __name__ == '__main__':
	create_availability()