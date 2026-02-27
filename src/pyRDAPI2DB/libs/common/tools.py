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

import sys
import os

import json

def GetConfigFile():
    if sys.platform == "linux" or sys.platform == "linux2":
        return '/etc/pyRDAPI2DB.config'

    elif sys.platform == "darwin":
        # MAC OS X
        return None

    elif sys.platform == "win32":
        return 'C:\\python\\etc\\pyRDAPI2DB.config'

    return None

def ReadConfig(filename):
    if os.path.isfile(filename):
        with open(filename) as json_data_file:
            return json.load(json_data_file)

    return None