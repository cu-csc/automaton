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
    def __init__(self, config, clusters):
        Thread.__init__(self)
        self.config = config
        self.clusters = clusters

    def run(self):
        LOG.info("Starting Automaton")
        #TODO(pdmars): do something

        # Code below demonstrates functionality of Cluster class:
        # for cluster in self.clusters.list:
        #    cluster.connect()
        #    cluster.launch()
        #    cluster.log_info()
        #    fqdns = cluster.get_fqdns()
        #    cluster.terminate_all()

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
