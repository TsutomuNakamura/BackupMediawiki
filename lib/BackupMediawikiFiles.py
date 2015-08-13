import os
import tarfile

from lib.Backup import Backup

class BackupMediawikiFiles(Backup):

    def __init__(self, config, mediawiki_backup_file):

        self.config                         = config

        self.mediawiki_backup_file          = mediawiki_backup_file

        self.wikidir                        = config['wikidir']
        self.mediawiki_backup_dir           = config['mediawiki_backup_dir']
        self.mediawiki_backup_file_prefix   = config['mediawiki_backup_file_prefix']
        self.mediawiki_backup_generation    = config['mediawiki_backup_generation']

        self.mediawiki_compression          = Backup.mediawiki_backup_compression

    def execute(self):
        """
        Backuping mediawiki files
        """
        # Creating backup dir and dump file name
        if not os.path.exists(self.mediawiki_backup_dir):
            print("Creating directory -> " + self.mediawiki_backup_dir)
            os.makedirs(self.mediawiki_backup_dir)

        print("Backup mediawiki files from "
            + self.wikidir + " to " + self.mediawiki_backup_file)
        with tarfile.open(
            self.mediawiki_backup_file, "w:" + self.mediawiki_compression) as tar:

            # Throws exception if archiving is failed
            tar.add(self.wikidir, arcname=os.path.basename(self.wikidir))
        print("Backuping mediawiki files to " + self.mediawiki_backup_file)

        # Remove out dated backup files
        self.remove_out_dated(
            self.mediawiki_backup_dir
            , self.mediawiki_backup_file_prefix + "*", self.mediawiki_backup_generation)

