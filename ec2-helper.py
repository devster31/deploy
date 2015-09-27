from boto import ec2
"""
From https://github.com/mikery/fabric-ec2, the directory structure is different
this file should be __init__.py inside a folder with the name of the package

Sample Usage:

    from fabric.api import run, sudo, env
    from fabric_ec2 import EC2TagManager

    def configure_roles(environment):
        ""Set up the Fabric env.roledefs, using the correct roles for the given environment""
        tags = EC2TagManager(AWS_KEY, AWS_SECRET,
            regions=['eu-west-1'],
            common_tags={'production': 'true'})

        roles = {}
        for role in ['web', 'db']:
            roles[role] = tags.get_instances(role=role)

        return roles

    env.roledefs = configure_roles()

    @roles('web')
    def restart_web():
        sudo('/etc/init.d/nginx restart')

    @roles('db')
    def restart_db():
        sudo('/etc/init.d/postgresql restart')

    def hostname():
        run('hostname')

    $ fab restart_db
    $ fab restart_web
    $ fab hostname --roles web
"""


class EC2TagManager:
    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, regions=None, common_tags=None):
        """
        This class helps find instances with a particular set of tags.
        If access key/secret are not given, they must be available as environment
        variables so boto can access them.
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.common_tags = common_tags if common_tags else {}
        # todo get full region list
        self.regions = regions if regions else ['us-east-1']
        # Open connections to ec2 regions
        self.conn = {}
        for region in self.regions:
            self.conn[region] = ec2.connect_to_region(region,
                                                      aws_access_key_id=self.aws_access_key_id,
                                                      aws_secret_access_key=self.aws_secret_access_key)

    def _build_tag_filter(self, tags):
        """
        Convert a dict in to a tag filter.
        Given a dict {'key': 'val'}, return {'tag:key': 'val'}.
        """
        tag_filter = {}
        for k, v in tags.iteritems():
            tag_filter['tag:%s' % k] = v
        return tag_filter

    def get_instances(self, instance_attr='public_dns_name', only_running=True, **kwargs):
        """
        Return instances that match the given tags.
        Keyword arguments:
        instance_attr -- attribute of instance(s) to return (default public_dns_name)
        Additional arguments are used to generate tag filter e.g. "get_instances(role='test')
        """
        if not instance_attr:
            raise ValueError('instance_attr cannot be None or empty' % instance_attr)

        tags = self.common_tags
        for k, v in kwargs.copy().iteritems():
            tags[k] = v
            kwargs.pop(k)

        tag_filter = self._build_tag_filter(tags)

        hosts = []
        for region in self.regions:
            reservations = self.conn[region].get_all_instances(None, tag_filter)
            for res in reservations:
                for instance in res.instances:
                    if only_running and instance.state != 'running':
                        continue

                    instance_value = getattr(instance, instance_attr)
                    if instance_value:
                        # Terminated/stopped instances will not have a public_dns_name
                        hosts.append(instance_value)
                    else:
                        raise ValueError('%s is not an attribute of instance' % instance_attr)
        return hosts
def _get_public_dns(region, key, value ="*"):
    public_dns   = []
    connection   = _create_connection(region)
    reservations = connection.get_all_instances(filters = {key : value})
    for reservation in reservations:
        for instance in reservation.instances:
            print "Instance", instance.public_dns_name
            public_dns.append(str(instance.public_dns_name))
    return public_dns