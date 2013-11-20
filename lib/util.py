import logging
import subprocess
import socket
import tempfile
import os
import datetime

from ConfigParser import SafeConfigParser
from optparse import OptionParser
from fabric import api as fabric_api

LOG = logging.getLogger(__name__)


class Command(object):
    def __init__(self, args=[]):
        self.stdout = None
        self.stderr = None
        self.args = args

    def execute(self):
        process = subprocess.Popen(self.args, shell=True,
                                   executable="/bin/bash",
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        (self.stdout, self.stderr) = process.communicate()
        return process.returncode


class RemoteCommand(object):
    """Run a command in a remote machine.

    Given a machine address, a none interactive command and ssh key,
    the function uses fabric to execute the command in the remote
    machines.

    Args:

        hostname (string) : address of the machine

        ssh_private_key (string) : absolute path to ssh private key

        command ( string ) : command to execute


    Return:

        bool

    """

    def __init__(self, hostname, ssh_private_key, command):
        self.stdout = None
        self.stderr = None
        self.command = command
        self.hostname = hostname
        self.ssh_private_key = ssh_private_key

    def execute(self):
        if os.path.isfile(self.ssh_private_key):
            context = fabric_api.settings(fabric_api.hide('running',
                                                          'stdout',
                                                          'stderr',
                                                          'warnings'),
                                          user="root",
                                          key_filename=[self.ssh_private_key],
                                          disable_known_hosts=True,
                                          linewise=True,
                                          warn_only=True,
                                          abort_on_prompts=False,
                                          always_use_pty=True,
                                          timeout=5)

        else:
            LOG.debug("Path to ssh private key is invalid")
            return None

        if context:
            with context:
                fabric_api.env.host_string = self.hostname
                try:
                    results = fabric_api.run(self.command)
                    self.stdout = results.stdout
                    self.stderr = results.stderr
                    return results.return_code
                except Exception as expt:
                    LOG.debug("Exception in running remote command: %s" %
                              str(expt))
                    return None
        else:
            LOG.debug("issue initializing fabric context")
            return None


def read_config(file):
    config = SafeConfigParser()
    config.read(file)
    return config


def parse_options():

    parser = OptionParser()

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Enable debugging log level.")
    parser.set_defaults(debug=False)

    parser.add_option("-g", "--global_file", action="store",
                      dest="global_file",
                      help="Location of the file with global parameters "
                           "(default: etc/global.conf).")
    parser.set_defaults(global_file="etc/global.conf")

    parser.add_option("-c", "--clouds_file", action="store",
                      dest="clouds_file",
                      help="Location of the file with cloud parameters "
                           "(default: etc/clouds.conf).")
    parser.set_defaults(clouds_file="etc/clouds.conf")

    parser.add_option("-b", "--benchmarking_file", action="store",
                      dest="benchmarking_file",
                      help="Location of the file with benchmarking "
                           "parameters (default: etc/benchmarking.conf).")
    parser.set_defaults(benchmarking_file="etc/benchmarking.conf")

    parser.add_option("-l", "--launch_cluster", action="store_true",
                      dest="launch_cluster",
                      help="Launch desired number of clusters")

    parser.add_option("-t", "--terminate_cluster", action="store",
                      dest="terminate_cluster",
                      help="Terminate specific instance, argument: "
                           "all/instance_id",
                      default=False)

    parser.add_option("-s", "--deploy_software", action="store_true",
                      dest="deploy_software", help="Deploy Software")

    parser.add_option("-e", "--execute_benchmarks", action="store_true",
                      dest="execute_benchmarks", help="execute benchmarks")

    parser.add_option("-o", "--gather_logs", action="store_true",
                      dest="gather_logs", help="Gather logs")

    parser.add_option("-p", "--generate_graphs", action="store_true",
                      dest="generate_graphs",
                      help="Generate graphs that based on the collected logs")

    parser.add_option("-i", "--show_id", action="store_true", dest="show_id",
                      help="show the id of all running instances")
    (options, args) = parser.parse_args()

    return (options, args)


def check_port_status(address, port=22, timeout=2, status_timeout=60):
    """Check weather a remote port is accepting connection.

    Given a port and an address, we establish a socket connection
    to determine the port state

    Args :
        address (string): address of the machine, ip or hostname
        port (int) : port number to connect to
        timeout (int) : time to wait for a response

    return :
        bool
            True: if port is accepting connection
            False : if port is not accepting

    """
    starttime = datetime.datetime.now()
    endtime = starttime
    while ((endtime-starttime).seconds) < status_timeout:
        default_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_socket.connect((address, port))
        except Exception as inst:
            LOG.debug("Exception in check_port_status : %s" % (str(inst)))
            endtime = datetime.datetime.now()
            continue
        finally:
            remote_socket.close()
            socket.setdefaulttimeout(default_timeout)
        return True
    return False


def clone_git_repo(repo_src):
    """Clone a git repo

    given a repo location, clone it locally and return the directory path

    Args:
        repo_src (string): git repo src location

    Return:
        repo_dest (string): directory that contains the cloned repo

    """
    repo_dest = tempfile.mkdtemp(dir="/tmp")
    clone_cmd_obj = Command("git clone %s %s" % (repo_src, repo_dest))
    if clone_cmd_obj.execute() == 0:
        return repo_dest


def is_executable_file(file_path):
    """Check if a given file is executable

    Args:
        file_path (string) : file absolute path

    Return:
        bool

    """
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)


def read_path(path_src):
    if len(path_src and ',') == 1:
        path_src = path_src.replace(' ', '').replace('\n', '')
        paths = path_src.split(",")
        return paths
