import os, sys
import datetime
import subprocess
import tarfile

from lib.Command import Command

class BackupMySQL:

    # DB parameters
    config                  = None
    wg_db_server            = None
    wg_db_name              = None
    wg_db_user              = None
    wg_db_password          = None

    mysqldump_file          = None
    default_character_set   = None

    mysqldump_file_prefix   = None
    mysqldump_dir           = None
    mysqldump_compression   = None

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

        self.mysqldump_file_prefix  = self.config['mysqldump_file_prefix']
        self.mysqldump_dir          = self.config['mysqldump_dir']
        self.mysqldump_compression  = self.config['mysqldump_compression']

        if self.mysqldump_compression == "gz":
            self.mysqldump_extension = ".tar.gz"
        elif self.mysqldump_compression == "bz2":
            self.mysqldump_extension = ".tar.bz2"
        else:
            self.mysqldump_extension = ".tar"


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
            , self.wg_db_password, self.wg_db_name, self.default_character_set)

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
            tar.add(self.mysqldump_file)

        print("Compress mysql data was succeeded (file="
            + self.mysqldump_file + self.mysqldump_extension + ")")

