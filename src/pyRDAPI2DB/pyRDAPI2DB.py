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
import sys
import re
from typing import Iterable, List

__VERSION__ = '1.0.1'
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


def extract_domains_from_pattern(pattern):
    domains = re.findall(r'([a-zA-Z0-9\-]+\\\.[a-zA-Z]{2,})', pattern)
    return [d.replace(r'\.', '.') for d in domains]

def normalize_api_patterns(api_patterns: Iterable[str]) -> List[str]:
    normalized = []

    for p in api_patterns:
        if not p or not isinstance(p, str):
            continue

        if p.startswith("/") and p.endswith("/"):
            p = p[1:-1]

        p = p.replace("\\/", "/")
        p = p.strip()

        try:
            re.compile(p)
        except re.error:
            continue

        normalized.append(p)

    return normalized

def match_patterns(expressions, compiled):
    return [
        p
        for p, rx in compiled
        if any(rx.search(expr) for expr in expressions)
    ]

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

    hostsRegEx = normalize_api_patterns(hostsRegEx)

    up_hosts = {
        k: v
        for k, v in hostsStatus.items()
        if v.get("status") == "up"
    }

    if not up_hosts or len(up_hosts) == 0:
        sys.exit()

    for pattern in hostsRegEx:
        domains = extract_domains_from_pattern(pattern)

        for domain in domains:
            if domain in up_hosts:
                up_hosts[domain].setdefault("regex", []).append(pattern)

    compiled = [(p, re.compile(p)) for p in hostsRegEx]

    expDict = {
        "docs.google.com": [
            "http://docs.google.com/file/5/",
            "http://docs.google.com/open/"
        ],
        "hitfile.net": [
            "http://hitfile.net/0000000/"
        ],
        "katfile.com": [
            "http://katfile.com/000000000000/"
        ],
        "mega.co.nz": [
            "http://mega.co.nz/0/",
            "http://mega.nz/0/"
        ],
        "rapidgator.net": [
            "http://rapidgator.net/file/00000000000000000000000000000000/",
            "http://rapidgator.net/file/0000000/"
        ],
        "send.cm": [
            "http://send.cm/000000000000/",
            "http://send.cm/d/000000000000/"
        ],
        "turbobit.net": [
            "http://turbobit.net/download/free/0/",
            "http://turbobit.net/000000000000.html/",
            "http://turbobit.net/000000000000/0/",
            "http://turbo.to/download/free/0/",
            "http://turbo.to/000000000000.html/",
            "http://turbobif.com/download/free/0/",
            "http://turbobif.com/000000000000.html/",
            "http://turb.to/download/free/0/",
            "http://turb.to/000000000000.html/"
        ]
    }

    for key, value in up_hosts.items():
        if value.get("regex"):
            continue

        print(key)
        expressions = expDict.get(key)
        if not expressions:
            continue

        value["regex"] = match_patterns(expressions, compiled)

    db.setrealdebritHosts(up_hosts)



if __name__ == '__main__':
    main()
