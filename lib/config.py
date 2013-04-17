
from lib.util import read_config


class GlobalConfig(object):
    """GlobalConfig class retrieves information from the file that
    specifies global parameters

    """

    def __init__(self, config):
        self.config = config
        default_dict = self.config.defaults()
        self.key_name = default_dict['key_name']
        self.key_path = default_dict['key_path']
        self.ssh_priv_key = default_dict['ssh_priv_key']
        self.log_local_path = default_dict['log_local_path']
        self.ssh_username = default_dict['ssh_username']
        self.ssh_timeout = default_dict['ssh_timeout']
        self.graph_path = default_dict['graph_path']


class CloudsConfig(object):
    """CloudsConfig class retrieves information from the file that
    specifies global parameters

    """

    def __init__(self, config):
        self.config = config
        self.list = config.sections()


class Benchmark(object):
    """Benchmark class retrieves information from one of the section of
    the benchmarking file

    """

    def __init__(self, benchmark_name, config):
        self.config = config
        self.name = benchmark_name
        dict = self.config.items(self.name)
        self.dict = {}
        # Form a dictionary out of items in the specified section
        for pair in dict:
            self.dict[pair[0]] = pair[1]


class BenchmarkingConfig(object):
    """BenchmarkingConfig class retrieves benchmarking information and
    populates benchmark list

    """

    def __init__(self, config):
        self.config = config
        self.list = list()
        for sec in self.config.sections():
            self.list.append(Benchmark(sec, self.config))


class Config(object):
    """Config class retrieves all configuration information

    """

    def __init__(self, options):
        self.options = options
        self.globals = GlobalConfig(read_config(options.global_file))
        self.clouds = CloudsConfig(read_config(options.clouds_file))
        self.benchmarking = BenchmarkingConfig(read_config(
            options.benchmarking_file))
