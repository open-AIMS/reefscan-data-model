import smbclient
from smbclient import path, shutil

from reefscanner.basic_model.model_utils import samba_listdir


class SambaFileOps:
    def __init__(self, username):
        smbclient.ClientConfig(username=username, password=username,
            connection_options = {
                "smb_version": "3.1.1",
                "max_credits": 2048
            }
            )


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
        # create destination folder is it does not exist
        self.fast_smb_copy(frm, to)
        return True

    def mkdir(self, dir):
        smbclient.mkdir(dir)

    def makedirs(self, dir, exist_ok=True):
        smbclient.makedirs(dir, exist_ok=exist_ok)

    def move(self, frm, to):
        smbclient.rename(frm, to)

    def fast_smb_copy(self, src_unc, dst_path, buf_size=4 * 1024 * 1024):
        """
        High-speed file copy from SMB using large buffered reads.
        """
        with smbclient.open_file(src_unc, mode="rb") as fsrc:
            with open(dst_path, "wb") as fdst:
                while True:
                    chunk = fsrc.read(buf_size)
                    if not chunk:
                        break
                    fdst.write(chunk)
