import unittest

import json 

import sys
sys.path.append("..")
from distrowatch import get_versions

class TestVersions(unittest.TestCase):

    def setUp(self):
        pass

    def test_get_libs(self):
        libs = get_versions.get_libs()
        test_libs = {"pinned_req": "1.0\n"}
        self.assertEqual(libs, test_libs)

    def test_check_lib(self):
        current = "1.1.0"
        bug = "1.1.1"
        minor = "1.2.1"
        major = "2.1.1"
        none = "1.1.0"
        none2 = "1.1"
        self.assertEqual("none", get_versions.check_lib(current, none))
        self.assertEqual("none", get_versions.check_lib(current, none2))
        self.assertEqual("bug", get_versions.check_lib(current, bug))
        self.assertEqual("minor", get_versions.check_lib(current, minor))
        self.assertEqual("major", get_versions.check_lib(current, major))

    def test_create_json(self):
        distros = {"minor": ["somelib"],
             "major": ["otherlib", "finallib"]}
        get_versions.create_json(distros)
        f = open("distros.json")
        saved = json.load(f)
        self.assertEqual(saved, distros)

if __name__ == '__main__':
    unittest.main()