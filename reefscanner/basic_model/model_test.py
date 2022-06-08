import logging

from reefscanner.basic_model.basic_model import BasicModel
from reefscanner.basic_model.progress_no_queue import ProgressNoQueue
from reefscanner.basic_model.progress_queue import ProgressQueue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
basic_model.set_data_folders("c:/temp/dum", "")
basic_model.slow_network = False
basic_model.read_from_files(progress_queue, camera_connected=False)
# basic_model.new_method()

logger.info("done")

logger.info(basic_model.surveys_data)

basic_model.export()



