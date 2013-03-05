print# coding=utf-8
import logging
import sqlite3
import os

from resources.cloud.clouds import Cloud, Clouds
from resources.cluster.database import Database
from lib.util import read_path,Command,RemoteCommand,check_port_status

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
    def __init__(self, config, avail_clouds, benchmark,cluster_name,database):
        self.config = config
        self.benchmark = benchmark
        self.name = cluster_name
        self.clouds = list()        # clouds from which instances are requested
        self.requests = list()      # number of instances requested
        self.path = list()
        self.database = database
        for option in self.benchmark.dict:
            if(option=="log_files"):
                self.path = read_path(self.benchmark.dict[option])
            elif(option == "url"):
                self.url = self.benchmark.dict[option]
            elif(option == "remote_location"):
                self.remote_location = self.benchmark.dict[option]
            else:
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
                for instance in reservation.instances:
                    self.database.add(self.name,self.clouds[i].name,instance.id,self.benchmark.name)

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
        
        reservations = list()
        if self.reservations:
            reservations = self.reservations
        else:
            for cloud in self.clouds:
                reservations = cloud.conn.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                instance.terminate()
                self.database.terminate(instance.id)
                LOG.debug("Terminated instance: " + instance.id)

    def terminate(self,cluster):
        reservations = list()
        if self.reservations:
            reservations = self.reservations
        else:
            for cloud in self.clouds:
                reservations = cloud.conn.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                if self.database.check(cluster,instance.id):
                    instance.terminate()
                    self.database.terminate(instance.id)
                    LOG.debug("Terminated instance: " + instance.id)

    def download_logs(self):
        reservations = list()
        ssh_username = self.config.globals.ssh_username
        if self.reservations:
            reservations = self.reservations
        else:
            for cloud in self.clouds:
                reservations = cloud.conn.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                if self.database.check_benchmark(self.benchmark.name,instance.id):
                    local_path = os.path.join(self.config.globals.log_local_path,self.benchmark.name,instance.id)
                    if not os.path.exists(local_path):
                        os.makedirs(local_path)
                    for path in self.path:
                        com = "scp "+ssh_username+"@"+instance.public_dns_name+":"+ path +" "+local_path
                        LOG.debug("Download logs: [%s] download %s into %s" % (self.benchmark.name,os.path.basename(path),local_path))
                        command = Command(com)
                        command_return = command.execute()
                        if command_return != 0:
                            LOG.debug("Download logs: "+command.stdout)
                            LOG.debug("Download logs: "+command.stderr)
    
    def deploy_software(self):
        ssh_priv_key = self.config.globals.ssh_priv_key
        ssh_username = self.config.globals.ssh_username
        reservations = list()    
        if self.reservations:
            reservations = self.reservations
        else:
            for cloud in self.clouds:
                reservations = cloud.conn.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                if self.database.check_benchmark(self.benchmark.name,instance.id):
                    while not check_port_status(instance.ip_address,22,2):
                        continue
                    cmds = list()
                    cmds.append("wget %s" % (self.url))
                    cmds.append("apt-get update")
                    cmds.append("apt-get install unzip")
                    cmds.append("unzip BioPerf.zip")
                    cmds.append("sed -i 's/read BIOPERF/#read BIOPERF/g' install-BioPerf.sh")
                    cmds.append("./install-BioPerf.sh")
                    for c in cmds:
                        command = RemoteCommand(instance.public_dns_name,ssh_priv_key,c)
                        command.execute()
                        LOG.debug("Deploy_software: "+command.stdout)
                        LOG.debug("Deploy_software: "+command.stderr)
                

class Clusters(object):
    """ Clusters class represents a collection of clusters specified in the benchmarking file """

    def __init__(self, config):
        self.config = config
        avail_clouds = Clouds(self.config)
        self.database = Database()
        self.list = list()
        a=0
        for benchmark in self.config.benchmarking.list:
            a=a+1
            LOG.debug("Creating cluster for benchmark: " + benchmark.name)
            cluster_name = "cluster-"+str(self.database.countcluster()+a)
            self.list.append(Cluster(self.config, avail_clouds, benchmark,cluster_name,self.database))
    