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

import mariadb
import json

from .databaseHelper import databaseHelper
from .datalayer.dl_settings import DL_settings


class databaseCore:

    CURRENT_DB_VERSION = 1

    def __init__(self, config):
        self._config = config
        if not self.create_database():
            raise Exception('database creation failed')
        self._pool = databaseHelper.getConnectionPool(config)

    def check_database(self):
        if self.update_database():
            return True

        return False

    def create_database(self):

        retValue = True

        DB_NAME = self._config['database']
        con = databaseHelper.getMasterConnection(self._config)

        try:
            if not databaseHelper.database_exists(con, DB_NAME):
                retValue = databaseHelper.create_database(con, DB_NAME)

            return retValue

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False

        finally:
            con.close()

    def update_database(self):
        con = self._pool.get_connection()
        try:
            dbVersion = self.get_database_version(con)

            while dbVersion < databaseCore.CURRENT_DB_VERSION:
                dbVersion = self._update_database(con, dbVersion)

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False

        finally:
            con.close()

        return True

    def get_database_version(self, con):
        if not databaseHelper.tableExists(con, self._config['database'], 'settings'):
            return 0

        retValue = DL_settings.getSetting(con, 'database_version')
        if retValue is not None:
            return int(retValue)

        return 0

    @staticmethod
    def _update_database(con, dbVersion):

        if dbVersion == 0:

            statement = 'CREATE TABLE IF NOT EXISTS settings (' \
                        '   setting_id INT NOT NULL AUTO_INCREMENT,' \
                        '   name VARCHAR(100),' \
                        '   value MEDIUMTEXT,' \
                        '   PRIMARY KEY (setting_id)' \
                        ');'

            databaseHelper.executeNonQuery(con, statement)

            dbVersion = 1
            DL_settings.setSetting(con, 'database_version', str(dbVersion))

        return dbVersion

    def setrealdebritHosts(self, hosts):
        con = self._pool.get_connection()
        try:
            DL_settings.setSetting(con, 'realdebrit_hosts', json.dumps(hosts))

        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return False

        finally:
            con.close()

        return True