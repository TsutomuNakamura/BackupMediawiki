import os
import tarfile

class BackupMediawikiFiles:

    wikidir                     = None
    mediawiki_files_backup_dir  = None

    def __init__(self, config):
        self.wikidir                    = config['wikidir']
        self.mediawiki_files_backup_dir = config['mediawiki_files_backup_dir']

        print("self.mediawiki_files_backup_dir: " + self.mediawiki_files_backup_dir)

    def execute(self):
        with tarfile.open("/var/tmp/mediawiki.tar.gz", "w:gz") as tar:
            tar.add("/var/www/html/wiki/", arcname=os.path.basename("/var/www/html/wiki/"))

        pass

if __name__ == "__main__":
    import yaml

    with open("../conf/default.yaml", 'r') as f:
        config = yaml.load(f.read())
        bkobj = BackupMediawikiFiles(config)
        bkobj.execute()



