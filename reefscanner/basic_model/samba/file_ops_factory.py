from reefscanner.basic_model.samba.samba_file_ops import SambaFileOps
from reefscanner.basic_model.samba.os_file_ops import OsFileOps
def get_file_ops(samba, username=None):
    if samba:
        if username is None:
            raise Exception("username cannot be None for samba")
        return SambaFileOps(username)
    else:
        return OsFileOps()