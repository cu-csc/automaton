#!/usr/bin/env python

import logging
import signal

from lib.logger import configure_logging
from lib.util import parse_options
from lib.util import read_config
from threading import Thread


SIGEXIT = False
LOG = logging.getLogger(__name__)


class Automaton(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.config = config

    def run(self):
        LOG.info("Starting Automaton")
        #TODO(pdmars): do something


def clean_exit(signum, frame):
    global SIGEXIT
    SIGEXIT = True
    LOG.critical("Exit signal received. Exiting at the next sane time. "
                 "Please stand by.")


def main():
    (options, args) = parse_options()
    configure_logging(options.debug)
    config = read_config(options.config_file)
    signal.signal(signal.SIGINT, clean_exit)
    automaton = Automaton(config)
    automaton.start()
    # wake every seconed to make sure signals are handled by the main thread
    # need this due to a quirk in the way Python threading handles signals
    while automaton.isAlive():
        automaton.join(timeout=1.0)

if __name__ == "__main__":
    main()
