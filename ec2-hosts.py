#!/usr/bin/env python
"""
Dynamic boto inventory for fab deploy
https://github.com/ansible/ansible/blob/devel/contrib/inventory/ec2.ini
https://github.com/ansible/ansible/blob/devel/contrib/inventory/ec2.py
https://gist.github.com/ozkatz/5900450
https://boto.readthedocs.org/en/latest/ec2_tut.html
"""
import os
from boto.ec2 import EC2Connection
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class EC2Hosts(object):

    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

    def __init__(self):
        self.conn = EC2Connection(
            EC2Hosts.aws_access_key_id,
            EC2Hosts.aws_secret_access_key
        )
        self._host_map = None

    def _generate_host_map(self):
        if self._host_map is None:
            self._host_map = {}
            for reservation in self.conn.get_all_instances():
                for instance in reservation.instances:
                    self._host_map[instance.tags.get('Name')] = instance.public_dns_name
        return self._host_map

    def generate_roledef(self, patterns):
        """
        Patterns - a mapping between role name and
        regular expression to match against. Example:
        {
            "db": "swayy-prod-db\d+",
            "web": "swayy-prod-web\d+",
            "worker": "swayy-prod-worker\d+",
            "python": "swayy-prod-(web|worker)\d+",  # Will match all web and worker servers
            "all": "swayy-prod-.*"  # Will match ALL production servers
        }
        """
        roledef = {}
        host_map = self._generate_host_map()
        for role, pattern in patterns.items():
            for name in host_map.keys():
                if re.match(pattern, name):
                    if not role in roledef:
                        roledef[role] = []
                    roledef[role].append(host_map[name])
        return roledef
