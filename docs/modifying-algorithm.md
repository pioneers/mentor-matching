
### How To Modify the Convex Program
Note: I strongly recommend against trying to change the basic structure of the convex program.  It's a pain to work with, and almost all the structures I tried prior to this one had too many variables / constraints for `cvxpy` to successfully handle.  If you do have to futz with the structure, I would recommend using only linear constraints as far as possible.  Also, if you have to create a variable for every possible mentor-mentor pair (or for every mentor-mentor-team group), the program probably will not work.

* Variables, constraints, and the objective function are each created in their own block in `assign.py`.
	* Variables should be added to the list `variables`, as well as to the dictionaries `by_type`, `by_mentor`, `by_team`, `by_mentor_team`, and `assignment_group` (where appropriate) for easy access later.
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
