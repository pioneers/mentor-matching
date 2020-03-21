import unittest
from utils import Mentor
import csv


class TestParsingMentor(unittest.TestCase):
    def test_from_string(self):
        raw_csv_line = [
            "Mavericl,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,,,Jessica,1,Inconvenient,Convenient,Convenient,Not possible,Not possible,Somewhat,Very Confident"
        ]
        reader = csv.reader(raw_csv_line)
        processed_line = next(reader)
        mentor = Mentor(processed_line)

        self.assertEqual(mentor.name, "Mavericl")


if __name__ == "__main__":
    unittest.main()
