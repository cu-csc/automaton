import logging


def configure_logging(debug=False):
    formatter = logging.Formatter("%(asctime)s - %(name)-16s - "
                                  "%(levelname)-8s - %(message)s")
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    if debug:
        logging.getLogger('').setLevel(logging.DEBUG)
    else:
        logging.getLogger('').setLevel(logging.INFO)
