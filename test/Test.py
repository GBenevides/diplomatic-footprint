import unittest
import app_statics
import generate_all_data
import data_from_official_doc
import unittest
from unittest.mock import patch
from io import StringIO
from collections import Counter
import pandas as pd
import sys
import app
import TestStatics
import json
import os


class ParseTests(unittest.TestCase):

    def test_map_name_test(self):
        meeting = {'Person': 'Person One;Person Two', 'Country': 'Turkey', 'Post': 'presidente;first-spouse'}
        expected = (['p1', 'p2'], [])
        result = data_from_official_doc.map_name(meeting, "2007")
        self.assertEqual(expected, result)

    def test_generate_2009(self):
        std_data_path_prefix = "../data/Viagens-internacionais-"
        lula = {"2009": [40, 108]}

        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            result = generate_all_data.generate_data_by_year("Lula", lula, std_data_path_prefix, True)
            printed_output = mock_stdout.getvalue().strip()
            self.assertEqual(0, result)
            self.assertEqual(TestStatics.expected_output_2009, printed_output)

    def test_average_meetings_2004(self):
        # Lula
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        df_visits_lula = app.load_data(BASE_DIR, 2004, 2005, "Lula")
        df_visits_lula["president"] = "LULA_KEY"
        self.assertEqual(21, len(df_visits_lula))
        unique_countries = df_visits_lula["Country"].unique()
        countries_string = '\n'.join(unique_countries)
        print_verbose("Distinct countries:\n" + countries_string)
        self.assertEqual(18, len(unique_countries))

        # Basic stats
        meetings_in_trip, sorted_host_code_counts, codes_with_max_count = app.meetings_stats_by_year(df_visits_lula,
                                                                                                     False)
        max_count = max(sorted_host_code_counts.values())
        self.assertEqual(55, meetings_in_trip)
        self.assertEqual(39, len(sorted_host_code_counts.keys()))
        print_verbose("\n\nDistinct names:")
        distinct_names_joined = '\n'.join(sorted_host_code_counts.keys())
        print_verbose(distinct_names_joined)
        self.assertEqual(TestStatics.distinct_names_2004, distinct_names_joined)
        for code, count in sorted_host_code_counts.items():
            print_verbose(f"Code: {app_statics.leaders_mapping[code]['figure']}, Meetings: {count}")
        self.assertEqual(['JC1', 'KO2'], codes_with_max_count)
        self.assertEqual(5, max_count)

    def test_data_consistency(self):
        for entry in app_statics.leaders_mapping.values():
            print_verbose("Entry: " + str(entry))
            self.assertTrue(entry['figure'] and isinstance(entry['figure'], str))
            self.assertTrue(entry['country'] and isinstance(entry['country'], str))
            self.assertTrue(isinstance(entry['posts'], list))

    def test_average_meetings_mock_data(self):
        df_visits_mock = pd.DataFrame.from_records(TestStatics.mock_data)
        df_visits_mock["president"] = "MOCK_KEY"
        self.assertEqual(4, len(df_visits_mock))
        unique_countries = df_visits_mock["Country"].unique()
        countries_string = '\n'.join(unique_countries)
        print_verbose("Distinct countries:\n" + countries_string)
        self.assertEqual(3, len(unique_countries))

        # Basic stats
        meetings_in_trip, sorted_host_code_counts, codes_with_max_count = app.meetings_stats_by_year(df_visits_mock)
        max_count = max(sorted_host_code_counts.values())
        self.assertEqual(9, meetings_in_trip)
        self.assertEqual(5, len(sorted_host_code_counts.keys()))
        print_verbose("\n\nDistinct names:")
        distinct_names_joined = '\n'.join(dict(sorted(sorted_host_code_counts.items())))
        print_verbose(distinct_names_joined)
        self.assertEqual(TestStatics.distinct_names_mock, distinct_names_joined)
        for code, count in sorted_host_code_counts.items():
            print_verbose(f"Code: {app_statics.leaders_mapping[code]['figure']}, Meetings: {count}")
        self.assertEqual(Counter(['AB6', 'AT1']), Counter(codes_with_max_count))
        self.assertEqual(3, max_count)


def print_verbose(token):
    verbose_test = False
    if verbose_test:
        print(token)


if __name__ == '__main__':
    unittest.main()
