import csv
import unittest

from utils import Mentor


class TestParsingMentor(unittest.TestCase):
    def test_from_string(self):
        raw_csv_line = [
            "Mavericl,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,,,Jessica,1,Inconvenient,Convenient,Convenient,Not possible,Not possible,Somewhat,Very Confident"
        ]
        reader = csv.reader(raw_csv_line)
        processed_line = next(reader)
        mentor = Mentor(processed_line)

        self.assertEqual(mentor.name, "Mavericl")
        self.assertEqual(mentor.teamTypeRequests, [1, 1, 0, 0])
        self.assertEqual(mentor.teamsRequested, [])
        self.assertEqual(mentor.teamsRequired, [])
        self.assertEqual(mentor.mentorsRequired, ["Jessica"])
        self.assertEqual(mentor.comfortAlone, "1")
        self.assertEqual(
            mentor.transitConveniences,
            [
                "Inconvenient",
                "Convenient",
                "Convenient",
                "Not possible",
                "Not possible",
            ],
        )
        self.assertEqual(mentor.skillsConfidence, ["Somewhat", "Very Confident"])


if __name__ == "__main__":
    unittest.main()
