import os, sys
import datetime
import subprocess
import tarfile

from lib.Command import Command
from lib.Backup  import Backup

class BackupMySQL(Backup):

    def __init__(
            self, config, wg_db_server, wg_db_name
            , wg_db_user, wg_db_password
            , mysqldump_file
            , default_character_set="binary"):

        self.config                 = config

        self.wg_db_server           = wg_db_server
        self.wg_db_name             = wg_db_name
        self.wg_db_user             = wg_db_user
        self.wg_db_password         = wg_db_password

        self.mysqldump_file         = mysqldump_file
        self.default_character_set  = default_character_set

        self.mysqldump_file_prefix      = self.config['mysqldump_file_prefix']
        self.mysqldump_dir              = self.config['mysqldump_dir']
        self.mysqldump_generation_num   = self.config['mysqldump_generation_num']
        self.mysqldump_timeout_sec      = self.config['mysqldump_timeout_sec']

        self.mysqldump_compression      = Backup.mediawiki_backup_compression
        self.mysqldump_extension        = Backup.mediawiki_backup_extension

    def execute(self):
        """
        Backup mysql data.
        """

        # Creating backup dir and dump file name
        if not os.path.exists(self.mysqldump_dir):
            print("Creating directory -> " + self.mysqldump_dir)
            os.makedirs(self.mysqldump_dir)

        # Dump DB data with mysqldump
        print("Dumping mysql date (file=" + self.mysqldump_file + ")")
        retcode, dummy, errout = Command.mysqldump(
            self.mysqldump_file,   self.wg_db_user
            , self.wg_db_password, self.wg_db_name
            , self.default_character_set, self.mysqldump_timeout_sec)

        if not retcode == 0:
            raise Exception("Failed to backup DB with mysqldump"
                + "[mysqldump_file=" + self.mysqldump_file + ","
                + "user=" + self.wg_db_user + ","
                + "password=*,"
                + "db_name=" + self.wg_db_name + ","
                + "character_set" + self.default_character_set + ","
                + "retcode=" + retcode + "]")

        print("Dump mysql data was succeeded(file=" + self.mysqldump_file + ")")

        # Compress mysqldump file
        print("Compressing mysql data")
        with tarfile.open(
                self.mysqldump_file + self.mysqldump_extension
                    , "w:" + self.mysqldump_compression) as tar:
            tar.add(self.mysqldump_file, arcname=os.path.basename(self.mysqldump_file))

        os.remove(self.mysqldump_file)

        print("Compress mysql data was succeeded (file="
            + self.mysqldump_file + self.mysqldump_extension + ")")

        self.remove_out_dated(
            self.mysqldump_dir, self.mysqldump_file_prefix + "*", self.mysqldump_generation_num)

