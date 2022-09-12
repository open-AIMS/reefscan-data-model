import logging
from datetime import datetime
import datetime
import pandas as pd

import shortuuid
import os

from reefscanner.basic_model.progress_queue import ProgressQueue
from reefscanner.basic_model.reader_writer import read_survey_data
from reefscanner.basic_model.json_utils import read_json_file
from reefscanner.basic_model.json_utils import write_json_file

logger = logging.getLogger(__name__)


class BasicModel(object):
    def __init__(self):
        self.slow_network = True
        self.data_folder = ""
        self.camera_data_folder = ""
        self.trip = {}
        self.surveys_data = {}
        self.camera_surveys = {}
        self.default_observer = ""
        self.default_operator = ""
        self.default_vessel = ""
        self.messages = []
        self.camera_samba = True
        self.local_samba = False

    def set_data_folders(self, data_folder, camera_data_folder):
        if not os.path.isdir(data_folder):
            os.makedirs(data_folder)

        self.data_folder = data_folder
        self.camera_data_folder = camera_data_folder

    def read_from_files(self, progress_queue: ProgressQueue, camera_connected):
        logger.info("start read from files")
        start = datetime.datetime.now()

        progress_queue.reset()
        progress_queue.set_progress_label("Reading data from local file system")
        try:
            self.surveys_data = self.read_surveys(progress_queue, self.data_folder, self.data_folder, self.local_samba,
                                                  self.slow_network)
        except:
            raise Exception("Error can't find local files")

        if camera_connected:
            progress_queue.reset()
            progress_queue.set_progress_label("Reading data from camera")
            try:
                self.camera_surveys = self.read_surveys(progress_queue, self.camera_data_folder, self.data_folder,
                                                        self.camera_samba, False)
            except:
                raise Exception("Error can't find camera. Make sure the computer is connected to the camera via an ethernet cable. You may need to restart the camera.")

        # finish = datetime.datetime.now()
        # delta = finish - start
        # print("time taken")
        # print(delta)

    def read_surveys(self, progress_queue: ProgressQueue, image_folder, json_folder, samba, slow_network):
        logger.info("start read surveys")

        surveys_data = read_survey_data(image_folder, json_folder, default_vessel=self.default_vessel,
                                        default_operator=self.default_operator,
                                        default_observer=self.default_observer,
                                        progress_queue=progress_queue, samba=samba, slow_network=slow_network)
        logger.info("finish read surveys")

        return surveys_data

    def surveys_to_df(self):
        survey_list = []
        for folder in self.surveys_data.keys():
            survey = self.surveys_data[folder]
            if 'sequence_name' in survey:
                survey.pop("sequence_name")
            survey_list.append(survey)

        return pd.DataFrame(survey_list)

    def combined_df(self):
        df = self.surveys_to_df()
        # df = df.drop(
        #     ["samba"], axis=1)
        return df

    def export(self):
        csv_file = self.data_folder + "/surveys.csv"
        print("export to " + csv_file)
        df = self.combined_df()

        df.to_csv(csv_file, index=False)
