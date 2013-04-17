"""
Module that handle the staged deployment execution
"""

from lib import util


class Executor(object):

    def __init__(self, hostname, private_key, staged_dict):
        self.hostname = hostname
        self.private_key = private_key
        self.staged_dict = staged_dict

    def execute_one_level(self, run_level):

        result_dict = {}
        cmds_in_run_level = self.staged_dict[run_level]

        for command in cmds_in_run_level:
            remote_command = util.RemoteCommand(self.hostname,
                                                self.private_key, command)
            return_code = remote_command.execute()
            result_dict[command] = (return_code, remote_command.stdout,
                                    remote_command.stderr)

            if return_code != 0:
                break
        return result_dict
