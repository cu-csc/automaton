"""
Module that tests various deployment functionality
To run me from command line:
cd automaton/tests
export PYTHONPATH=$PYTHONPATH:../
python -m unittest -v deployment_tests
unset PYTHONPATH

I should have used nose but
"""

import unittest


from lib import util
from deployment import common

class test_deployment_functions(unittest.TestCase):

    def setUp(self):
        self.testing_machine = "vm-148-120.uc.futuregrid.org"
        self.bad_machine_name = "Idonotexistwallah.wrong"
        self.key_filename = "/Users/ali/.ssh/ali_alzabarah_fg.priv"

    def test_port_status_check(self):
        # ssh port
        self.assertFalse(util.check_port_status("google.com"))
        # ssh port
        self.assertTrue(util.check_port_status("research.cs.colorado.edu"))
        # http port
        self.assertTrue(util.check_port_status("google.com",80,2))
        # wrong domain
        self.assertFalse(util.check_port_status("Idonotexistwallah.wrong"))
        # wrong ip
        self.assertFalse(util.check_port_status("256.256.256.256"))


    def test_run_remote_command(self):
        result = util.RemoteCommand(self.testing_machine,
            self.key_filename, "grep ewrqwerasdfqewr /etc/passwd").execute()
        self.assertNotEqual(result,0)

        result = util.RemoteCommand(self.testing_machine,
            self.key_filename, "ls -al /etc/passwd").execute()
        self.assertEqual(result,0)

    def test_clone_git_repo(self):
        self.assertIsNotNone(util.clone_git_repo("https://github.com/alal3177/automaton.git"))

    def test_is_executable(self):
        self.assertFalse(util.is_executable_file("wrong/path"))
        self.assertTrue(util.is_executable_file("/bin/echo"))
        self.assertFalse(util.is_executable_file("/tmp"))

    def test_get_executable_files(self):
        self.assertIsNotNone(common.get_executable_files("/bin"))

if __name__ == '__main__':
    unittest.main()