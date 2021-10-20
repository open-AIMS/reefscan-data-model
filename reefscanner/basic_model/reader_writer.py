import datetime
import logging
import os

from reefscanner.basic_model.exif_utils import get_exif_data
from reefscanner.basic_model.json_utils import write_json_file, read_json_file
from reefscanner.basic_model.progress_queue import ProgressQueue

logger = logging.getLogger(__name__)

def save_survey(survey):
    survey_to_save = survey.copy()
    folder = survey_to_save.pop('folder')
    survey_to_save.pop("id")
    survey_to_save.pop("start_lat")
    survey_to_save.pop("start_lon")
    survey_to_save.pop("finish_lat")
    survey_to_save.pop("finish_lon")
    write_json_file(folder, 'survey.json', survey_to_save)


def read_survey_data(data_folder, trip, default_project, default_operator, data_array, progress_queue: ProgressQueue):
    progress_queue.set_progress_label("Reading surveys")
    surveys_folder = f'{data_folder}/images'
    survey_folders = os.listdir(surveys_folder)
    progress_queue.set_progress_max(len(survey_folders))
    for survey_folder in survey_folders:
        full_path = f'{surveys_folder}/{survey_folder}'
        if os.path.isdir(full_path):
            survey_file = f'{full_path}/survey.json'
            if os.path.exists(survey_file):
                survey = read_json_file(survey_file)
            else:
                survey = None

            start = datetime.datetime.now()
            photos = [name for name in os.listdir(full_path) if name.lower().endswith(".jpg")]
            finish = datetime.datetime.now()
            photos.sort()
            count_photos = len(photos)
            # delta = finish - start
            # print("time taken")
            # print(delta)
            # print(count_photos)
            if survey is None:
                survey = {"site": "",
                          "project": default_project, "operator": default_operator,
                          "vessel": trip["vessel"], "trip": trip["uuid"]
                          }

            if count_photos == 0:
                survey["photos"] = 0
                survey["start_date"] = ""
                survey["start_lat"] = ""
                survey["start_lon"] = ""
                survey["finish_date"] = ""
                survey["finish_lat"] = ""
                survey["finish_lon"] = ""
            else:
                first_photo = f'{full_path}/{photos[0]}'
                start_exif = get_exif_data(first_photo, False)
                last_photo = f'{full_path}/{photos[len(photos) - 1]}'
                finish_exif = get_exif_data(last_photo, False)
                survey["photos"] = count_photos
                survey["start_date"] = start_exif["date_taken"]
                survey["start_lat"] = start_exif["latitude"]
                survey["start_lon"] = start_exif["longitude"]
                survey["finish_date"] = finish_exif["date_taken"]
                survey["finish_lat"] = finish_exif["latitude"]
                survey["finish_lon"] = finish_exif["longitude"]

            survey["id"] = survey_folder
            survey["folder"] = full_path
            data_array.append(survey)
            progress_queue.set_progress_value()


def save_site(site, all_sites):
    # check for duplicate names
    for other_site in all_sites:
        site_name_ = site["name"]
        site_uuid_ = site["uuid"]
        if (site_name_ == other_site["name"]) and (site_uuid_ != other_site["uuid"]):
            raise Exception(f"Duplicate Site Name {site_name_}")


    site_to_save = site.copy()
    site_to_save.pop('uuid')
    folder = site_to_save.pop('folder')
    write_json_file(folder, 'site.json', site_to_save)


def read_site_data(datafolder, data_array):
    # self.datafolder = datafolder
    sites_folder = f'{datafolder}/sites'
    site_folders = os.listdir(sites_folder)
    for site_folder in site_folders:
        site_full_path = f'{sites_folder}/{site_folder}'
        if os.path.isdir(site_full_path):
            site_file = f'{site_full_path}/site.json'
            site = read_json_file(site_file)
            site["folder"] = site_full_path
            site["uuid"] = site_folder
            data_array.append(site)

