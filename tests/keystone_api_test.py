import keystoneclient.v2_0.client as ksclient
from credentials import get_keystone_creds

print "Getting credentials"
creds = get_keystone_creds()

print "Connecting to keystone client"
keystone = ksclient.Client(**creds)

print "Getting auth token"
print keystone.auth_token
