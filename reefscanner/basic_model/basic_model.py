import logging
from datetime import datetime
import datetime
import pandas as pd

import shortuuid
import os

from reefscanner.basic_model.progress_queue import ProgressQueue
from reefscanner.basic_model.reader_writer import read_survey_data, read_site_data, read_method_data
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
        self.sites_data_array = []
        self.methods_data_array = []
        self.projects = []
        self.default_project = ""
        self.default_operator = ""
        self.messages = []
        self.camera_samba = True
        self.local_samba = False

    def set_data_folders(self, data_folder, camera_data_folder):
        if not os.path.isdir(data_folder):
            os.makedirs(data_folder)

        self.data_folder = data_folder
        self.camera_data_folder = camera_data_folder

    def read_from_files(self, progress_queue: ProgressQueue):
        logger.info("start read from files")
        start = datetime.datetime.now()

        progress_queue.set_progress_label("Reading trip data")
        self.read_trip()
        progress_queue.set_progress_label("Reading project data")
        self.read_projects()

        progress_queue.set_progress_label("Reading data from local file system")
        try:
            self.surveys_data = self.read_surveys(progress_queue, self.data_folder, self.data_folder, self.local_samba,
                                                  self.slow_network)
        except:
            raise Exception("Error can't find local files")

        progress_queue.set_progress_label("Reading data from camera")
        try:
            self.camera_surveys = self.read_surveys(progress_queue, self.camera_data_folder, self.data_folder,
                                                    self.camera_samba, False)
        except:
            raise Exception("Error can't find camera")
        # self.camera_surveys = self.read_surveys(progress_queue, self.camera_data_folder, self.data_folder, True)
        self.read_sites()
        self.read_methods()
        # finish = datetime.datetime.now()
        # delta = finish - start
        # print("time taken")
        # print(delta)

    def read_surveys(self, progress_queue: ProgressQueue, image_folder, json_folder, samba, slow_network):
        logger.info("start read surveys")

        surveys_data = read_survey_data(image_folder, json_folder, self.trip, self.default_project,
                                        self.default_operator, progress_queue, samba, slow_network)
        logger.info("finish read surveys")

        return surveys_data

    def read_projects(self):
        try:
            self.projects = read_json_file(f"{self.data_folder}/projects.json")
            self.default_project = self.projects[0]["id"]
        except Exception as e:
            logger.warning("No Projects", e)
            self.messages.append("No Projects")
            self.projects = []

    def read_methods(self):
        self.methods_data_array = []
        try:
            read_method_data(f"{self.data_folder}", self.methods_data_array)
        except Exception as e:
            logger.warning("No Methods", e)
            self.messages.append("No Methods")
            self.methods = []

    def new_method(self):
        self.methods_data_array.append({"name": "method_name", "description": "method_description"})

    def read_sites(self):
        self.sites_data_array = []
        try:
            read_site_data(self.data_folder, self.sites_data_array)
        except Exception as e:
            logger.warning("No Sites", e)
            self.messages.append("No Sites")
            self.sites_data_array = []

    def save_trip(self):
        trip = self.trip.copy()
        uuid = trip.pop('uuid')
        folder = trip.pop('folder')
        trip["start_date"] = datetime.date.strftime(self.trip["start_date"], "%Y-%m-%d")
        trip["finish_date"] = datetime.date.strftime(self.trip["finish_date"], "%Y-%m-%d")

        write_json_file(folder, 'trip.json', trip)

    def read_trip(self):
        trips_folder = f'{self.data_folder}/trips'
        if not os.path.isdir(trips_folder):
            os.mkdir(trips_folder)

        trip_folders = os.listdir(trips_folder)
        if len(trip_folders) == 0:
            uuid = shortuuid.uuid()
            os.mkdir(f'{trips_folder}/{uuid}')
        else:
            uuid = trip_folders[0]

        trip_file_name = f'{trips_folder}/{uuid}/trip.json'

        if os.path.exists(trip_file_name):
            self.trip = read_json_file(trip_file_name)
            self.trip["start_date"] = datetime.datetime.strptime(self.trip["start_date"], "%Y-%m-%d").date()
            self.trip["finish_date"] = datetime.datetime.strptime(self.trip["finish_date"], "%Y-%m-%d").date()
            new_trip = False
        else:
            today = datetime.date.today()
            self.trip = {"name": "EDIT THIS TRIP", "start_date": today, "vessel": "",
                         "finish_date": today + datetime.timedelta(days=7)}
            new_trip = True

        self.trip["folder"] = f'{trips_folder}/{uuid}'
        self.trip["uuid"] = uuid

        if new_trip:
            self.save_trip()

    def surveys_to_df(self):
        survey_list = []
        for folder in self.surveys_data.keys():
            survey = self.surveys_data[folder]
            survey_list.append(survey)

        return pd.DataFrame(survey_list)

    def trip_to_df(self):
        return pd.DataFrame([self.trip])

    def methods_to_df(self):
        df = pd.DataFrame(self.methods_data_array)
        return df

    def projects_to_df(self):
        return pd.DataFrame(self.projects)

    def sites_to_df(self):
        return pd.DataFrame(self.sites_data_array)

    def combined_df(self):
        df = self.surveys_to_df()
        trip_df = self.trip_to_df()
        trip_df = trip_df.add_prefix("trip_")
        df = df.merge(trip_df, left_on="trip", right_on="trip_uuid")
        method_df = self.methods_to_df()
        method_df = method_df.add_prefix("method_")
        project_df = self.projects_to_df()
        project_df = project_df.add_prefix("project_")
        site_df = self.sites_to_df()
        site_df = site_df.add_prefix("site_")
        df = df.merge(method_df, left_on="trip_method", right_on="method_uuid", how="left")
        df = df.merge(project_df, left_on="trip_project", right_on="project_id", how="left")
        df = df.merge(site_df, left_on="site", right_on="site_uuid", how="left")

        df = df.drop(
            ["project", "site", "trip", "samba", "trip_method", "trip_project", "trip_uuid", "method_uuid", "project_id",
             "site_uuid", "method_folder", "site_folder"], axis=1)
        return df

    def export(self):
        csv_file = self.data_folder + "/surveys.csv"
        print("export to " + csv_file)
        df = self.combined_df()

        df.to_csv(csv_file, index=False)
