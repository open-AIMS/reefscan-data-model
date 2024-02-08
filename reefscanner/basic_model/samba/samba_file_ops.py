import smbclient
from smbclient import path, shutil

from reefscanner.basic_model.model_utils import samba_listdir


class SambaFileOps:
    def __init__(self):
        smbclient.ClientConfig(username='jetson', password='jetson')

    def file_size_mb(self, file):
        # return smbclient.path.getsize(file)/1000000
        return smbclient.lstat(file).st_size/1000000

    def listjpegsfast(self, dir):
        return samba_listdir(dir)

    def listdir(self, dir):
        return smbclient._os.listdir(dir)

    def isdir(self, dir):
        return smbclient.path.isdir(dir)

    def open(self, filename, mode="r"):
        return smbclient.open_file(filename, mode=mode)

    def exists(self, fname):
        return smbclient.path.exists(fname)

    def rmdir(self, dir):
        return smbclient.rmdir(dir)

    def remove(self, fname):
        return smbclient.remove(fname)

    def copyfile(self, frm, to):
        return smbclient.shutil.copyfile(frm, to)

    def mkdir(self, dir):
        smbclient.mkdir(dir)

    def move(self, frm, to):
        smbclient.rename(frm, to)