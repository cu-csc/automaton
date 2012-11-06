import logging
import subprocess

from ConfigParser import SafeConfigParser
from optparse import OptionParser


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


def read_config(file):
    config = SafeConfigParser()
    config.read(file)
    return config


def parse_options():
    parser = OptionParser()

    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      help="Enable debugging log level.")
    parser.set_defaults(debug=False)

    parser.add_option("-g", "--global_file", action="store", dest="global_file",
                      help="Location of the file with global parameters (default: etc/global.conf).")
    parser.set_defaults(global_file="etc/global.conf")

    parser.add_option("-c", "--clouds_file", action="store", dest="clouds_file",
                      help="Location of the file with cloud parameters (default: etc/clouds.conf).")
    parser.set_defaults(clouds_file="etc/clouds.conf")

    parser.add_option("-b", "--benchmarking_file", action="store", dest="benchmarking_file",
                      help="Location of the file with benchmarking parameters (default: etc/benchmarking.conf).")
    parser.set_defaults(benchmarking_file="etc/benchmarking.conf")

    (options, args) = parser.parse_args()
    return (options, args)
