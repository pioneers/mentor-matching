import csv


class School:
	def __init__(self, row):
		self.name = row[0]
		self.avail_times = [[0 for time in range(9)] for day in range(7)]
		for day in range(7):
			for time in range(9):
				if row[(day * 9) + time + 1] != "":
					self.avail_times[day][time] = 1
		self.num_mentors = int(row[64])
		self.is_new = int(row[65])

class Mentor:
	def __init__(self, row):
		self.name = row[0]
		self.avail_times = [[0 for time in range(9)] for day in range(7)]
		for day in range(7):
			for time in range(9):
				if row[(day * 9) + time + 1] != "":
					self.avail_times[day][time] = 1
		self.mentor_alone = int(row[64]) # 5 is fine with mentoring alone, 1 is not so fine
		self.new_school = int(row[65])

def calc_weight(school, mentor):
	if mentor.name == "Grant Ermendorfer" and school.name == "REALM":
		return 10000
	if mentor.name == "Ravi Mandla" and school.name == "Hercules High School":
		return 10000
	if mentor.name == "Austin Wright" and school.name == "Coliseum":
		return 10000
	weight = 0
	for day in range(7):
		for time in range(9):
			if school.avail_times[day][time] == 1 and mentor.avail_times[day][time] == 1:
				weight += 10
	if weight == 0:
		return -10000000 # can't make the same time, so don't match
	if mentor.mentor_alone <= 2:
		if school.num_mentors > 1:
			weight += 50
		else:
			weight -= 50
	if mentor.new_school == school.is_new:
		weight += 20
	return weight

schools = []
mentors = []

with open("schools.csv", "r") as schoolFile:
	header = next(schoolFile) # ignore header
	for row in schoolFile:
		schools.append(School(row.split(",")))

with open("mentors.csv", "r") as mentorFile:
	header = next(mentorFile) # ignore header
	for row in mentorFile:
		mentors.append(Mentor(row.split(",")))

with open("pair_vals.csv", "w") as outputFile:
	first_row = "Name"
	for school in schools:
		for i in range(1, school.num_mentors + 1):
			first_row += "," + school.name + str(i)
	outputFile.write(first_row + "\n")
	for mentor in mentors:
		mentorRow = mentor.name
		for school in schools:
			for i in range(1, school.num_mentors + 1):
				mentorRow += "," + str(calc_weight(school, mentor))
		outputFile.write(mentorRow + "\n")