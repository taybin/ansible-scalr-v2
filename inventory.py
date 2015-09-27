#!/usr/bin/env python

import os
import datetime
import urllib
import base64
import hmac
import hashlib
import argparse
# pip install xmltodict
import xmltodict
# pip install configparser
import configparser

try:
    import json
except ImportError:
    import simplejson as json


class ScalrInventory(object):

    def __init__(self):

        self.farms = {}
        self.inventory = {}
        self.read_cli_args()

        # 1. Get our Configuration
        self.get_configuration()

        # 2. Get our Farms
        self.farms = self.get_farms()

        # 3. Fill Farm Information
        self.farms = self.get_farm_detail(self.farms)

        # 4. Convert to Ansible Inventory
        self.inventory = self.convert_to_inventory(self.farms)

        if self.args.list:
            print json.dumps(self.inventory)

    def get_farms(self):

        farms = {}

        # FarmList and Parse XML Response
        scalr_dict = self.convert_to_dict(self.call_api('FarmsList'))

        farm_list = scalr_dict['FarmsListResponse']['FarmSet']['Item']

        # Extract the ID and Name
        for farm in farm_list:
            farms[farm['Name']] = {}
            farms[farm['Name']] = {
                "ID": farm['ID'],
                "Status": farm['Status']
            }

        return farms

    def get_farm_detail(self, farms):

        # FarmDetails and Parse XML Response
        for farm in farms:

            farm_detail = {}
            farms[farm]['roles'] = {}

            scalr_dict = self.convert_to_dict(self.call_api('FarmGetDetails',
                                                            {'FarmID': farms[farm]['ID']}))

            farm_detail = scalr_dict['FarmGetDetailsResponse']['FarmRoleSet']['Item']

            # Single role does not present as an array, check
            # for array and handle.
            if isinstance(farm_detail, list):
                for roles in farm_detail:
                    farms[farm]['roles'][roles['Name']] = {}
                    farms[farm]['roles'][roles['Name']]['servers'] = []

                    if isinstance(roles['ServerSet'], dict):
                        server_info = roles['ServerSet']['Item']

                        farms[farm]['roles'][roles['Name']]['servers'] = self.parse_server_list(server_info)

            else:
                farms[farm]['roles'][farm_detail['Name']] = {}
                farms[farm]['roles'][farm_detail['Name']]['servers'] = []

                if isinstance(farm_detail['ServerSet'], dict):
                    server_info = farm_detail['ServerSet']['Item']

                    farms[farm]['roles'][farm_detail['Name']]['servers'] = self.parse_server_list(server_info)

        return farms

    def get_configuration(self):

        # Parse Configuration File
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + '/' + 'config.ini')

        default_config = config['DEFAULT']

        self.SCALR_API_KEY = default_config['SCALR_API_KEY']
        self.SCALR_SECRET_KEY = default_config['SCALR_SECRET_KEY']
        self.API_URL = default_config['API_URL']
        self.API_VERSION = default_config['API_VERSION']
        self.API_AUTH_VERSION = default_config['API_AUTH_VERSION']

    def convert_to_dict(self, xml):

        # Return JSON/DICT
        return xmltodict.parse(xml)

    def parse_server_list(self, servers):

        # Parse Server List in Roles
        server_list = []

        # Single server does not present as an array, check
        # for array and handle.
        if isinstance(servers, list):
            for server in servers:
                server_list.append(server['PrivateIP'])
        else:
            server_list.append(servers['PrivateIP'])

        return server_list

    def convert_to_inventory(self, farms):

        inventory = {}

        # Parse farms and convert to inventory
        for farm in farms:
            inventory[farm] = {}
            inventory[farm]['vars'] = {'Status': farms[farm]['Status'], 'ID': farms[farm]['ID']}
            inventory[farm]['children'] = []

            for role in farms[farm]['roles']:
                inventory[farm]['children'].append(role)

                inventory[role] = {}
                inventory[role]['hosts'] = []

                for server in farms[farm]['roles'][role]['servers']:
                    inventory[role]['hosts'].append(server)

        # End result is farm -> role as children

        return inventory

    def call_api(self, API_ACTION, ADDITIONAL_PARAMS={}):

        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Build PARAMS & Join /w Additional
        params = {
            "Action": API_ACTION,
            "Version": self.API_VERSION,
            "AuthVersion": self.API_AUTH_VERSION,
            "Timestamp": timestamp,
            "KeyID": self.SCALR_API_KEY,
            "Signature":  base64.b64encode(hmac.new(self.SCALR_SECRET_KEY,
                                                    ":".join([API_ACTION, self.SCALR_API_KEY, timestamp]),
                                                    hashlib.sha256).digest()),
        }

        params.update(ADDITIONAL_PARAMS)

        # Call API
        urlparams = urllib.urlencode(params)
        req = urllib.urlopen(self.API_URL, urlparams)

        return req.read()

    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        self.args = parser.parse_args()


# Run Scalr Inventory
ScalrInventory()
