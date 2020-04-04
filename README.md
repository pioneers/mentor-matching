# [Catchy Name Placeholder] - Mentor Matching Application
A tool to facilitate mentor matching.

Started by James Hulett at mentor matching February 2018.
Further developed by Scott Numamoto and Vivien Nguyen in 2019.
Yet more development by James Hulett in January 2020.

There are two steps in using the mentor matching program:

0. Collect data from mentors and teams with the data formats in mind
1. Prepare the data on the mentors and teams
2. Decide on the weights to use and run the program to get the matching

## Collect data from mentors and teams

Key pointers:

- Ask mentors and teams their availability in the same format
- Are you adding new questions to factor into mentor matching? If so, read through [docs/data-format](docs/data-format.md) to understand how the answers to this question will be parsed. You also need to understand how the matching is optimized in `mentor_matching/object_set.py` to then modify the file with your data.

## Prepare the data on the mentors and teams

Keep your environment clean with a virtual environment

1. Install virtualenv: `pip install --user virtualenv`
2. Create a virtual environment: `virtualenv venv`
3. Activate the environment: `source venv/bin/activate`
4. Install the dependencies: `pip install -r requirements.txt`
5. Installing `cvxpy` can be difficult - it may require "Microsoft Visual C++ Build Tools". Don't be afraid to Google around or reach out to #edu/software teams for help.

Check that the program is working

5. Test that your installation works: `python main.py --mentor-data data/mentors-example.csv --team-data teams-example.csv`
6. Inspect that result makes sense in `output/`
7. Check that result is still the same previously: `pytest`

Prepare the mentor and team data

8. Read through [docs/data-format.md](docs/data-format.md) to understand how the program parses mentors and teams.
9. Update constants in `mentor_matching/csv_parsing.py` to reflect your data
10. Update `mentor_matching/team.py` and `mentor_matching/mentor.py` with the ordering of your questions and any new data you've collected.
11. Test parsing a single team and mentor by editing `mentor_matching/mentor_test.py` and `mentor_matching/team_test.py`. You can run these tests with `pytest mentor_matching/mentor_test.py`.
12. Ensure your data contains no commas - these mess up CSVs and the parsing
12. Save your data in `data/`
13. Run the program to ensure that parsing all lines work: `python main.py --mentor-data data/mentors.csv --team-data data/teams.csv`
14. Review `output/matching.csv` to ensure the program produced an actual matching

Practice modifying the weights

15. Review what each of the weights do. Encourage all members of the mentor matching meeting to review the weights ahead of the meeting and come prepared with questions. Understanding the weights is critical to choosing them.
16. Try modifying the weights in `data/matching_parameters.yaml` and running the program. Try using different parameters with the `--parameters` flag.
