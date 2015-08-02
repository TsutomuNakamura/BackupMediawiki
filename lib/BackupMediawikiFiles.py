import os
import tarfile

class BackupMediawikiFiles:

    wikidir                 = None
    mediawiki_backup_dir    = None
    mediawiki_backup_prefix = None
    mediawiki_compression   = None

    def __init__(self, config):
        self.wikidir                    = config['wikidir']
        self.mediawiki_backup_dir       = config['mediawiki_backup_dir']
        self.mediawiki_backup_prefix    = config['mediawiki_backup_prefix']
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

        with tarfile.open(
                os.path.join(self.mediawiki_backup_dir
                    , self.mediawiki_backup_prefix + self.mediawiki_backup_extension)
                    , "w:" + self.mediawiki_compression) as tar:

            # Throws exception if archiving is failed
            tar.add(self.wikidir, arcname=os.path.basename(self.wikidir))

if __name__ == "__main__":
    import yaml

    with open("../conf/default.yaml", 'r') as f:
        config = yaml.load(f.read())
        bkobj = BackupMediawikiFiles(config)
        bkobj.execute()



