# coding=utf-8
import logging

from resources.cloud.clouds import Cloud, Clouds

LOG = logging.getLogger(__name__)

class Cluster(object):
    """ Cluster class represents resources used for a set of benchmarks.

    Each section of the file that specifies benchmarks
    might have references to sections of the file that specifies available clouds, e.g.:
      sierra = 0
      hotel = 1
    In this case "sierra" is a reference to the "sierra" cloud, "hotel" is a reference to
    the "hotel" cloud. References should exactly match section names in the cloud file
    (both references and section names are case-sensitive).

    """
    def __init__(self, config, avail_clouds, benchmark):
        self.config = config
        self.benchmark = benchmark
        self.clouds = list()        # clouds from which instances are requested
        self.requests = list()      # number of instances requested
        for option in self.benchmark.dict:
            cloud = avail_clouds.lookup_by_name(option)
            request = int(self.benchmark.dict[option])
            if cloud != None and request > 0:
                self.clouds.append(cloud)
                self.requests.append(request)
        if len(self.clouds) == 0:
            LOG.debug("Benchmark \"%s\" does not have references to available clouds" % (self.benchmark.name))
        self.reservations = list()  # list of reservations that is populated in the launch() method

    def connect(self):
        """ Establishes connections to the clouds from which instances are requested """

        for cloud in self.clouds:
            cloud.connect()

    def launch(self):
        """ Launches requested instances and populates reservation list """

        for i in range(len(self.clouds)):           # for every cloud
            for j in range(self.requests[i]):       # spawn as many instances as requested
                reservation = self.clouds[i].boot_image()
                self.reservations.append(reservation)

    def log_info(self):
        """ Loops through reservations and logs status information for every instance """

        for reservation in self.reservations:
            for instance in reservation.instances:
                status = "Cluster: %s, Reservation: %s, Instance: %s, Status: %s, FQDN: %s, Key: %s" %\
                          (self.benchmark.name, reservation.id, instance.id, instance.state,
                          instance.public_dns_name, instance.key_name)
                LOG.debug(status)

    def get_fqdns(self):
        """ Loops through reservations and returns Fully Qualified Domain Name (FQDN) for every instance """

        fqdns = list()
        for reservation in self.reservations:
            for instance in reservation.instances:
                fqdns.append(instance.public_dns_name)
        return fqdns

    def terminate_all(self):
        """ Loops through reservations and terminates every instance """
        for reservation in self.reservations:
            for instance in reservation.instances:
                instance.terminate()
                LOG.debug("Terminated instance: " + instance.id)

class Clusters(object):
    """ Clusters class represents a collection of clusters specified in the benchmarking file """

    def __init__(self, config):
        self.config = config
        avail_clouds = Clouds(self.config)

        self.list = list()
        for benchmark in self.config.benchmarking.list:
            LOG.debug("Creating cluster for benchmark: " + benchmark.name)
            self.list.append(Cluster(self.config, avail_clouds, benchmark))