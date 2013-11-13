Automaton
=========

Automaton automates the process of executing benchmark applications on various
resources (e.g., infrastructure clouds and clusters). Ideally this will include 
all steps from provisioning cloud resources, downloading, configuring, and 
compiling the benchmark applications, executing the applications, gathering the 
results, and generating graphs.

Prerequisites
-------------

Automaton requires that numpy, fabirc, boto, and matplotlib libraries be installed.
The easiest way to install these libraries is through [pip]

Numpy can be installed with the command:

    pip install numpy

All other libraries can be automatically installed using pip by giving the command:

    pip install -r requirements.txt

After installing the required libraries, Automaton should be ready to run. Check 
by running Automaton with:

    python ./automaton.py -h

If a help message is shown, then the required libraries have been installed 
successfully. 

Configuration & Environment Variables
---------------------------------------

Automaton has a global configuration files that needs to be preconfigured before
benchmarks can be run -- etc/global.conf. Because Automaton uses ssh to connect
to servers, you must provide the path to your public and private keys. Assuming 
you already have generated a key pair (if not, see Github's [guide to generating
ssh keys]), the two lines that need to be edited are:

    key_path = path/to/public/key
    ssh_priv_key = path/to/private/key


In addition to configuring etc/global.conf with your ssh keys, Automaton also 
requires that your credentials from the cloud server that you are accessing be
available. 

For example, using the Nimbus cloud on [FutureGrid]:

    ssh <username>@hotel.futuregrid.org
    cd .nimbus
    cat querytokens.sh

Run the two export commands on the local machine. 

Automaton should now be configured and ready to run.


Running Automaton
-----------------

Deploying the Automaton software, executing the benchmarks, and gathering and 
generating graphs is accomplished through the use of flags that can be seen by
running:

    python automaton.py -h

Generally, the first command to run, in order to launch the desired clusters
specified in the etc/cloud.conf file is:

    python automaton.py -l

Then, the software can be deployed with:

    python automaton.py -s

The benchmarks can be executed with:

    python automaton.py -e

Executing the benchmarks may take some time to complete, but once they are finished
running the logs can be gathered with:

    python automaton.py -o

And finally the graphs generated with:

    python automaton.py -p

A specific instance or all of the running clusters can be terminated with:

    python automaton.py -t <all/instance id>


Contributing
------------

1. Read: http://www.python.org/dev/peps/pep-0008/
2. Run pep8 and make sure your code conforms.

<!-- references -->
[pip]: http://www.pip-installer.org/en/latest/
[guide to generating ssh keys]: https://help.github.com/articles/generating-ssh-keys
[FutureGrid]: http://www.futuregrid.org