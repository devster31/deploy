import boto, urllib2
from   boto.ec2 import connect_to_region
from   fabric.api import env, run, cd, settings, sudo
from   fabric.api import parallel
import os
import sys

# from http://abhishek-tiwari.com/hacking/interacting-with-tagged-ec2-instances-using-fabric

REGION   = os.environ.get("AWS_EC2_REGION")
WEB_ROOT = "/var/www"


# Your custom Fabric task here after and run them using,
# fab set_hosts:phpapp,2X,us-west-1 task1 task2 task3

# Fabric task to set env.hosts based on tag key-value pair
def set_hosts(tag = "phpapp", value="*", region=REGION):
    key          = "tag:"+tag
    env.hosts    = _get_public_dns(region, key, value)

# Private method to get public DNS name for instance with given tag key and value pair
def _get_public_dns(region, key, value ="*"):
    public_dns   = []
    connection   = _create_connection(region)
    reservations = connection.get_all_instances(filters = {key : value})
    for reservation in reservations:
        for instance in reservation.instances:
            print "Instance", instance.public_dns_name
            public_dns.append(str(instance.public_dns_name))
    return public_dns

# Private method for getting AWS connection
def _create_connection(region):
    print "Connecting to ", region

    conn = connect_to_region(
        region_name = region, 
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"), 
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
    )

    print "Connection with AWS established"
    return connection