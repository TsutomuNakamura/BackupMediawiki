import os
import tarfile

class BackupMediawikiFiles:

    config                          = None

    mediawiki_backup_file           = None

    wikidir                         = None
    mediawiki_backup_dir            = None
    mediawiki_backup_file_prefix    = None
    mediawiki_compression           = None

    def __init__(self, config, mediawiki_backup_file):

        self.config                     = config

        self.mediawiki_backup_file      = mediawiki_backup_file

        self.wikidir                    = config['wikidir']
        self.mediawiki_backup_dir       = config['mediawiki_backup_dir']
        self.mediawiki_backup_file_prefix    = config['mediawiki_backup_file_prefix']
        self.mediawiki_compression      = config['mediawiki_compression']

        if self.mediawiki_compression == "gz":
            self.mediawiki_backup_extension = ".tar.gz"
        elif self.mediawiki_compression == "bz2":
            self.mediawiki_backup_extension = ".tar.bz2"
        else:
            self.mediawiki_backup_extension = ".tar"


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

if __name__ == "__main__":
    import yaml

    with open("../conf/default.yaml", 'r') as f:
        config = yaml.load(f.read())
        bkobj = BackupMediawikiFiles(config)
        bkobj.execute()



