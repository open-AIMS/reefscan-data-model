import logging

from reefscanner.archive_stats.archive_stats import ArchiveStats
from reefscanner.basic_model.basic_model import BasicModel
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
basic_model.set_data_folders("E:/heron_island_tech_2022", r"\\192.168.3.2\images")
# basic_model.set_data_folders("c:/temp/reefscan", r"\\192.168.1.254\images")

basic_model.slow_network = False
basic_model.read_from_files(progress_queue, camera_connected=True)
# basic_model.new_method()

logger.info("done")

logger.info(basic_model.surveys_data)

basic_model.export()

archive_stats = ArchiveStats()

archive_stats.get_archive_stats(basic_model)
print("archive")
print(archive_stats.to_string())



