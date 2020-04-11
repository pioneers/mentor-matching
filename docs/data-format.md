# Data Format

This documents explains the format of the data for mentors and teams.

You can make many simple configuration changes by adjusting the constants in
`mentor_matching/csv_parsing.py`.

## Mentor Data Format
There should be 1 (configurable) header row (which will be ignored). Every row thereafter
should correspond to a mentor.

The columns should be organized as follows:
* 1 column for mentor name.
* `7*24 = 168` (configurable) columns for availability, where a `1`
  (configurable) represents the mentor being available in that time slot and
  a `0` represents them being unavailable.
* 4 (configurable) columns for which team type(s) (eg new, small coach
  presence, etc) the mentor would like to work with, where a `1` (configurable)
  represents the mentor wanting to work with that team type and a `0`
  represents them not.
* 1 column for team(s) this mentor would like to be matched with, separated by
  a semicolon if there are multiple (blank if none).  Any such names must
  appear exactly as they do in `teams.csv`.
* 1 column for comfort mentoring alone (configurable: must be a number from 1
  to 5, with 5 as most confident).
* 5 (configurable) columns for convenience of different transit types (each must be "Not
  possible", "Inconvenient", or "Convenient" (configurable)).
* 5 (configurable) columns for confidence in 2 (configurable) skills (each must be "Not Confident",
  "Somewhat", "Neutral", "Confident", or "Very Confident" (configurable)).

In cases where there are multiple columns (ie, availability, transit
conveniences, etc), the columns must be in the same order as in `teams.csv`.

## Team Data Format
There should be one header row (which will be ignored), and every row
thereafter should correspond to a team.

The columns should be organized as follows:
* 1 column for team name.
* Availabilty columns which must be the same as done for mentors
* What team type is this team in the same format as done for mentors
* 5 (configurable) columns for how long each travel method would take, as an
  integer number of minutes.  If the team plans on working with their mentor(s)
  on the Berkeley campus, put in 0 for these columns.
* 5 (configureable) columns for how much the team wants the 2 (configurable)
  different skills (each must be "Not at all", "Somewhat", or "Very").

In cases where there are multiple columns (ie, availability, transit times,
etc), the columns must be in the same order as in `mentors.csv`.

## How To Modify the Input Format

To modify what the values in a column type should look like or how many
columns of that type there should be:

* change the appropriate lines in `mentor_matching/mentor.py::from_list` or
  `mentor_matching/team.py::from_list`
* Test your change by altering
  `mentor_matching/mentor_test.py::test_from_string` - run `make test`
* update the lines in [Mentor Data Format](#mentor-data-format) and
  [Team Data Format](#team-data-format)
* update the format in `mentors-example.csv` and `teams-example.csv`. Note that
  all values are read from the csv as strings.

To remove a column type:

* Skip over the unneeded columns by incrementing `position` without processing
  the data in `from_list` OR modify the CSV itself and remove processing and
  incrementing
* Delete the field from the object and constructors if necessary
* Update and run tests: `make test`
* Update any documentation in [Mentor Data Format](#mentor-data-format) and
  [Team Data Format](#team-data-format).

To add a column type, add:

* add new parameters to Mentor or Team constructors
* Update object docstrings
* add processing of the new column in `from_list`
* Update the CSV data
* Update and run tests: `make test`
* Update any documentation in [Mentor Data Format](#mentor-data-format) and
  [Team Data Format](#team-data-format).

To change the order of the columns:

* Rearrange `from_list`
* Rearrange the corresponding lines in
  [Mentor Data Format](#mentor-data-format) and
  [Team Data Format](#team-data-format).
* Rearrange the columns of the sample data
