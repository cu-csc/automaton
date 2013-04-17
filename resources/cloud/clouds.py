import logging
import os

from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import RegionInfo

LOG = logging.getLogger(__name__)


class Cloud(object):
    """Cloud class provides functionality for connecting to a specified
    cloud and launching an instance there

    cloud_name should match one of the section names in the file that
    specifies cloud information

    """

    def __init__(self, cloud_name, config):
        self.config = config
        self.name = cloud_name
        self.cloud_config = self.config.clouds.config
        self.cloud_uri = self.cloud_config.get(self.name, "cloud_uri")
        self.cloud_port = int(self.cloud_config.get(self.name, "cloud_port"))
        self.cloud_type = self.cloud_config.get(self.name, "cloud_type")
        self.image_id = self.cloud_config.get(self.name, "image_id")
        self.instance_type = self.cloud_config.get(self.name, "instance_type")
        aid = self.cloud_config.get(self.name, "access_id")
        self.access_var = aid.strip('$')
        sk = self.cloud_config.get(self.name, "secret_key")
        self.secret_var = sk.strip('$')
        self.access_id = os.environ[self.access_var]
        self.secret_key = os.environ[self.secret_var]
        self.conn = None

    def connect(self):
        """Connects to the cloud using boto interface"""

        self.region = RegionInfo(name=self.cloud_type, endpoint=self.cloud_uri)
        self.conn = EC2Connection(
            self.access_id, self.secret_key,
            port=self.cloud_port, region=self.region, validate_certs=False)
        self.conn.host = self.cloud_uri
        LOG.debug("Connected to cloud: %s" % (self.name))

    def register_key(self):
        """Registers the public key that will be used in the launched
        instance

        """

        with open(self.config.globals.key_path, 'r') as key_file_object:
            key_content = key_file_object.read().strip()
        import_result = self.conn.import_key_pair(self.config.globals.key_name,
                                                  key_content)
        LOG.debug("Registered key \"%s\"" % (self.config.globals.key_name))
        return import_result

    def boot_image(self):
        """Registers the public key and launches an instance of specified
        image

        """

        # Check if a key with specified name is already registered. If
        # not, register the key
        registered = False
        for key in self.conn.get_all_key_pairs():
            if key.name == self.config.globals.key_name:
                registered = True
                break
        if not registered:
            self.register_key()
        else:
            LOG.debug("Key \"%s\" is already registered" %
                      (self.config.globals.key_name))

        image_object = self.conn.get_image(self.image_id)
        boot_result = image_object.run(key_name=self.config.globals.key_name,
                                       instance_type=self.instance_type)
        LOG.debug("Attempted to boot an instance. Result: %s" % (boot_result))
        return boot_result


class Clouds(object):
    """Clusters class represents a collection of clouds specified in the
    clouds file

    """

    def __init__(self, config):
        self.config = config
        self.list = list()
        for cloud_name in self.config.clouds.list:
            self.list.append(Cloud(cloud_name, self.config))

    def lookup_by_name(self, name):
        """Finds a cloud in the collection with a given name; if does not
        exist, returns None

        """

        for cloud in self.list:
            if cloud.name == name:
                return cloud
        return None
