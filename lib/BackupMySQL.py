import os, sys
import datetime
import subprocess

from lib.Command import Command

class BackupMySQL:

    # DB parameters
    wg_db_server            = None
    wg_db_name              = None
    wg_db_user              = None
    wg_db_password          = None
    backup_dir              = None
    default_character_set   = None

    dump_file_prefix      = None
    dump_file_name        = None
    backup_max_try_num      = None

    dump_file             = None

    def __init__(self, config, wg_db_server, wg_db_name
            , wg_db_user, wg_db_password
            , default_character_set="binary"):
        self.config                 = config
        self.wg_db_server           = wg_db_server
        self.wg_db_name             = wg_db_name
        self.wg_db_user             = wg_db_user
        self.wg_db_password         = wg_db_password
        self.default_character_set  = default_character_set

        self.dump_file_prefix       = self.config['mysql_dump_file_prefix']
        self.backup_dir             = self.config['db_dump_dir']
        self.backup_max_try_num     = self.config['backup_max_retry_num']

    def execute(self):
        """
        Backup mysql data.
        """

        # Creating backup dir and dump file name
        if not os.path.exists(self.backup_dir):
            print("Creating directory -> " + self.backup_dir)
            os.makedirs(self.backup_dir)

        for retry_count in range(self.backup_max_try_num):
            date_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            self.dump_file = os.path.join(
                    self.backup_dir, self.dump_file_prefix + "." + date_suffix)

            if not os.path.exists(self.dump_file):
                break
            elif retry_count == self.backup_max_try_num:  # Retry over
                raise Exception("Dump mysql data to " + self.dump_file + " is failed")

            time.sleep(1)

        # Dump DB data with mysqldump
        print("Mysql dump -> " + self.dump_file)
        retcode, dummy, errout = Command.mysqldump(
            self.dump_file, self.wg_db_user
            , self.wg_db_password, self.wg_db_name, self.default_character_set)

        if not retcode == 0:
            raise Exception("Failed to backup DB with mysqldump"
                + "[dump_file=" + self.dump_file + ","
                + "user=" + self.wg_db_user + ","
                + "password=*,"
                + "db_name=" + self.wg_db_name + ","
                + "character_set" + self.default_character_set + "]")





