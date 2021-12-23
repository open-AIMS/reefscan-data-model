import datetime
import logging
import os

from reefscanner.basic_model.exif_utils import get_exif_data
from reefscanner.basic_model.json_utils import write_json_file, read_json_file
from reefscanner.basic_model.progress_queue import ProgressQueue
from reefscanner.basic_model.samba.file_ops_factory import get_file_ops

logger = logging.getLogger(__name__)


def save_survey(survey):
    survey_to_save = survey.copy()
    json_folder = survey_to_save.pop('json_folder')
    image_folder = survey_to_save.pop('image_folder')
    survey_to_save.pop("id")
    # survey_to_save.pop("start_lat")
    # survey_to_save.pop("start_lon")
    # survey_to_save.pop("finish_lat")
    # survey_to_save.pop("finish_lon")
    survey_to_save.pop("samba")
    write_json_file(json_folder, 'survey.json', survey_to_save)


def read_survey_data(base_image_folder, json_folder, trip, default_project, default_operator, progress_queue: ProgressQueue, samba):
    file_ops = get_file_ops(samba)
    if base_image_folder is None:
        return {}

    data = {}
    progress_queue.set_progress_label("Reading surveys")
    image_folder = f'{base_image_folder}/images'
    if file_ops.isdir(image_folder):
        survey_image_folders = file_ops.listdir(image_folder)
    else:
        survey_image_folders = []

    progress_queue.set_progress_max(len(survey_image_folders))
    for survey_image_folder in survey_image_folders:
        full_survey_image_path = f'{image_folder}/{survey_image_folder}'
        full_survey_json_path = f'{json_folder}/images/{survey_image_folder}'
        if file_ops.isdir(full_survey_image_path):
            survey_file = f'{full_survey_json_path}/survey.json'
            if os.path.exists(survey_file):
                survey = read_json_file(survey_file)
            else:
                survey = None

            if survey is None:
                survey = {"site": "",
                          "project": default_project, "operator": default_operator,
                          "vessel": trip["vessel"], "trip": trip["uuid"]
                          }

            if samba:
                has_photos = True
            else:
                has_photos = get_stats_from_photos(file_ops, full_survey_image_path, survey)

            survey["id"] = survey_image_folder
            survey["json_folder"] = full_survey_json_path
            survey["image_folder"] = full_survey_image_path
            survey["samba"] = samba
            if has_photos:
                data[survey["id"]] = survey
            progress_queue.set_progress_value()
    return data


def get_stats_from_photos(file_ops, full_path, survey):
    photos = [name for name in file_ops.listdir(full_path) if name.lower().endswith(".jpg")]
    photos.sort()
    count_photos = len(photos)
    if count_photos == 0:
        survey["photos"] = 0
        survey["start_date"] = ""
        survey["start_lat"] = ""
        survey["start_lon"] = ""
        survey["finish_date"] = ""
        survey["finish_lat"] = ""
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

    return count_photos > 0


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

