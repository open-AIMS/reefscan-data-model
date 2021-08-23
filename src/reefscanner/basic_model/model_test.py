from reefscanner.basic_model.basic_model import BasicModel
from reefscanner.basic_model.set_progress_status_basic import set_progress_status_basic

basic_model = BasicModel()
basic_model.data_folder = "C:/aims/reef-scanner"
basic_model.read_from_files(set_progress_status_basic)

print (basic_model.sites_data_array)
print (basic_model.surveys_data_array)
