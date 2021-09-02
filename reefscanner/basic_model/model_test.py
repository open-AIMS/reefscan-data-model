from reefscanner.basic_model.basic_model import BasicModel
from reefscanner.basic_model.progress_no_queue import ProgressNoQueue
from reefscanner.basic_model.progress_queue import ProgressQueue

basic_model = BasicModel()
basic_model.data_folder = "C:/aims/reef-scanner"

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
basic_model.read_from_files(progress_queue)


