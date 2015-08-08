from abc import ABCMeta, abstractmethod
import glob
import os

class Backup:
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self):
        pass

    def remove_out_dated(self, search_dir, file_glob, generation_num):
        """
        Remove out dated backup files
        """
        files = glob.glob(os.path.join(search_dir, file_glob))

        files_length = len(files)
        if files_length > generation_num:
            files.sort(key=os.path.getmtime)

            for index in range(files_length - generation_num):
                # Delete out dated file
                print("Remove out dated file: " + files[index])
                os.remove(files[index])

