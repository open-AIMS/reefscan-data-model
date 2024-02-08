


# search s for the last occurence of old and replace with with new
from time import process_time

from smbclient._io import SMBDirectoryIO
from smbprotocol.exceptions import NoSuchFile
from smbprotocol.file_info import FileInformationClass


def replace_last(s: str, old: str, new: str):
    return new.join(s.rsplit(old, 1))

def print_time(msg, start, logger):
    stop = process_time()
    seconds = stop - start
    logger.info(f"{msg} in {seconds} seconds")

def samba_listdir(path, search_pattern="*.jpg", **kwargs):
    """
    Return a list containing the names of the entries in the directory given by path. The list is in arbitrary order,
    and does not include the special entries '.' and '..' even if they are present in the directory.

    :param path: The path to the directory to list.
    :param search_pattern: THe search string to match against the names of directories or files. This pattern can use
        '*' as a wildcard for multiple chars and '?' as a wildcard for a single char. Does not support regex patterns.
    :param kwargs: Common SMB Session arguments for smbclient.
    :return: A list containing the names of the entries in the directory.
    """
    with SMBDirectoryIO(path, mode='r', share_access='r', **kwargs) as dir_fd:
        try:
            raw_filenames = dir_fd.query_directory(search_pattern, FileInformationClass.FILE_NAMES_INFORMATION)
            filenames = []
            i = 0
            for f in raw_filenames:
                if i > 1000:
                    break
                filename = f['file_name'].get_value().decode('utf-16-le')
                if filename not in ['.', '..']:
                    filenames.append(filename)
                    i += 1
            return filenames
        except NoSuchFile:
            return []
