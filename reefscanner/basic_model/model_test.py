import logging
import os

from pytz import timezone

from reefscanner.archive_stats.archive_stats import ArchiveStats
from reefscanner.basic_model.basic_model import BasicModel
from reefscanner.basic_model.model_helper import check_model, rename_folders
from reefscanner.basic_model.progress_no_queue import ProgressNoQueue
from reefscanner.basic_model.progress_queue import ProgressQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger_smb = logging.getLogger('smbprotocol')
logger_smb.setLevel(level=logging.WARNING)
basic_model = BasicModel()

# progress_queue = ProgressQueue()
# basic_model.read_from_files(progress_queue)
#
# print(basic_model.sites_data_array)
# print(basic_model.surveys_data_array)
#
# ok = True
# while ok:
#     try:
#         i = progress_queue.q.get(block=False)
#         print(str(i))
#     except:
#         ok = False

progress_queue = ProgressNoQueue()
# basic_model.set_data_folders("D:/Trip7785_DaviesReef_CoralAUV_ReefScanTesting/ReefScan", "")
# basic_model.set_data_folders("E:/heron_island_tech_2022", r"\\192.168.3.2\images")
primary_data_folder = "D:/reefscan"
backup_data_folder = "F:/reefscan_backup"
basic_model.set_data_folders(primary_data_folder, backup_data_folder, r"\\192.168.3.2\images")

basic_model.slow_network = False
basic_model.read_from_files(progress_queue, camera_connected=True)

logger.info("done")

logger.info(basic_model.surveys_data)

# check_model(basic_model)
rename_folders(model=basic_model, local_tz=timezone("Australia/Brisbane"))
# basic_model.export()

# archive_stats = ArchiveStats()

# archive_stats.get_archive_stats(basic_model)
# print("archive")
# print(archive_stats.to_string())



