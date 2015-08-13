from subprocess import Popen, PIPE

class Command:

    @staticmethod
    def execute(command):
        """
        Command utility method.
        """

        proc = Popen(command, stdout=PIPE, stderr=PIPE)
        try:
            std_out, std_err = proc.communicate()
        except Alarm as e:
            proc.kill()
            print(str(e))

        return (proc.returncode, std_out, std_err)


    @staticmethod
    def mysqldump(dump_file, user, password, db_name, character_set, timeout_sec=300):
        """
        Mysqldump command utility
        """

        # Create mysqldump command
        command = [
            "mysqldump", "--single-transaction", "--skip-lock-tables"
            , "-u", user
            , "--password=" + password
            , "--default-character-set=" + character_set
            , "--databases", db_name
        ]

        retcode = None
        errout = None

        # Dump DB data and write to the file
        with open(dump_file, 'w') as f:
            proc = Popen(command, stdout=f, stderr=PIPE)

            try:
                dummy, errout = proc.communicate(timeout=timeout_sec)
            except Exception as e:
                proc.kill()
                raise e

            retcode = proc.returncode

        return (retcode, None, errout)

