ckupMediawiki
This is a script to backup your Mediawiki that is constructed by MySQL or Maria DB.

# Requirement
python3
MySQL or MariaDB (Required mysqldump)
Linux (This script is tested on Linux of distro Fedora22)

# Setting
Open and edit default.yaml for your environment.
Each meaning of parameters is explained in config file.

# How to use this script
Clone this repository on your environment.
```
git clone https://github.com/TsutomuNakamura/BackupMediawiki.git
```

Change current working directory and edit ./conf/default.yaml file as needed.
```
cd BackupMediawiki
vim ./conf/default.yaml
```

Execute BackupMediawiki.py.
```
./BackupMediawiki.py
```



