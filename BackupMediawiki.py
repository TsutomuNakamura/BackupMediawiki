#!/usr/bin/python3
import os, sys
import shutil
import re
import datetime
import time
import yaml

from lib.BackupMySQL import BackupMySQL

class BackupMediawiki:

    MODE_NORMAL     = 0
    MODE_READONLY   = 1

    # Config instance
    config = None

    # Config parameters
    workdir = None
    wikidir = None
    local_settings_file = None
    backup_local_settings_file = None
    current_local_settings_file = None
    backup_max_retry_num = None

    # DB parameters
    wg_db_server            = None
    wg_db_name              = None
    wg_db_user              = None
    wg_db_password          = None
    default_character_set   = None

    # Regular expression for getting db parameters.
    reg_wg_db_server            = re.compile("^\$wgDBserver\s*=\s*\"(.*)\";\s*$")
    reg_wg_db_name              = re.compile("^\$wgDBname\s*=\s*\"(.*)\";\s*$")
    reg_wg_db_user              = re.compile("^\$wgDBuser\s*=\s*\"(.*)\";\s*$")
    reg_wg_db_password          = re.compile("^\$wgDBpassword\s*=\s*\"(.*)\";\s*$")
    reg_default_character_set   = re.compile("^\$wgDBTableOptions\s*=\s*\".*DEFAULT CHARSET\s*=\s*([a-z0-9_]+).*\";\s*$")

    reg_wg_readonly     = re.compile("^\$wgReadOnly\s*=\s*[\"'](.*)[\"'];\s*$")

    def __init__(self):
        # TODO:
        with open("./conf/default.yaml", 'r') as f:
            self.config = yaml.load(f.read())

        self.workdir                = self.config['workdir']
        self.wikidir                = self.config['wikidir']
        self.local_settings_file    = self.config['local_settings_file']
        self.db_dump_dir            = self.config['db_dump_dir']
        self.files_dump_dir         = self.config['files_dump_dir']

        self.backup_max_retry_num   = self.config['backup_max_retry_num']


    def execute(self):

        # Creating work dir
        if not os.path.exists(self.workdir):
            print("Creating directory " + self.workdir)
            os.makedirs(self.workdir)

        print("workdir: " + self.config['workdir'])

        # Backup LocalSettings
        self.backup_local_settings()

        # Change the mode of the mediawiki to read only
        self.change_wiki_mode_readonly(BackupMediawiki.MODE_READONLY)

        BackupMySQL(
            self.config,
            self.wg_db_server,
            self.wg_db_name,
            self.wg_db_user,
            self.wg_db_password,
            self.db_dump_dir,
            default_character_set=self.default_character_set
        ).execute()

        # BackupMySQL(
        #     self.wg_db_server,
        #     self.wg_db_name,
        #     self.wg_db_user,
        #     self.wg_db_password,
        #     None
        # ).execute()


        # Backup mediawiki file data

    def backup_local_settings(self):
        """
        Backup LocalSettings.php in workdir.
        """

        for retry_count in range(5):
            date_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            self.current_local_settings_file = os.path.join(
                    self.wikidir, self.local_settings_file)
            self.backup_local_settings_file = os.path.join(
                    self.workdir, self.local_settings_file + "." + date_suffix)

            if not os.path.exists(self.backup_local_settings_file):
                break
            elif retry_count == self.backup_max_try_num:  # Retry over
                raise Exception("Backup " + self.current_local_settings_file
                        + " is failed. File " + self.backup_local_settings_file + " is already existed.")

            time.sleep(1)

        # Copy LocalSettings.php to workdir. Throw Exception when copy failed
        shutil.copyfile(self.current_local_settings_file, self.backup_local_settings_file)

        print("Backup current setting from "
            + self.current_local_settings_file
            + " to " + self.backup_local_settings_file)

    def change_wiki_mode_readonly(self, mode):
        """
        Change the mediawiki mode readonly during backup.
        And get the parameters.
        """

        local_settings_file = \
                os.path.join(self.wikidir, self.local_settings_file)

        read_only_matched = False
        last_line = None

        with open(local_settings_file) as f:
            for last_line in f.readlines():
                match = self.reg_wg_db_server.search(last_line)
                if match:
                    self.wg_db_server = match.group(1)
                    # print("Server: " + self.wg_db_server)
                    continue

                match = self.reg_wg_db_name.search(last_line)
                if match:
                    self.wg_db_name = match.group(1)
                    # print("DB Name: " + self.wg_db_name)
                    continue

                match = self.reg_wg_db_user.search(last_line)
                if match:
                    self.wg_db_user = match.group(1)
                    # print("DB User: " + self.wg_db_user)
                    continue

                match = self.reg_default_character_set.search(last_line)
                if match:
                    self.default_character_set = match.group(1)
                    print("Default character set: " + self.default_character_set)
                    continue

                match = self.reg_wg_db_password.search(last_line)
                if match:
                    self.wg_db_password = match.group(1)
                    continue

                match = self.reg_wg_readonly.search(last_line)
                if match:
                    # print("Read Only Message: " + match.group(1))
                    read_only_matched = True
                    continue

        # Check variables
        if self.wg_db_server == None:
            raise Exception("Cannot read the parameter $wgDBserver in " + local_settings_file)
        elif self.wg_db_name == None:
            raise Exception("Cannot read the parameter $wgDBname in " + local_settings_file)
        elif self.wg_db_user == None:
            raise Exception("Cannot read the parameter $wgDBuser in " + local_settings_file)
        elif self.wg_db_password == None:
            raise Exception("Cannot read the parameter $wgDBpassword in " + local_settings_file)

        if read_only_matched == False:
            # Add readonly parameter to mediawiki
            with open(local_settings_file, 'a') as f:
                if not "\n" in last_line:
                    f.write("\n")

                f.write("$wgReadOnly = 'Dumping Database, Access will be restored shortly';\n")
                print("Change mediawiki mode to readonly.")


if __name__ == "__main__":
    instance = BackupMediawiki()
    instance.execute()

