import logging
import shutil
from datetime import datetime
import datetime
from time import process_time

import pandas as pd

import shortuuid
import os

from reefscanner.basic_model.progress_queue import ProgressQueue
from reefscanner.basic_model.reader_writer import read_survey_data
from reefscanner.basic_model.json_utils import read_json_file
from reefscanner.basic_model.json_utils import write_json_file
from reefscanner.basic_model.survey import Survey

logger = logging.getLogger(__name__)


class BasicModel(object):
    def __init__(self):
        self.slow_network = True
        self.data_folder = ""
        self.camera_json_folder = ""
        self.camera_data_folder = ""
        self.backup_folder = None
        self.trip = {}
        self.surveys_data = {}
        self.camera_surveys = {}
        self.archived_surveys = {}
        self.messages = []
        self.camera_samba = True
        self.local_samba = False
        self.local_data_loaded = False
        self.camera_data_loaded = False
        self.archived_data_loaded = False

    def set_data_folders(self, data_folder, backup_folder, camera_data_folder):
        if not os.path.isdir(data_folder):
            os.makedirs(data_folder)

        self.data_folder = data_folder
        self.camera_data_folder = camera_data_folder
        self.camera_json_folder = data_folder.replace("/reefscan/", "/reefscan_camera_surveys/")
        self.backup_folder = backup_folder

    def read_from_files(self, progress_queue: ProgressQueue, camera_connected,
                        message="Reading data from local file system", error_message="Error can't find local files"):
        logger.info(f"start read from files {process_time()}")

        start = datetime.datetime.now()

        progress_queue.reset()
        progress_queue.set_progress_label(message)
        try:
            self.surveys_data = self.read_surveys(progress_queue, self.data_folder,
                                                  self.backup_folder,
                                                  self.local_samba,
                                                  self.slow_network,
                                                  message)
            self.local_data_loaded = True

        except:
            raise Exception(error_message)

        if camera_connected:
            self.load_camera_data(progress_queue)

    def load_camera_archive_data(self, progress_queue, message="Reading data from camera",
                                 error_message="Error can't find camera. Make sure the computer is connected to the camera via an ethernet cable. You may need to restart the camera."):
        progress_queue.reset()
        progress_queue.set_progress_label(message)
        try:
            self.archived_surveys = self.read_surveys(progress_queue, f"{self.camera_data_folder}/archive",
                                                    None,
                                                    self.camera_samba, False, message=message, archive=True)
            self.archived_data_loaded = True

        except:
            raise Exception(
                error_message)

    def load_camera_data(self, progress_queue, message="Reading data from camera",
                         error_message="Error can't find camera. Make sure the computer is connected to the camera via an ethernet cable. You may need to restart the camera."):
        progress_queue.reset()
        progress_queue.set_progress_label(message)
        logger.info(f"message {message} {process_time()}")

        try:
            self.camera_surveys = self.read_surveys(progress_queue, self.camera_data_folder,
                                                    None,
                                                    self.camera_samba, False, message)
            self.camera_data_loaded = True
        except:
            raise Exception(
                error_message)

    def read_surveys(self, progress_queue: ProgressQueue, image_folder,
                     backup_folder, samba, slow_network, message, archive=False):
        logger.info(f"start read surveys {process_time()}")

        surveys_data = read_survey_data(image_folder, backup_folder,
                                        progress_queue=progress_queue, samba=samba, slow_network=slow_network, message=message, archive=archive)
        logger.info("finish read surveys")

        return surveys_data

    def surveys_to_df(self):
        survey_list = []
        for id in self.surveys_data.keys():
            survey: Survey = self.surveys_data[id]
            survey_list.append(survey.to_json())

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
        if self.backup_folder is not None:
            backup_csv_file = self.backup_folder + "/surveys.csv"
            shutil.copy2(csv_file, backup_csv_file)

