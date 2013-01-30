#!/usr/bin/env python

import logging
import signal
from threading import Thread

from lib.logger import configure_logging
from lib.util import parse_options
from lib.util import read_config
from lib.config import Config
from resources.cloud.clouds import Cloud, Clouds
from resources.cluster.clusters import Clusters

SIGEXIT = False
LOG = logging.getLogger(__name__)


class Automaton(Thread):
    def __init__(self, config, clusters,options):
        Thread.__init__(self)
        self.config = config
        self.clusters = clusters
        self.options = options
    def run(self):
        LOG.info("Starting Automaton")
        #TODO(pdmars): do something

        # Code below demonstrates functionality of Cluster class:
        #for cluster in self.clusters.list:
            #cluster.connect()
            #print "connect"
            #cluster.launch()
            #print "launching"
            #cluster.log_info()
            #print "log_info"
            #fqdns = cluster.get_fqdns()
            #cluster.terminate_all()
            #print "terminate"
        for cluster in self.clusters.list:
            if self.options.launch_cluster:
                print "launch"
                cluster.connect()
                cluster.launch()
            if self.options.terminate_cluster:
                print "terminate"
                cluster.connect()
                if self.options.terminate_cluster=="all":
                    cluster.terminate_all()
                else:
                    cluster.terminate(self.options.terminate_cluster)
            if self.options.show_id:
                cluster.connect()
                cluster.show_id()

def clean_exit(signum, frame):
    global SIGEXIT
    SIGEXIT = True
    LOG.critical("Exit signal received. Exiting at the next sane time. "
                 "Please stand by.")

def main():
    (options, args) = parse_options()
    configure_logging(options.debug)
    
    config = Config(options)
    clusters = Clusters(config)
    
    signal.signal(signal.SIGINT, clean_exit)
    automaton = Automaton(config, clusters, options)
    automaton.start()
    # wake every seconed to make sure signals are handled by the main thread
    # need this due to a quirk in the way Python threading handles signals
    while automaton.isAlive():
        automaton.join(timeout=1.0)

if __name__ == "__main__":
    main()
