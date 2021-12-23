import smbclient
from smbclient import path


class SambaFileOps:
    def __init__(self):
        smbclient.ClientConfig(username='jetson', password='jetson')

    def listdir(self, dir):
        return smbclient._os.listdir(dir)

    def isdir(self, dir):
        return smbclient.path.isdir(dir)

    def open(self, filename, mode="r"):
        return smbclient.open_file(filename, mode=mode)

    def exists(self, fname):
        return smbclient.path.exists(fname)
