#!/bin/bash

apt-get remove --purge -y landscape-client
rm -f /etc/update-motd.d/51-cloudguest
cat > $(find /usr/lib -name landscapelink.py) <<'EOF'

from twisted.internet.defer import succeed

class LandscapeLink(object):
    def register(self, sysinfo):
        self._sysinfo = sysinfo
    def run(self):
        self._sysinfo.add_footnote(
            "This is a Puppet Master server (built with Packer.io)\n")
        return succeed(None)

EOF