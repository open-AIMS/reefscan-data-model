import os
import shutil
from os import path


class OsFileOps:
    def listdir(self, dir):
        return os.listdir(dir)

    def isdir(self, dir):
        return os.path.isdir(dir)

    def exists(self, fname):
        return os.path.exists(fname)

    def open(self, filename, mode="r"):
        return open(filename, mode=mode)

    def rmdir(self, dir):
        return os.rmdir(dir)

    def remove(self, fname):
        return os.remove(fname)

    def copyfile(self, frm, to):
        return shutil.copyfile(frm, to)
