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


def dict_has(dict, column):
    if column not in dict:
        return False

    if dict[column] is None:
        return False

    if dict[column] == "":
        return False

    return True


def read_survey_data(base_image_folder, json_folder, default_vessel, default_observer, default_operator, progress_queue: ProgressQueue, samba, slow_network):
    relative_root_path = ""
    relative_photo_path = ""

    file_ops = get_file_ops(samba)
    if base_image_folder is None:
        return {}

    data = {}
    image_folder = f'{base_image_folder}/{relative_root_path}'
    if file_ops.isdir(image_folder):
        survey_image_folders = file_ops.listdir(image_folder)
    else:
        survey_image_folders = []

    progress_queue.set_progress_max(len(survey_image_folders))
    for survey_image_folder in survey_image_folders:
        full_survey_image_path = f'{image_folder}/{survey_image_folder}/{relative_photo_path}'
        full_survey_json_path = f'{json_folder}/{relative_root_path}/{survey_image_folder}'
        if file_ops.isdir(full_survey_image_path):
            source_survey_file = f'{full_survey_image_path}/survey.json'
            survey_file = f'{full_survey_json_path}/survey.json'
            # there may be a survey.json on the camera but not yet on the computer
            # if so copy it
            if file_ops.exists(source_survey_file) and not os.path.exists(survey_file):
                os.makedirs(full_survey_json_path, exist_ok=True)
                file_ops.copyfile(source_survey_file, survey_file)

            if os.path.exists(survey_file):
                survey = read_json_file(survey_file)
            else:
                survey = None

            if survey is None:
                survey = {"reef": "", "site": "",
                          "operator": default_operator, "observer" : default_observer,
                          "vessel": default_vessel
                          }

            if not dict_has (survey, "operator"):
                survey["operator"] = default_operator

            if not dict_has (survey, "observer"):
                survey["observer"] = default_observer

            if not dict_has (survey, "vessel"):
                survey["vessel"] = default_vessel

            if samba or slow_network:
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
    photos = [name for name in file_ops.listdir(full_path) if name.lower().endswith(".jpg") or name.lower().endswith(".jpeg")]
    photos.sort()
    count_photos = len(photos)
    survey["photos"] = 0
    survey["start_date"] = ""
    survey["start_lat"] = ""
    survey["start_lon"] = ""
    survey["finish_date"] = ""
    survey["finish_lat"] = ""
    survey["finish_lat"] = ""
    survey["finish_lon"] = ""

    try:
        if count_photos > 0:
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
    except Exception as e:
        logger.warning("Error getting metadata for folder " + full_path, e)

    return count_photos > 0


