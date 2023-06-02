import unittest
import app_statics
import generate_all_data
import csv_from_official_doc
import unittest
from unittest.mock import patch
from io import StringIO
import sys

expected_output_2009 = '''Lula 2009
Inconsistent posts:
 []
Total state visits: 108
Done!
--------------'''

class ParseTests(unittest.TestCase):

    def test_map_name_test(self):
        meeting = {'Person': 'Person One;Person Two', 'Country': 'Turkey', 'Post': 'presidente;first-spouse'}
        expected = [{'figure': 'Person One', 'country': 'SomeCountry', 'posts': ['president']},
                    {'figure': 'Person Two', 'country': 'SomeCountry', 'posts': ['First-spouse']}], ['p1']
        result = csv_from_official_doc.map_name(meeting, "2007")
        self.assertEqual(result, expected)

    def test_generate_2009(self):
        std_data_path_prefix = "../data/Viagens-internacionais-"
        lula = {"2009": [40, 108]}

        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            result = generate_all_data.generate_csv_by_year("Lula", lula, std_data_path_prefix, True)
            printed_output = mock_stdout.getvalue().strip()
            self.assertEqual(0, result)
            self.assertEqual(expected_output_2009, printed_output)


if __name__ == '__main__':
    unittest.main()
