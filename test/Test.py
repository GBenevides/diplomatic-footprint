import unittest
import app_statics
import csv_from_official_doc


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_map_name_test(self):
        meeting = {'Person': 'Person One;Person Two', 'Country': 'Turkey', 'Post': 'presidente;first spouse'}
        list = []
        list += [4, 5]
        self.assertEqual(list, [4,5])
        result = csv_from_official_doc.map_name(meeting)
        print(result)



if __name__ == '__main__':
    unittest.main()
