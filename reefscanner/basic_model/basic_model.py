from datetime import datetime
import datetime

import shortuuid
import os

from reefscanner.basic_model.reader_writer import read_survey_data, read_site_data
from reefscanner.basic_model.json_utils import read_json_file
from reefscanner.basic_model.json_utils import write_json_file


class BasicModel(object):
    data_folder = ""
    trip = {}
    surveys_data_array = []
    sites_data_array = []
    projects = []
    default_project = ""
    default_operator = ""

    def set_data_folder(self, data_folder):
        if os.path.isdir(data_folder):
            self.data_folder = data_folder
            # self.read_from_files()

    def read_from_files(self, set_progress_status):
        start = datetime.datetime.now()

        # self.progress_dialog.setLabelText("Reading trip data")
        self.read_trip()
        # self.progress_dialog.setLabelText("Reading project data")
        self.read_projects()

        self.read_surveys(set_progress_status)
        self.read_sites()
        # finish = datetime.datetime.now()
        # delta = finish - start
        # print("time taken")
        # print(delta)

    def read_surveys(self, set_progress_status):
        self.surveys_data_array = []
        try:
            # self.progress_dialog.setLabelText("Reading survey data")
            read_survey_data(self.data_folder, self.trip, set_progress_status, self.default_project,
                             self.default_operator, self.surveys_data_array)
        except Exception as e:
            self.surveys_data_array = []
            print(str(e))

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

