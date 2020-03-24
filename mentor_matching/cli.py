import click

from mentor_matching.match import match
from mentor_matching.mentor import mentors_from_file
from mentor_matching.team import teams_from_file
from mentor_matching.utils import create_team_compatability_data_frame


DEFAULT_MENTOR_DATA_LOCATION = "data/mentors-example.csv"
DEFAULT_TEAM_DATA_LOCATION = "data/teams-example.csv"
DEFAULT_MATCHING_OUTPUT_LOCATION = "output/matching.csv"
DEFAULT_COMPATABILITY_MATRIX_OUTPUT_LOCATION = "output/compability.csv"


@click.command()
@click.option(
    "--mentor-data",
    default=DEFAULT_MENTOR_DATA_LOCATION,
    help="Mentor data file location",
)
@click.option(
    "--team-data", default=DEFAULT_TEAM_DATA_LOCATION, help="Team data file location"
)
@click.option(
    "--matching-output",
    default=DEFAULT_MATCHING_OUTPUT_LOCATION,
    help="Where to write matching output - which team each mentor is assigned to",
)
@click.option(
    "--compatability-matrix-output",
    default=DEFAULT_COMPATABILITY_MATRIX_OUTPUT_LOCATION,
    help="Where to write compatability matrix - which teams and mentors have compatible times",
)
def run(mentor_data, team_data, matching_output, compatability_matrix_output):
    print("Process started!  Reading mentor file...", flush=True)
    with open(mentor_data) as mentorFile:
        mentors = mentors_from_file(mentorFile)

    print("Reading team file...", flush=True)
    with open(team_data) as team_file:
        teams = teams_from_file(team_file)

    print("Creating compatibility file...", flush=True)
    compatability_data_frame = create_team_compatability_data_frame(mentors, teams)
    compatability_data_frame.to_csv(compatability_matrix_output)
    print(f"Compatibilities output to {compatability_matrix_output}")

    var_set = match(mentors, teams)

    if var_set is None:
        exit(-1)

    with open(matching_output, "w", newline="") as match_file:
        var_set.write_match(match_file)
    print(f"Matching output to {match_file}")


if __name__ == "__main__":
    run()
