# [Catchy Name Placeholder] - Mentor Matching Application
A tool to facilitate mentor matching.

Started by James Hulett at mentor matching February 2018.
Further developed by Scott Numamoto and Vivien Nguyen in 2019.
Yet more development by James Hulett in January 2020 and January 2021.

### README Table of Contents
[Usage](#usage)  
[Choosing A Solver](#choosing-a-solver)
[Mentor Data Format](#mentor-data-format)  
[Team Data Format](#team-data-format)  
[How To Modify the Input Format](#how-to-modify-the-input-format)  
[How To Change the Weights](#how-to-change-the-weights)  
[How To Modify the Convex Program](#how-to-modify-the-convex-program)  
[Description of the Convex Program](#description-of-the-convex-program)  
[TODOs](#todos)  


### Usage
1. Install the libraries listed in `requirements.txt`.  Note that `cvxpy` may require you to have "Microsoft Visual C++ Build Tools".  If this happens, you should probably ask someone who actually knows what they are doing how to make that work, since it's kind of a pain.

2. If using the Gurobi solver (see the [Choosing A Solver](#choosing-a-solver) section), run `pip install -i https://pypi.gurobi.com gurobipy`.  You will also need to sign up for a (free) academic license at https://www.gurobi.com/downloads/end-user-license-agreement-academic/.  TODO: Check if you need to be on AirBears to get the license.

3. Put mentor data in a file called `mentors.csv` and team data in a file called `teams.csv`.  Data should be formatted as described in the next
two sections.  See `mentors-example.csv` and `teams-example.csv` for example data formatting.

4. Ensure that there are no commas in any of the data.  Commas may cause the csv to be parsed incorrectly.

5. Run `assign.py`.  The matching will be output to `matching.csv`; a mentor-team compatibility matrix will be output to `compatibility.csv`.  If you want to use the Gurobi solver instead of the `cvxpy` solver, run `assign.py -g`.

6. On finishing, `assign.py` will print out the value of the solution it found.  If this value is negative, you should manually check the matching to see what's going on and if it needs fixing; it probably means that either (i) a mentor was assigned to a team that they have insufficient time overlap with, (ii) a mentor was not assigned to a team they were required to be assigned to, or (iii) mentors who were required to be assigned together are not.  If this does happen, the two most likely culprits are either (i) a mentor was required to be paired with a team they have insufficient time overlap with (fix by removing that requirement, or just ignore it if we know it won't be an issue), or (ii) there is no matching such that every mentor is paired with a team they have sufficient time overlap with (no easy fix, other than potentially bugging mentors / teams to give us more availabilities to work with).


### Choosing A Solver
When running the program, you have the choice between two solvers: Gurobi and `cvxpy`.  The default is `cvxpy`, since Gurobi requires a (free) academic license, and so is marginally more work to set up.  However, Gurobi has advantages if running on an instance with a larger number of teams / mentors--it is generally faster, provides mid-run updates on its progress towards the optimal solution, and still outputs a (suboptimal but probably not too bad) solution if you terminate it early.  To run with the `cvxpy` solver, simply run the program as usual; to use the Gurobi solver, run it with a `-g` tag.


### Mentor Data Format
There should be one header row (which will be ignored), and every row thereafter should correspond to a mentor.

The columns should be organized as follows:
* 1 column for mentor name.
* 70 columns for availability, where a 1 represents the mentor being available in that time slot and a 0 represents them being unavailable.
* 4 columns for which team type(s) (eg new, small coach presence, etc) the mentor would like to work with, where a 1 represents the mentor wanting to work with that team type and a 0 represents them not.
* 1 column for team(s) this mentor would like to be matched with, separated by a semicolon if there are multiple (blank if none).  Any such names must appear exactly as they do in `teams.csv`.
* 1 column for team(s) this mentor *must* be matched with, separated by a semicolon if there are multiple (blank if none).  Any such names must appear exactly as they do in `teams.csv`.
* 1 column for other mentor(s) this mentor would like to be matched with, separated by a semicolon if there are multiple (blank if none).  Any such names must be exactly the same as the name given in the first column of the other mentor(s)' row.
* 1 column for other mentor(s) this mentor *must* be matched with, separated by a semicolon if there are multiple (blank if none).  Any such names must be exactly the same as the name given in the first column of the other mentor(s)' row.
* 1 column for comfort mentoring alone (must be a number from 1 to 5, with 5 as most confident).
* 5 columns for convenience of different transit types (each must be "Not possible", "Inconvenient", or "Convenient").
* 5 columns for confidence in skills (each must be "Not Confident", "Somewhat", "Neutral", "Confident", or "Very Confident").

In cases where there are multiple columns (ie, availability, transit conveniences, etc), the columns must be in the same order as in `teams.csv`.


### Team Data Format
There should be one header row (which will be ignored), and every row thereafter should correspond to a team.

The columns should be organized as follows:
* 1 column for team name.
* 70 columns for availability, where a 1 represents the team being available in that time slot and a 0 represents them being unavailable.
* 4 columns for which team type (eg new, small coach presence, etc) this team is, where a 1 represents the team being that type and a 0 represents the team not being that type.
* 1 column for how good/bad it would be for this team to get only one mentor (must be "Bad", "Neutral", or "Good")
* 5 columns for how long each travel method would take, as an integer number of minutes.  If the team plans on working with their mentor(s) on the Berkeley campus, put in 0 for these columns.
* 5 columns for how much the team wants the different skills (each must be "Not at all", "Somewhat", or "Very").

In cases where there are multiple columns (ie, availability, transit times, etc), the columns must be in the same order as in `mentors.csv`.


### How To Modify the Input Format
* If you want to modify what the values in a column type should look like or how many columns of that type there should be, change the appropriate variable in `utils.py`, update the lines in [Mentor Data Format](#mentor-data-format) and [Team Data Format](#team-data-format), and update the format in `mentors-example.csv` and `teams-example.csv`.  Note that all values are read from the csv as strings.

* If you want to remove a column type, delete
	* The corresponding variables in `utils.py`.
	* The lines in the `__init__` functions for the `Mentor` and `Team` classes (in `utils.py`) that read in that column type.
	* The name and description of any corresponding attributes in the comments above the `Mentor` and `Team` classes.
	* The corresponding line(s) in [Mentor Data Format](#mentor-data-format) and [Team Data Format](#team-data-format).
	* The corresponding column(s) in `mentors-example.csv` and `teams-example.csv`.

* If you want to add a column type, add
	* Any necessary new variables in `utils.py` (ie, number of columns, possible values, etc), with comments for what each is for.  Note that all values are read from the csv as strings.
	* Lines in the `__init__` functions for the `Mentor` and `Team` classes (in `utils.py`) to read in that column type.
	* The name and description of any corresponding attributes in the comments above the `Mentor` and `Team` classes.
	* Corresponding line(s) in [Mentor Data Format](#mentor-data-format) and [Team Data Format](#team-data-format).
	* Corresponding column(s) in `mentors-example.csv` and `teams-example.csv`.

* If you want to change the order of the columns,
	* Rearrange the corresponding blocks in the `__init__` functions for the `Mentor` and `Team` classes (in `utils.py`).
	* Rearrange the corresponding lines in [Mentor Data Format](#mentor-data-format) and [Team Data Format](#team-data-format).
	* Rearrange the columns in `mentors-example.csv` and `teams-example.csv`.


### How To Change the Weights
* If you just want to change the weight given to some parameter, update the corresponding variable in `utils.py`.

* If you want to modify how a component of the mentor-team compatibility score is calculated, modify the corresponding function in `utils.py`.

* If you want to add / delete a component of the mentor-team compatibility score, add / delete the corresponding function in `utils.py` and the corresponding block in `getTeamCompatibility` (in `utils.py`).

* If you want to change how many mentors are assigned to each team, modify `minNumMentors` and `maxNumMentors` in `utils.py`.


### How To Modify the Convex Program
Note: I strongly recommend against trying to change the basic structure of the convex program.  It's a pain to work with, and almost all the structures I tried prior to this one had too many variables / constraints for `cvxpy` to successfully handle.  If you do have to futz with the structure, I would recommend using only linear constraints as far as possible.  Also, if you have to create a variable for every possible mentor-mentor pair (or for every mentor-mentor-team group), the program probably will not work.

* Variables, constraints, and the objective function are each created in their own block in `assign.py`.
	* Variables should be added to the list `variables`, as well as to the dictionaries `varByType`, `varByMentor`, `varByTeam`, `varByPair`, and `groupByVar` (where appropriate) for easy access later.
	* Constraints should be appended to the list `constraints`.
	* Terms in the objective function should be appended to the list `objectiveTerms`.  The objective function is just the sum of all these terms.
* If you modify the structure of the program, please update [Description of the Convex Program](#description-of-the-convex-program) accordingly.


### Description of the Convex Program
This section describes the convex program that is used to find a matching.  Hopefully no one will ever have to read this.

Variables:  
1. One boolean variable for each mentor-team pair, representing if that mentor is paired with that team (independent of co-mentors)
2. One boolean variable for each team, representing if that team has only one mentor
3. One boolean variable for each mentor-team pair, representing if that mentor is paired with that team and is alone
4. One boolean variable for each mentor-mentor-team group, representing if both those mentors are paired with the team

Constraints:  
1. The sum of a mentor's type 1 variables must equal 1.  This ensures that every mentor is paired with exactly one team.
2. The sum of a team's type 1 variables must be between `utils.minNumMentors` and `utils.maxNumMentors`.  This ensures that every team is paired with an appropriate number of mentors.
3. Letting M be the number of mentors, each team's type 2 variable must be less than or equal to (1/M) * (M + 1 - the sum of the team's type 1 variables).  This ensures that every team's type 2 variable is set to zero if it has more than one mentor assigned.
4. Each team's type 2 variable must be greater than or equal to (2 - the sum of the team's type 1 variables).  This ensures that every team's type 2 variable is set to 1 if it has one mentor.  This will break if the sum is zero, but that cannot happen so long as `utils.minNumMentors` is strictly greater than zero.
5. The sum of a team's type 3 variables is equal to its type 2 variable.  This ensures that type 3 variables are used if and only if there is exactly one mentor assigned to the team.
6. Each variable of type 3 is less than or equal to the corresponding variable of type 1.  This ensures that type 3 variables are only used when the corresponding mentor and team are actually paired.
7. Letting M be the number of mentors, the sum of a mentor-team pair's type 4 variables is at most M times its type 1 variable.  This ensures that a type 4 variable can only be set to 1 if both corresponding mentors are assigned to the corresponding team.

Terms in the Objective Function:  
1. For each type 1 variable, we have the value of that mentor-team matching (independent of co-mentors) times the variable.
2. For each type 3 variable, we have the value of the mentor gives the team alone times the variable.
3. For each type 4 variable, we have the value the two mentors give the team together times the variable.
4. For each pair of mentors that must be together, subtract `utils.mentorRequiredValue`.  Similarly, for each mentor that must be with a specific team, subtract `utils.teamRequiredValue`.  Note that these offsets are independent of the solution, and so won't change the optimum; their only purpose is to make it such that solutions that don't satisfy all requirements have a negative value, making it easier to spot if this happens.

Note that based on how the constraints are set up, there is nothing requiring type 4 variables to be set to 1.  Hence, we need to ensure that type 4 variables can only give positive value to the program.  In particular, this means that the cost for not having time overlaps between a mentor and a school have to be charged to the type 1 variables, not to the type 3/4 ones.  Additionally, note that the type 7 constraints allow us to set all type 4 variables to 1 provided that both corresponding mentors are assigned to the corresponding team.  Hence, the value we get from type 3 objective function terms grows quadratically with the number of mentors assigned to a team.  For this reason, it is recommended that `utils.minNumMentors` and `utils.maxNumMentors` differ by at most 1.  If the difference is larger than 1, the program will likely prefer assignments that give some teams many mentors and other teams few mentors, whereas we would prefer it to assign all teams an approximately equal number of mentors.


### TODOs

* Verify that Gurobi instructions work.

* Calculate the amount of availability overlap between a team and two mentors in a less overly-optimistic way.