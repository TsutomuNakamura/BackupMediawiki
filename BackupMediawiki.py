#!/usr/bin/python3
import os, sys
import shutil
import re
import datetime
import time
import yaml
import traceback
import glob

from lib.BackupMySQL import BackupMySQL
from lib.BackupMediawikiFiles import BackupMediawikiFiles
from lib.Backup import Backup
from lib.Mail import Mail

class BackupMediawiki:

    # Mediawiki modes
    MODE_NORMAL                 = 0
    MODE_READONLY               = 1

    # Path to LocalSettings file
    backup_local_settings_file  = None

    # Regular expression for getting db parameters.
    reg_wg_db_server            = re.compile("^\$wgDBserver\s*=\s*\"(.*)\";\s*$")
    reg_wg_db_name              = re.compile("^\$wgDBname\s*=\s*\"(.*)\";\s*$")
    reg_wg_db_user              = re.compile("^\$wgDBuser\s*=\s*\"(.*)\";\s*$")
    reg_wg_db_password          = re.compile("^\$wgDBpassword\s*=\s*\"(.*)\";\s*$")
    reg_default_character_set   = re.compile("^\$wgDBTableOptions\s*=\s*\".*DEFAULT CHARSET\s*=\s*([a-z0-9_]+).*\";\s*$")
    reg_wg_readonly             = re.compile("^\$wgReadOnly\s*=\s*[\"'](.*)[\"'];\s*$")

    def __init__(self):

        config_file_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "conf/default.yaml")

        with open(config_file_path, 'r') as f:
            self.config = yaml.load(f.read())

        self.workdir                        = self.config['workdir']
        self.wikidir                        = self.config['wikidir']
        self.local_settings_file            = self.config['local_settings_file']

        self.mysqldump_dir                  = self.config['mysqldump_dir']
        self.mysqldump_file_prefix          = self.config['mysqldump_file_prefix']

        self.mediawiki_backup_dir           = self.config['mediawiki_backup_dir']
        self.mediawiki_backup_file_prefix   = self.config['mediawiki_backup_file_prefix']

        self.define_file_name_retry_num     = self.config['define_file_name_retry_num']

        self.current_local_settings_file    = os.path.join(
                                                    self.wikidir, self.local_settings_file)

        if self.define_file_name_retry_num < 0:
            self.define_file_name_retry_num = 0


    def execute(self):
        try:
            self.backup_resources()
        except Exception:
            # Replace mysqldump password if existed
            stack = re.sub('\-\-password=.*\-\-default\-character\-set='
                    , '--password=?????\', \'--default-charcter-set='
                    , traceback.format_exc()
                    , flags=re.MULTILINE)
            print(stack)

            # Send mail if some error occured
            if 'mail_recipient_address' in self.config:
                mail = Mail(self.config)
                mail.send(
                    os.path.basename(__file__) + " encountered an error\n"
                    , stack)
        finally:
            # Restore LocalSettings if succeeded
            if not self.backup_local_settings_file == None:
                print("Restoreing LocalSettings file")
                shutil.copyfile(
                        self.backup_local_settings_file, self.current_local_settings_file)
                os.remove(self.backup_local_settings_file)


    def backup_resources(self):

        # Creating or clearning work directory
        if not os.path.exists(self.workdir):
            print("Creating directory " + self.workdir)
            os.makedirs(self.workdir)
        else:
            for f in glob.glob(os.path.join(self.workdir, self.local_settings_file) + '*'):
                print("Removing: " + f)
                os.remove(f)

        for retry_count in range(self.define_file_name_retry_num + 1):
            date_suffix = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            self.backup_local_settings_file = os.path.join(
                    self.workdir, self.local_settings_file + "." + date_suffix)

            if os.path.exists(self.backup_local_settings_file):
                last_try_filename = self.backup_local_settings_file
                sleep(1); continue

            self.mysqldump_file = os.path.join(
                    self.mysqldump_dir, self.mysqldump_file_prefix + "." + date_suffix)

            if os.path.exists(self.mysqldump_file):
                last_try_filename = self.mysqldump_file
                sleep(1); continue

            if os.path.exists(self.mysqldump_file + Backup.mediawiki_backup_extension):
                last_try_filename = self.mysqldump_file + Backup.mediawiki_backup_extension
                sleep(1); continue

            # self.mediawiki_backup_file = os.path.join(
            #         self.mediawiki_backup_dir
            #         , self.mediawiki_backup_file_prefix
            #         + "." + date_suffix + Backup.mediawiki_backup_extension)
            self.mediawiki_backup_file = os.path.join(
                    self.mediawiki_backup_dir, self.mediawiki_backup_file_prefix + "." + date_suffix)

            if os.path.exists(self.mediawiki_backup_file):
                last_try_filename = self.mediawiki_backup_file
                sleep(1); continue

            break

        # Check retry count
        if retry_count > self.define_file_name_retry_num:
             raise Exception("Backup is failed. File "
                    + self.backup_local_settings_file + " is already existed.")

        # Backup LocalSettings
        self.backup_local_settings()

        # Change the mode of the mediawiki to read only
        self.change_wiki_mode_readonly(BackupMediawiki.MODE_READONLY)

        # Backup mysql data
        BackupMySQL(
            self.config,
            self.wg_db_server,
            self.wg_db_name,
            self.wg_db_user,
            self.wg_db_password,
            self.mysqldump_file,
            default_character_set=self.default_character_set
        ).execute()

        # Backup mediawiki file data
        BackupMediawikiFiles(
            self.config,
            self.mediawiki_backup_file
        ).execute()


    def backup_local_settings(self):
        """
        Backup LocalSettings.php in workdir.
        """

        retry_count                         = -1
        last_try_filename                   = None

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
                    continue

                match = self.reg_wg_db_name.search(last_line)
                if match:
                    self.wg_db_name = match.group(1)
                    continue

                match = self.reg_wg_db_user.search(last_line)
                if match:
                    self.wg_db_user = match.group(1)
                    continue

                match = self.reg_default_character_set.search(last_line)
                if match:
                    self.default_character_set = match.group(1)
                    continue

                match = self.reg_wg_db_password.search(last_line)
                if match:
                    self.wg_db_password = match.group(1)
                    continue

                match = self.reg_wg_readonly.search(last_line)
                if match:
                    read_only_matched = True
                    continue

        # Check variables
        if self.wg_db_server == None:
            raise Exception("Cannot read the parameter $wgDBserver in " + local_settings_file)
        if self.wg_db_name == None:
            raise Exception("Cannot read the parameter $wgDBname in " + local_settings_file)
        if self.wg_db_user == None:
            raise Exception("Cannot read the parameter $wgDBuser in " + local_settings_file)
        if self.wg_db_password == None:
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

