# [Catchy Name Placeholder] - Mentor Matching Application
A tool to facilitate mentor matching.

Started by James Hulett at mentor matching February 2018.
Further developed by Scott Numamoto and Vivien Nguyen in 2019.
Yet more development by James Hulett in January 2020.

### README Table of Contents
[Usage](#usage)  
[Mentor Data Format](#mentor-data-format)  
[Team Data Format](#team-data-format)  
[How To Modify the Input Format](#how-to-modify-the-input-format)  
[How To Change the Weights](#how-to-change-the-weights)  
[How To Modify the Convex Program](#how-to-modify-the-convex-program)  
[Description of the Convex Program](#description-of-the-convex-program)  
[TODOs](#todos)  


### Usage
1. Install the libraries listed in `requirements.txt`.  Note that `cvxpy` may require you to have "Microsoft Visual C++ Build Tools".  If this happens, you should probably ask someone who actually knows what they are doing how to make that work, since it's kind of a pain.

2. Put mentor data in a file called `mentors.csv` and team data in a file called `teams.csv`.  Data should be formatted as described in the next
two sections.  See `mentors-example.csv` and `teams-example.csv` for example data formatting.

3. Ensure that there are no commas in any of the data.  Commas may cause the csv to be parsed incorrectly.

4. Run `assign.py`.  The matching will be output to `matching.csv`; a mentor-team compatibility matrix will be output to `compatibility.csv`.


### Mentor Data Format
There should be one header row (which will be ignored), and every row thereafter should correspond to a mentor.

The columns should be organized as follows:
* 1 column for mentor name.
* 70 columns for availability, where a 1 represents the mentor being available in that time slot and a 0 represents them being unavailable.
* 4 columns for which team type(s) (eg new, small coach presence, etc) the mentor would like to work with, where a 1 represents the mentor wanting to work with that team type and a 0 represents them not.
* 1 column for team(s) this mentor would like to be matched with, separated by a semicolon if there are multiple (blank if none).  Any such names must appear exactly as they do in `teams.csv`.
* 1 column for team(s) this mentor *must* be matched with, separated by a semicolon if there are multiple (blank if none).  Any such names must appear exactly as they do in `teams.csv`.
* 1 column for other mentor(s) mentor *must* be matched with, separated by a semicolon if there are multiple (blank if none).  Any such names must be exactly the same as the name given in the first column of the other mentor(s)' row.
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
1. One boolean variable for each mentor-team pair, representing if that mentor is paired with that team and is alone
2. One boolean variable for each mentor-team pair, representing if that mentor AND at least one other are paired with that team

Constraints:  
1. The sum of a team's type 2 variables plus twice the sum of its type 1 variables must be at least 2.  This ensures that if only one mentor is assigned to the team, the program must use the corresponding type 1 variable, and not the type 2 variable.
2. The sum of a mentor's type 1 and 2 variables is exactly 1.  This ensures that a mentor gets matched with exactly one team.
3. The sum of a team's type 1 and 2 variables is between 1 and 2.  This ensures that a team gets an appropriate number of mentors.
4. For every pair of mentors who are required to be together, the sum of all their type 1 variables must be zero.  This ensures that mentors who are supposed to be paired together don't end up alone.
5. For every pair of mentors who are required to be together and for each team, the difference between the type 2 variables for those mentors and that team must be greater than or equal to zero.  This ensures that these mentors will be together, as if the second mentor is assigned to a team the first mentor isn't, that difference will be negative.  This assumes these mentors aren't assigned using type 1 variables, which the constraints of type 4 guarantee.

Terms in the Objective Function:  
1. For each type 1 variable, we have (the value of that mentor-team matching minus the cost of the mentor being alone) times the variable.
2. For each type 2 variable, we have the value of that mentor-team matching times the variable.

Note that based on how the constraints are set up, there is nothing to stop the program from using type 1 variables when there are actually multiple mentors assigned to that team.  However, as it is currently set up, you can only incur an extra cost by doing that, so there's no reason for the program to do so.  But this does mean that we can only ever have solo-mentoring incur a cost--we can never treat it as adding value without changing the structure of the constraints.


### TODOs
