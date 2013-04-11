"""
This entire file is just an example to demonstrate functionality of staged deployment.
We will implement the execution workflow here when we have more time.
"""

import shutil

from lib import util
from deployment import common
from deployment.executor import Executor

# config file path
config_file = "../etc/global.conf"

# clone the repo locally
my_local_folder = util.clone_git_repo(util.read_config(config_file).get("DEFAULT","git_repo_location"))

# we fill a dict with our stages
stages = common.get_stages("client", my_local_folder, util.read_config(config_file).get("DEFAULT","git_repo_home"))


# remove the directory since it is not needed anymore
shutil.rmtree(my_local_folder,ignore_errors=True)

# clone the repo to the vm
remote_clone_result = util.RemoteCommand("vm-148-120.uc.futuregrid.org",\
    util.read_config(config_file).get("DEFAULT", "ssh_priv_key"),
    "git clone %s %s" % (util.read_config(config_file).get("DEFAULT","git_repo_location") ,
                         util.read_config(config_file).get("DEFAULT","git_repo_home"))).execute()

# initiate executor class with the stages
exec_obj = Executor("vm-148-120.uc.futuregrid.org",
    util.read_config(config_file).get("DEFAULT", "ssh_priv_key"),
    stages)

# loop over all available stages that has a script with execution bit set and execute it
# if any of the commands at stage 0 failed for example, then we abort the execution and do not go
# to next stage

abort = False
for each_stage in stages:
    if not abort:
        all_commands_result = exec_obj.execute_one_level(each_stage)
        print "done with %s and all commands results are : %s" % (each_stage, str(all_commands_result))
        for command_result in all_commands_result:
            result, stdout, stderr =  all_commands_result[command_result]
            if result != 0:
                abort = True
                break

