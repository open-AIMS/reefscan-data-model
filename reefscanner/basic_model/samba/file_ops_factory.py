from reefscanner.basic_model.samba.samba_file_ops import SambaFileOps
from reefscanner.basic_model.samba.os_file_ops import OsFileOps
def get_file_ops(samba):
    if samba:
        return SambaFileOps()
    else:
        return OsFileOps()