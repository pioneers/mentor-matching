"""
Spreadsheet formatting constants
"""

# Basic formatting
mentorHeaderRows = 1 # how many of the rows in the mentor sheet are headers and so should be ignored
teamHeaderRows = 1 # how many of the rows in the team sheet are headers and so should be ignored
multiItemDelimiter = ";" # what character is used to separate entries in cells that may have multiple values
						 # CANNOT be a comma, since that will create problems with the csv formatting

# Availability information
minutesPerSlot = 30 # number of minutes each slot accounts for
slotsPerDay = [24,24,24,24,24,24,24] # how many slots occur on each day--list in order they appear on the spreadsheet
availableMark = "1" # what will appear in a slot if a mentor / team is available at that time
unavailableMark = "0" # what will appear in a slot if a mentor / team is *not* available at that time

# Team types
numTeamTypes = 4 # how many team types we've defined / let mentors choose from
teamTypeYesMark = "1" # what will appear if a mentor wants a team type / a team is that type
teamTypeNoMark = "0" # what will appear if a mentor doesn't want a team type / the team isn't that type

# Mentoring alone
aloneComfortLevels = ["1", "2", "3", "4", "5"] # comfort levels mentors can put down for mentoring alone 
											   # should be arranged from least to most comfortable
singleMentorLevels = ["Bad", "Neutral", "Good"] # request levels assigned to teams for how good/bad it would be to give them only a single mentor 
												# should be arranged from bad to good

# Transit
numTypesTransit = 5 # number of different types of transit we ask mentors / teams about
transitConvenienceLevels = ["Not possible", "Inconvenient", "Convenient"] # convenience levels mentors can put down for transit types 
																		  # should be arranged from least to most convenient

# Skills
numSkills = 2 # how many skills we ask mentors for confidence in / teams for how much they want
skillConfidenceLevels = ["Not Confident", "Somewhat", "Neutral", "Confident", "Very Confident"] # confidence levels mentors can put down for skills
																								# should be arranged from least to most confident
skillRequestLevels = ["5", "4", "3", "2", "1"] # levels that teams can say they want mentors with a given school
											   # should be arranged from from least to most requested


"""
Weights and other matching-related constants
"""

# Number of mentors per team
minNumMentors = 1 # minimum number of mentors that can be assigned to a team; must be strictly greater than zero or else things will break
maxNumMentors = 2 # maximum number of mentors that can be assigned to a team
# it is recommended that these two numbers have a difference of at most 1, since otherwise the program may be incentivized to assign some teams the maximum number of mentors at the cost of assigning other teams the minimum number (which is probably not what we want)

# Availability overlap
minMeetingTime = 60 # minimum number of minutes a mentor's / team's availabilities need to overlap in order to count
totalMeetingTime = 90 # how many minutes per week we want mentors to be with their teams
teamOverlapValue = 10 # how much each minute of availability overlap between a team and mentor is valued
mentorOverlapValue = 0 # how much each minute of availability overlap between two mentors is valued
noOverlapCost = 10000 # how much cost to incur if a mentor and team don't have any availabilities at the same times (should be very large)
partialOverlapCost = 10000 # how much cost to incur if there is some overlap, but less than totalMeetingTime

# Team types
teamTypeMatchValue = 500 # how much value to give if a team is of a type the mentor wants

# Team requests
teamRequestedValue = 900 # how much value to give if a mentor requested to work with a team
teamRequiredValue = 200000 # how much value to give if a mentor *must* be matched with this team

# Mentoring alone
aloneComfortCosts = [1500, 1000, 500, 10, 1] # how much cost to incur for mentoring alone based on comfort level
											 # note that the order of this must match that of aloneComfortLevels (from above)
singleMentorCosts = [500, 0, -200]  # how much cost to incur if a team only has one mentor
									# note that the order of this must match that of singleMentorValueLevels (from above)
									# negative costs correspond to giving value if a team is only assigned one mentor

# Transit
transitConvenienceWeights = [0, 0.6, 1] # how much the value of an overlap should be weighted based on convenience of transit required
										# setting a weight to 0 will mean that we don't consider travel types of that convenience

#Skills
skillMatchValues = [[0, 0, 0, 0, 0],		# how much value to give depending on how confident a mentor is in a skill and how much a team wants it
					[0, 15, 25, 40, 50],	# each subarray corresponds to a team request level, from least important to most
					[0, 25, 50, 75, 100],	# each entry in a subarray corresponds to a mentor confidence level, from least to most
                    [0, 50, 100, 150, 200],
                    [0, 75, 150, 225, 300]]


"""
class representing a mentor
stores information about a mentor from the spreadsheet and contains various helper functions specific to mentors
attributes:
	name: the mentor's name as a string
	availability: the mentor's availability as a boolean matrix
					each sublist corresponds to one day, and has a boolean value for each slot
	teamTypeRequests: the mentor's requests for team types, as a boolean list
						each entry corresponds to one team type
	teamsRequested: a list of the name(s) of team(s) a mentor has requested to be on (given extra weight)
						the list is empty if no teams are requested
	teamsRequired: a list of the name(s) of team(s) a mentor must be assigned to one of
						the list is empty if no teams are required
	mentorsRequired: a list of the name(s) of other mentor(s) a mentor must be paired with
						the list is empty if no other mentors are required
	comfortAlone: how comfortable the mentor is mentoring alone, as an element from aloneComfortLevels
	transitConveniences: how convenient each transit type is, as a list of elements from transitConvenienceLevels
	skillsConfidence: how confident the mentor is in each skill, as a list of elements from skillConfidenceLevels
"""
class Mentor:
	def __init__(self, dataRow):
		"""
		Initialize a mentor from a spreadsheet row
		dataRow should contain all the data about a mentor, formatted as described in the comments at the top of this file
			all entries should be strings (as is output by a csv reader), otherwise behavior is undefined
		will raise an exception if data is not formatted correctly
		"""
		position = 0 # what position in dataRow we are looking at right now

		# get name
		self.name = dataRow[position]
		position += 1

		# get availabilities
		self.availability = [] # this will be an array of arrays, where each subarray is the availability on a given day
		for numSlots in slotsPerDay:
			dayAvailability = []
			for slot in range(numSlots):
				if dataRow[position] == availableMark:
					dayAvailability.append(1)
				elif dataRow[position] == unavailableMark:
					dayAvailability.append(0)
				else:
					raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s availability in column " + str(position + 1))
				position += 1
			self.availability.append(dayAvailability)

		# get team type requests
		self.teamTypeRequests = []
		for teamType in range(numTeamTypes):
			if dataRow[position] == teamTypeYesMark:
				self.teamTypeRequests.append(1)
			elif dataRow[position] == teamTypeNoMark:
				self.teamTypeRequests.append(0)
			else:
				raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s team type request in column " + str(position + 1))
			position += 1

		# get co-mentor / team requests and requirements
		self.teamsRequested = []
		if dataRow[position] != "": # means the mentor requested at least one team
			# split up multiple team names, strip leading / trailing white space, and put into an array
			self.teamsRequested = [name.strip() for name in dataRow[position].split(multiItemDelimiter)]
		position += 1
		self.teamsRequired = []
		if dataRow[position] != "": # means the mentor is required by at least one team
			# split up multiple team names, strip leading / trailing white space, and put into an array
			self.teamsRequired = [name.strip() for name in dataRow[position].split(multiItemDelimiter)]
		position += 1
		self.mentorsRequired = []
		if dataRow[position] != "": # means the mentor is required to be paired with at least one other mentor
			# split up multiple mentor names, strip leading / trailing white space, and put into an array
			self.mentorsRequired = [name.strip() for name in dataRow[position].split(multiItemDelimiter)]
		position += 1

		# get comfort mentoring alone
		if dataRow[position] not in aloneComfortLevels:
			raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s team comfort mentoring alone in column " + str(position + 1))
		self.comfortAlone = dataRow[position]
		position += 1

		# get transit type conveniences
		self.transitConveniences = []
		for transitType in range(numTypesTransit):
			if dataRow[position] not in transitConvenienceLevels:
				raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s team transit convenience in column " + str(position + 1))
			self.transitConveniences.append(dataRow[position])
			position += 1

		# get confidence in skills
		self.skillsConfidence = []
		for skill in range(numSkills):
			if dataRow[position] not in skillConfidenceLevels:
				raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s team skill confidence in column " + str(position + 1))
			self.skillsConfidence.append(dataRow[position])
			position += 1

	def isMatch(self, otherName):
		"""
		Returns whether or not this mentor matches the input name
		Comparison ignores spaces and capitalization, but otherwise the names must match exactly
		"""
		ownName = self.name.replace(" ", "").lower()
		otherName = otherName.replace(" ", "").lower()
		return ownName == otherName

	def mustPair(self, otherMentor):
		"""
		Returns whether or otherMentor appears in this mentor's list of mentors they are required to be matched with
		"""
		for name in self.mentorsRequired:
			if otherMentor.isMatch(name):
				return True
		return False

"""
class representing a team
stores information about a team from the spreadsheet and contains various helper functions specific to teams
attributes:
	name: the team's name as a string
	availability: the team's availability as a boolean matrix
					each sublist corresponds to one day, and has a boolean value for each slot
	teamTypes: whether the team falls into each team type, as a boolean list
						each entry corresponds to one team type
	singleMentorLevel: how much this team wants / doesn't want to have a single mentor, as an element from singleMentorLevels
	transitTimes: how long each transit type would take in minutes, as a list integers
	skillRequests: how much the team wants each skill, as a list of elements from skillRequestLevels
"""
class Team:
	def __init__(self, dataRow):
		"""
		Initialize a team from a spreadsheet row
		dataRow should contain all the data about a team, formatted as described in the comments at the top of this file
			all entries should be strings (as is output by a csv reader), otherwise behavior is undefined
		will raise an exception if data is not formatted correctly
		"""
		position = 0 # what position in dataRow we are looking at right now

		# get name
		self.name = dataRow[position]
		position += 1

		# get availabilities
		self.availability = [] # this will be an array of arrays, where each subarray is the availability on a given day
		for numSlots in slotsPerDay:
			dayAvailability = []
			for slot in range(numSlots):
				if dataRow[position] == availableMark:
					dayAvailability.append(1)
				elif dataRow[position] == unavailableMark:
					dayAvailability.append(0)
				else:
					raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s availability in column " + str(position + 1))
				position += 1
			self.availability.append(dayAvailability)

		# get team types
		self.teamTypes = []
		for teamType in range(numTeamTypes):
			if dataRow[position] == teamTypeYesMark:
				self.teamTypes.append(1)
			elif dataRow[position] == teamTypeNoMark:
				self.teamTypes.append(0)
			else:
				raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s team type in column " + str(position + 1))
			position += 1

		# get single mentor level
		if dataRow[position] not in singleMentorLevels:
			raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s single mentor level in column " + str(position + 1))
		self.singleMentorLevel = dataRow[position]
		position += 1

		# get transit times
		self.transitTimes = []
		for transitType in range(numTypesTransit):
			try:
				self.transitTimes.append(int(dataRow[position])) # if dataRow[position] isn't an integer, this will raise a ValueError
				position += 1
			except ValueError:
				raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s travel time in column " + str(position + 1))

		# get requests for skills
		self.skillRequests = []
		for skill in range(numSkills):
			if dataRow[position] not in skillRequestLevels:
				raise ValueError("Got invalid value " + dataRow[position] + " for " + self.name + "'s team skill request in column " + str(position + 1))
			self.skillRequests.append(dataRow[position])
			position += 1

	def isMatch(self, otherName):
		"""
		Returns whether or not this team matches the input name
		Comparison ignores spaces and capitalization, but otherwise the names must match exactly
		"""
		ownName = self.name.replace(" ", "").lower()
		otherName = otherName.replace(" ", "").lower()
		return ownName == otherName


"""
Functions for finding the value of a mentor-team pair, independent of any co-mentors
"""

def getTeamOverlapValue(mentor, team, transitType):
	"""
	Measures how well the availability of a mentor's and team's availabilities overlap
	Assumes the mentor uses input transit type, which is an integer in range(numTransitTypes)
	Finds the total amount of overlap (minus travel time for the mentor), but an overlap must be for at least minMeetingTime to count
	Value is then total overlap time multiplied by teamOverlapValue and the transit convenience weight for that mentor and transit type
	If the transit type weight is zero for the mentor, returns -noOverlapCost
	If total overlap is zero, returns -noOverlapCost
	If total overlap is non-zero but less than totalMeetingTime, charges partialOverlapCost to the value (after weighting)

	Random note: there's an adversarial input to this where a small gap in the team's availability between two overlaps, combined
					with a long travel time could cause the value to be overreported by giving a slot in the second overlap both
					to that overlap and to travel time after the first overlap.  But I don't think this will actually come up
					in practice, so I don't think it's worth futzing with the code to try to fix that.
	"""
	totalOverlap = 0
	for day in range(7):
		# at the beginning of a day, reset all counters for contiguous blocks
		mentorAvailabilityBeforeOverlap = 0 # mentor may be able to travel before overlap happens
		currOverlap = 0
		for slotNum in range(slotsPerDay[day]):
			if mentor.availability[day][slotNum] and team.availability[day][slotNum]:
				# this slot is part of an overlap, so start the overlap counter
				currOverlap += minutesPerSlot
			elif currOverlap > 0:
				# previously was in an overlap, but that just ended
				# need to figure out how much time the mentor is free after the overlap in case they can travel during that time
				mentorAvailabilityAfterOverlap = 0
				for afterSlot in range(slotNum, slotsPerDay[day]):
					if mentor.availability[day][slotNum]:
						mentorAvailabilityAfterOverlap += minutesPerSlot
					else:
						break # found a gap in the mentor's availability, so stop counting
				if mentorAvailabilityBeforeOverlap < team.transitTimes[transitType]:
					# mentor has to use up some of the overlap time to travel there
					# else travel time before overlap doesn't interfere
					currOverlap -= team.transitTimes[transitType] - mentorAvailabilityBeforeOverlap
				if mentorAvailabilityAfterOverlap < team.transitTimes[transitType]:
					# mentor has to use up some of the overlap time to travel back
					# else travel time after overlap doesn't interfere
					currOverlap -= team.transitTimes[transitType] - mentorAvailabilityAfterOverlap
				if currOverlap >= minMeetingTime:
					# enough of an overlap to count, so add it in
					# else, just ignore this overlap
					totalOverlap += currOverlap
				# overlap ended, so zero out all counters
				currOverlap = 0
				mentorAvailabilityBeforeOverlap = 0
			elif mentor.availability[day][slotNum]:
				# mentor has availability right now, but school doesn't
				# at best, this is time the mentor could use for travel before another overlap, so increment that counter
				mentorAvailabilityBeforeOverlap += minutesPerSlot
			else:
				# mentor has no availability and didn't just finish an overlap, so reset counters
				mentorAvailabilityBeforeOverlap = 0

		if currOverlap > 0:
			# means that the day ended with an overlap, so check to see if it is long enough (minus travel time)
			if mentorAvailabilityBeforeOverlap < team.transitTimes[transitType]:
				# need to charge for some amount of transit time before overlap
				currOverlap -= team.transitTimes[transitType] - mentorAvailabilityBeforeOverlap
			# to be safe since we don't have data for later, I'll assume that the mentor has no availability afterwards
			# so we have to charge for the whole travel time at the end
			currOverlap -= team.transitTimes[transitType]
			if currOverlap >= minMeetingTime:
				totalOverlap += currOverlap

	# find the weight of this transit type for this mentor
	convenience = mentor.transitConveniences[transitType]
	weight = transitConvenienceWeights[transitConvenienceLevels.index(convenience)] # index between the weights and levels lists are the same
	value = totalOverlap * teamOverlapValue * weight

	if weight == 0:
		# this transit type is not good for this mentor, so treat it as if there were no overlap
		return -noOverlapCost
	if totalOverlap == 0:
		# no overlap found, so charge noOverlapCost
		return -noOverlapCost
	if totalOverlap < minMeetingTime:
		# have some overlap, but not as much as we'd want, so penalize the value somewhat
		value -= partialOverlapCost

	return value

def getTeamTypeValue(mentor, team):
	"""
	Get the value for pairing a mentor with a team based on what type of team the mentor wants / what type the team is

	Random thought: as it is set up right now, it gives a flat value if there are any matches regardless of how many there are
					based off our previous system, this makes sense since each team can only be one type
					but in principle we could have multiple non-exclusive descriptors for a team, and give more value if there are more matches
	"""
	for teamType in range(numTeamTypes):
		if mentor.teamTypeRequests[teamType] and team.teamTypes[teamType]:
			return teamTypeMatchValue
	return 0 # no matches :'(

def getTeamRequestedValue(mentor, team):
	"""
	If the mentor must be matched with the team, returns teamRequiredValue
	If the mentor just requested the team, returns teamRequestedValue
	Else returns 0
	"""
	for teamName in mentor.teamsRequired:
		if team.isMatch(teamName):
			return teamRequiredValue
	for teamName in mentor.teamsRequested:
		if team.isMatch(teamName):
			return teamRequestedValue
	return 0

def getTeamCompatibility(mentor, team):
	"""
	Gets a "compatibility score" between a mentor and a team (used as the weight in the later optimization problem)
	Uses the functions defined above to compute different aspects of the score
	"""
	score = 0

	# find value from overlapping availabilities
	# value may differ depending on transportation type used, so try them all
	bestOverlap = -noOverlapCost # baseline to beat is no overlap at all
	for transitType in range(numTypesTransit):
		# check if this transit type is better than previous best and update if needed
		bestOverlap = max(bestOverlap, getTeamOverlapValue(mentor, team, transitType))
	score += bestOverlap

	# find value from team type matches
	score += getTeamTypeValue(mentor, team)

	# find value from team requests / requirements
	score += getTeamRequestedValue(mentor, team)

	return score


"""
Functions for finding the value of a mentor-team pair if the mentor is alone.
"""

def getMentorAloneCost(mentor):
	"""
	Finds the cost of this mentor being alone based on their comfortability with that
	"""
	mentorComfort = mentor.comfortAlone
	mentorIndex = aloneComfortLevels.index(mentorComfort)
	return aloneComfortCosts[mentorIndex]

def getSingleMentorCost(team):
	"""
	Finds the cost (or value if negative) of this team getting only a single mentor
	"""
	teamLevel = team.singleMentorLevel
	teamIndex = singleMentorLevels.index(teamLevel)
	return singleMentorCosts[teamIndex]

def getSkillsValueSingle(mentor, team):
	"""
	Finds the value this mentor alone provides to the team in terms of their skills
	"""
	totalValue = 0

	for skill in range(numSkills):
		mentorConfidence = mentor.skillsConfidence[skill]
		mentorIndex = skillConfidenceLevels.index(mentorConfidence)
		teamRequest = team.skillRequests[skill]
		teamIndex = skillRequestLevels.index(teamRequest)
		totalValue += skillMatchValues[teamIndex][mentorIndex]

	return totalValue

def getAloneCompatibility(mentor, team):
	"""
	Gets a "compatibility score" between a mentor and a team if the mentor is alone
	Uses the functions defined above to compute different aspects of the score
	"""
	score = 0

	# find cost of this mentor being alone
	score -= getMentorAloneCost(mentor)

	# find value (or cost if negative) of this team having only a single mentor
	score -= getSingleMentorCost(team)

	# find value the mentor gives the team from their skills
	score += getSkillsValueSingle(mentor, team)

	return score

"""
Functions for finding the value of a mentor-mentor-team group.
"""

def getGroupOverlapValue(mentor1, mentor2, team):
	"""
	Finds the value of the overlap between a pair of mentors and a team.
	TODO: decide how to quantify this
	"""
	# TODO
	return 0

def getMentorRequestedValue(mentor1, mentor2):
	"""
	Returns the value of pairing these two mentors depending of if the pair was requested / required
	TODO: Assign values and stuff
	"""
	# TODO
	return 0

def getSkillsValuePair(mentor1, mentor2, team):
	"""
	Finds the value two mentors provide to the team in terms of their skills
	For each skill, we take the maximum amount either mentor provides.
	"""
	totalValue = 0

	for skill in range(numSkills):
		mentor1Confidence = mentor1.skillsConfidence[skill]
		mentor1Index = skillConfidenceLevels.index(mentor1Confidence)
		mentor2Confidence = mentor2.skillsConfidence[skill]
		mentor2Index = skillConfidenceLevels.index(mentor2Confidence)
		teamRequest = team.skillRequests[skill]
		teamIndex = skillRequestLevels.index(teamRequest)
		totalValue += max(skillMatchValues[teamIndex][mentor1Index], skillMatchValues[teamIndex][mentor2Index])

	return totalValue

def getGroupCompatibility(mentor1, mentor2, team):
	"""
	Gets a "compatibility score" of a mentor-mentor-team group
	Uses the functions defined above to compute different aspects of the score
	"""
	score = 0

	# find value of the time overlaps of this group
	score += getGroupOverlapValue(mentor1, mentor2, team)

	# add an offset if these two mentors are requested or required to be together
	score += getMentorRequestedValue(mentor1, mentor2)

	# find value the mentors give the team from their skills
	score += getSkillsValuePair(mentor1, mentor2, team)

	return score


