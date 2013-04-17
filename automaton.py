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
from graphing.graphing import Graph

SIGEXIT = False
LOG = logging.getLogger(__name__)


class Automaton(Thread):
    def __init__(self, config, clusters):
        Thread.__init__(self)
        self.config = config
        self.clusters = clusters

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
        if self.config.options.show_id:
            self.clusters.database.printdata()
        if self.config.options.generate_graphs:
            graph = Graph(self.config)
            graph.generate_graph()
        for cluster in self.clusters.list:
            if self.config.options.launch_cluster:
                cluster.connect()
                cluster.launch()
            if self.config.options.terminate_cluster:
                cluster.connect()
                if self.config.options.terminate_cluster == "all":
                    cluster.terminate_all()
                else:
                    cluster.terminate(self.config.options.terminate_cluster)
            if self.config.options.gather_logs:
                cluster.connect()
                cluster.download_logs()
            if self.config.options.deploy_software:
                cluster.connect()
                cluster.deploy_software()
            if self.config.options.excute_benchmarks:
                cluster.connect()
                cluster.excute_benchmarks()


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
    automaton = Automaton(config, clusters)
    automaton.start()
    # wake every seconed to make sure signals are handled by the main thread
    # need this due to a quirk in the way Python threading handles signals
    while automaton.isAlive():
        automaton.join(timeout=1.0)

if __name__ == "__main__":
    main()
