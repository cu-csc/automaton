import os
import time
import novaclient.exceptions as exception
import novaclient.v1_1.client as nvclient
from credentials import get_nova_creds

class NovaAPITest(object):

    def __init__(self):
        self.creds = get_nova_creds()
        self.nova = nvclient.Client(**self.creds)

        print "Checking for keypair and importing if not found"
        if not self.nova.keypairs.findall(name="mykey"):
            with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
                self.nova.keypairs.create(name="mykey", public_key=fpubkey.read())


        self.image = self.nova.images.find(name="futuregrid/ubuntu-12.04-03-Mar-2014")
        self.flavor = self.nova.flavors.find(name="m1.tiny")

    def create(self, name):
        print "Creating instance of " + str(self.image) + " of flavor " + str(self.flavor)
        instance = self.nova.servers.create(name=name, image=self.image, flavor=self.flavor, key_name="mykey")

        # Poll at 5 second intervals, until the status is no longer 'BUILD'
        status = instance.status
        while status == 'BUILD':
            time.sleep(5)
            # Retrieve the instance again so the status field updates
            instance = self.nova.servers.get(instance.id)
            status = instance.status
        floating_ip = self.nova.floating_ips.create()
        instance.add_floating_ip(floating_ip)
        print "status: %s" % status
        
    def destroy(self, name):
        print "Deleting instance " + name
        try:
            server = self.nova.servers.find(name=name)
            server.delete()
        except exception.NotFound:
            print "Instance of name " + name + " not found"

    def iplist(self):
        for instance in self.nova.floating_ips.list():
            print str(instance.instance_id) + " has floating ip " + str(instance.ip)

def main():
    conn = NovaAPITest()
    conn.create("test")
    conn.iplist()
    # conn.destroy("test")

if __name__ == "__main__":
    main()

