
class BackupMediawikiFiles:

    mediawiki_files_backup_dir = None

    def __init__(self, config):
        self.mediawiki_files_backup_dir = config['mediawiki_files_backup_dir']

    def execute(self):
        pass

