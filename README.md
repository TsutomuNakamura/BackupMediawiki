# BackupMediawiki
This is a script to backup your Mediawiki that is constructed by MySQL or Maria DB.

# Requirement
* python3
* MySQL or MariaDB (Required mysqldump)
* Linux (This script is tested on Linux of distro Fedora22 and Fedora23)

# Setting
Open and edit default.yaml for your environment.
Each meaning of parameters is explained in config file.

# How to use this script
Clone this repository on your environment.
``` console
git clone https://github.com/TsutomuNakamura/BackupMediawiki.git
```

Change current working directory and edit ./conf/default.yaml file as needed.
``` console
cd BackupMediawiki
vim ./conf/default.yaml
```

Run BackupMediawiki.py.
``` console
./BackupMediawiki.py
```

After finished it, you'll find backup files are located in "mediawiki_backup_dir" and "mysqldump_dir" that assigned in default.yaml.

``` console
ls /var/mediawiki-backup/wiki/files/mediawiki-backup*
ls /var/mediawiki-backup/wiki/db/mysql-dump*
```

# Restoreing
If you got backups with default settings on Fedora, the restoring process will like below.
``` console
cp /var/mediawiki-backup/wiki/db/mysql-dump.YYYYMMDDhhmmss.tar.gz .
tar -zxf /var/mediawiki-backup/wiki/db/mysql-dump.YYYYMMDDhhmmss.tar.gz
mysql YOUR_WIKI_DB_NAME < mysql-dump.YYYYMMDDhhmmss

cp /var/mediawiki-backup/wiki/files/mediawiki-backup.YYYYMMDDhhmmss.tar.gz .
tar -zxf mediawiki-backup.YYYYMMDDhhmmss.tar.gz
cd mediawiki-backup.YYYYMMDDhhmmss
rm -rf /var/www/wiki/images
cp -r images /var/www/wiki/
chown -R apache:apache /var/www/wiki/images
rm -rf /var/www/wiki/mw-config
cp -r mw-config /var/www/wiki/
cp LocalSettings.php /var/www/wiki/
```
