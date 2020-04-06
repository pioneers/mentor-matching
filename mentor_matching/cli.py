import click

from mentor_matching.match import match
from mentor_matching.mentor import mentors_from_file
from mentor_matching.objective_set import Parameters
from mentor_matching.team import teams_from_file

DEFAULT_MENTOR_DATA_LOCATION = "data/mentors-example.csv"
DEFAULT_TEAM_DATA_LOCATION = "data/teams-example.csv"
DEFAULT_MATCHING_OUTPUT_LOCATION = "output/matching.csv"
DEFAULT_COMPATABILITY_MATRIX_OUTPUT_LOCATION = "output/compability.csv"
DEFAULT_PARAMETERS_LOCATION = "data/parameters.yaml"


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
@click.option(
    "--parameters-data",
    default=DEFAULT_PARAMETERS_LOCATION,
    help="Parameters YAML file location",
)
def run(
    mentor_data,
    team_data,
    matching_output,
    compatability_matrix_output,
    parameters_data,
):
    print("Process started!  Reading mentor file...", flush=True)
    with open(mentor_data) as mentorFile:
        mentors = mentors_from_file(mentorFile)

    print("Reading team file...", flush=True)
    with open(team_data) as team_file:
        teams = teams_from_file(team_file)

    print("Reading parameters...")
    parameters = Parameters.from_file(parameters_data)

    # print("Creating compatibility file...", flush=True)
    # compatability_data_frame = create_team_compatability_data_frame(mentors, teams)
    # compatability_data_frame.to_csv(compatability_matrix_output)
    # print(f"Compatibilities output to {compatability_matrix_output}")

    assignment_set = match(mentors, teams, parameters)

    if assignment_set is None:
        exit(-1)

    with open(matching_output, "w", newline="") as match_file:
        assignment_set.write_match(match_file)
    print(f"Matching output to {matching_output}")


if __name__ == "__main__":
    run()
