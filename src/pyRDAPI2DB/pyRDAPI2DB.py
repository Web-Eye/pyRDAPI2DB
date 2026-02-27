# -*- coding: utf-8 -*-
# Copyright 2026 WebEye
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import os

import sys

__VERSION__ = '1.0.0'
__VERSIONSTRING__ = f'pyRDAPI2DB Version {__VERSION__}'

from libs.common.tools import GetConfigFile, ReadConfig
from libs.core.databaseCore import databaseCore
from libs.core.realdebritCore import realdebritCore


def LoadConfig():
    configFile = GetConfigFile()
    return ReadConfig(configFile)

def isValidConfig(config):
    if config is None:
        return False

    _database = config.get('database')
    if _database is None:
        return False

    if not _database.get('host'):
        return False

    _port = _database.get('port')
    if _port is None or _port == 0:
        return False

    if not _database.get('user'):
        return False

    if not _database.get('password'):
        return False

    if not _database.get('database'):
        return False

    _rd = config.get('realdebrit')
    if _rd is None:
        return False

    if not _rd.get('token'):
        return False

    return True

def main():
    parser = argparse.ArgumentParser(
        description='runner',
        epilog="That's all folks"
    )

    parser.add_argument('-v', '--version',
                        action='store_true')

    parser.add_argument('--verbose',
                        action='store_true')

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit()

    if args.version:
        print(__VERSIONSTRING__)
        sys.exit()

    config = LoadConfig()
    if not isValidConfig(config):
        print('invalid config')
        sys.exit()

    db = databaseCore(config['database'])
    if not db.check_database():
        print('unable to check database')
        sys.exit()

    api = realdebritCore(config['realdebrit']['token'])
    hostsStatus = api.getHostsStatus()
    if not hostsStatus:
        print('unable to get hosts status')
        sys.exit()

    hostsRegEx = api.getHostsRegEx()
    if not hostsRegEx:
        print('unable to get hosts regex')
        sys.exit()

    up_hosts = {
        k: v
        for k, v in hostsStatus.items()
        if v.get("status") == "up"
    }

    if not up_hosts or len(up_hosts) == 0:
        sys.exit()

    for key, value in up_hosts.items():
        prefix = key.split(".", 1)[0]

        value["regex"] = [
            item for item in hostsRegEx
            if prefix in item
        ]

    db.setrealdebritHosts(up_hosts)

if __name__ == '__main__':
    main()