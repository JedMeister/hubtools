# 
# Copyright (c) 2011 Alon Swartz <alon@turnkeylinux.org>
# 
# This file is part of HubTools.
# 
# HubTools is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
# 
from utils import AttrDict

class Server(AttrDict):
    def __repr__(self):
        return "<Server: %s (%s, %s)>" % (self.name, self.instanceid, self.status)

    def __init__(self, hubobj, response):
        self.hubobj = hubobj
        self._parse_response(response)

    def _parse_response(self, response):
        self.raw = response
        self.instanceid = response['instanceid']
        self.size = response['type']
        self.region = response['region']
        self.ipaddress = response['ipaddress']
        self.status = response['status']
        self.boot_status = response['server']['boot_status']
        self.name = response['server']['name']
        self.label = response['server']['description']
        self.type = 'ebs' if response['ebs_backed'] else 's3'

    def update(self):
        attrs = {'refresh_cache': True}
        r = self.hubobj.api('GET', 'amazon/instance/%s/' % self.instanceid, attrs)
        self._parse_response(r[0])

    def reboot(self):
        r = self.hubobj.api('PUT', 'amazon/instance/%s/reboot/' % self.instanceid)
        self._parse_response(r)

    def destroy(self):
        r = self.hubobj.api('PUT', 'amazon/instance/%s/destroy/' % self.instanceid)
        self._parse_response(r)

    def stop(self):
        r = self.hubobj.api('PUT', 'amazon/instance/%s/stop/' % self.instanceid)
        self._parse_response(r)

    def start(self):
        r = self.hubobj.api('PUT', 'amazon/instance/%s/start/' % self.instanceid)
        self._parse_response(r)

    def unregister(self):
        self.hubobj.api('DELETE', 'amazon/instance/%s/unregister/' % self.instanceid)
  
class Servers(object):
    def __init__(self, hubobj):
        self.hubobj = hubobj

    def get(self, instanceid=None, refresh_cache=False):
        attrs = {'refresh_cache': refresh_cache}
        if instanceid:
            r = self.hubobj.api('GET', 'amazon/instance/%s/' % instanceid, attrs)
        else:
            r = self.hubobj.api('GET', 'amazon/instances/', attrs)

        return map(lambda server: Server(self.hubobj, server), r)

    def launch(self, name, region="us-east-1", size="m1.small", type="s3",
               label="", **kwargs):
        """Launch a new cloud server

        args:

            name        - appliance name (e.g., core)
            region      - region for instance launch (e.g., us-east-1)
            size        - instance size (e.g., m1.small)
            type        - instance type (e.g., s3 or ebs)

        kwargs (optional, * is required depending on appliance):

            root_pass   - root password to set (random if not specified)
            db_pass*    - database password
            app_pass*   - admin password for application
            app_email*  - admin email for application
            app_domain* - domain for application

            fqdn        - fully qualified domain name to associate
                          e.g., www.tklapp.com. | www.example.com.

            backup_id   - automatically restore backup to new cloud server
                          note: backup key cannot be passphrase protected
        """
        attrs = {'region': region, 'size': size ,'type': type, 'label': label}
        attrs.update(kwargs)
        r = self.hubobj.api('POST', 'amazon/launch/%s/' % name, attrs)

        return Server(self.hubobj, r)

