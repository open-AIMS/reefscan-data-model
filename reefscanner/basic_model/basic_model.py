import logging
from datetime import datetime
import datetime

import shortuuid
import os

from reefscanner.basic_model.progress_queue import ProgressQueue
from reefscanner.basic_model.reader_writer import read_survey_data, read_site_data
from reefscanner.basic_model.json_utils import read_json_file
from reefscanner.basic_model.json_utils import write_json_file

logger = logging.getLogger(__name__)

class BasicModel(object):
    def __init__(self):
        self.data_folder = ""
        self.trip = {}
        self.surveys_data_array = []
        self.sites_data_array = []
        self.projects = []
        self.default_project = ""
        self.default_operator = ""

    def set_data_folder(self, data_folder):
        if os.path.isdir(data_folder):
            self.data_folder = data_folder
            # self.read_from_files()

    def read_from_files(self, progress_queue: ProgressQueue):
        logger.info("start read from files")
        start = datetime.datetime.now()

        progress_queue.set_progress_label("Reading trip data")
        self.read_trip()
        progress_queue.set_progress_label("Reading project data")
        self.read_projects()

        self.read_surveys(progress_queue)
        self.read_sites()
        # finish = datetime.datetime.now()
        # delta = finish - start
        # print("time taken")
        # print(delta)

    def read_surveys(self, progress_queue: ProgressQueue):
        logger.info("start read surveys")

        self.surveys_data_array = []
        try:
            progress_queue.set_progress_label("Reading survey data")
            read_survey_data(self.data_folder, self.trip,  self.default_project,
                             self.default_operator, self.surveys_data_array, progress_queue)
        except Exception as e:
            self.surveys_data_array = []
            print(str(e))
        logger.info("finish read surveys")

    def read_projects(self):
        self.projects = read_json_file(f"{self.data_folder}/projects.json")
        self.default_project = self.projects[0]["id"]

    def read_sites(self):
        self.sites_data_array = []
        try:
            read_site_data(self.data_folder, self.sites_data_array)
        except Exception as e:
            self.sites_data_array = []
            print(e)

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

