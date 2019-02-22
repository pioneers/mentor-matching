import cvxpy as cvx
import numpy as np

num_mentors = 3
num_schools = 2

# Each row is a mentor
# Each col is a school
# Each cell is compatability
# Must have more mentors than schools
mentor_school_compatability = np.array([
    [3, 9],
    [4, 9],
    [2, 9]])

# compatability
# time slot A, time slot B, trait 1, trait 2, trait 3, trait 4

assert mentor_school_compatability.shape[0] == num_mentors, "number of mentors in matrix does not match settings"
assert mentor_school_compatability.shape[1] == num_schools, "number of school in matrix does not match settings"

mentor_school_assignments = cvx.Variable(
    (num_mentors, num_schools), boolean=True)

# We want to maximize the dot product of compatability and assignments
objective = cvx.Maximize(cvx.sum(cvx.multiply(
    mentor_school_compatability, mentor_school_assignments)))

constraints = []

# Every mentor has exactly one school
for mentor_index in range(num_mentors):
    constraints.append(sum(mentor_school_assignments[mentor_index]) == 1)

# Every school has at least one mentor
for school_index in range(num_schools):
    num_mentors_for_school = 0
    for mentor_index in range(num_mentors):
        num_mentors_for_school += mentor_school_assignments[mentor_index, school_index]
    constraints.append(num_mentors_for_school >= 1)


# One optimization might be of the traits
# Time might be the constraints

# Every individual has a time table matrix/vector we must AND them together for a vaild time

problem = cvx.Problem(objective, constraints)
print("Optimal value", problem.solve())
print("Optimal assignment")
print(mentor_school_assignments.value > 0.5)
