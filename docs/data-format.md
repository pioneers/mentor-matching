
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
