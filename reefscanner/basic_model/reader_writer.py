import datetime
import glob
import logging
import os

from reefscanner.archive_stats.archive_stats import ArchiveStats
from reefscanner.archive_stats.archive_survey_stats import ArchiveSurveyStats
from reefscanner.basic_model.exif_utils import get_exif_data
from reefscanner.basic_model.json_utils import write_json_file, read_json_file
from reefscanner.basic_model.progress_queue import ProgressQueue
from reefscanner.basic_model.samba.file_ops_factory import get_file_ops

logger = logging.getLogger(__name__)


def save_survey(survey, primary_folder, backup_folder):
    survey_to_save = survey.copy()
    json_folder = survey_to_save.pop('json_folder')
    image_folder = survey_to_save.pop('image_folder')
    # survey_to_save.pop("id")
    # survey_to_save.pop("start_lat")
    # survey_to_save.pop("start_lon")
    # survey_to_save.pop("finish_lat")
    # survey_to_save.pop("finish_lon")
    survey_to_save.pop("samba")
    write_json_file(json_folder, 'survey.json', survey_to_save)
    if backup_folder is not None:
        backup_json_folder = json_folder.replace(primary_folder, backup_folder)
        write_json_file(backup_json_folder, 'survey.json', survey_to_save)



def dict_has(dict, column):
    if column not in dict:
        return False

    if dict[column] is None:
        return False

    if dict[column] == "":
        return False

    return True

# search folder and all it's sub folders for surveys. We know it's a survey if the folder has has "survey.json"
# Or maybe any folder with photos in it we should also include
def find_surveys_local_disk(base_folder, file_ops):
    survey_image_folders = []
    for root, dirs, files in os.walk(base_folder):
        for dir in dirs:
            full_dir = f"{root}/{dir}".replace("\\", "/")
            survey_json = f"{full_dir}/survey.json"
            if file_ops.exists(survey_json):
                survey_image_folders.append(full_dir)
            else:
                photos = glob.iglob(f"{full_dir}/*.jpg")
                if any(photos):
                    survey_image_folders.append(full_dir)

    return survey_image_folders


# find all direct subfolders of the base folder except the archive folder
def find_surveys_camera(base_folder, file_ops):
    survey_image_folders = []

    for folder in file_ops.listdir(base_folder):
        if folder != "archive":
            survey_image_folders.append(f"{base_folder}/{folder}")
    return survey_image_folders


def read_survey_data(base_image_folder, json_folder,
                     backup_folder,
                     progress_queue: ProgressQueue, samba, slow_network):

    file_ops = get_file_ops(samba)
    if base_image_folder is None:
        return {}

    data = {}
    if not file_ops.isdir(base_image_folder):
        return []
    else:
        if samba:
            survey_image_folders =find_surveys_camera(base_image_folder, file_ops)
        else:
            survey_image_folders = find_surveys_local_disk(base_image_folder, file_ops)

    progress_queue.set_progress_max(len(survey_image_folders) + 1)
    for full_survey_image_path in survey_image_folders:
        if samba:
            full_survey_json_path = find_json_folder(os.path.basename(full_survey_image_path), json_folder)
        else:
            full_survey_json_path = full_survey_image_path
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
                survey = {"reef": "", "site": ""
                          }

            if samba or slow_network:
                has_photos = True
            else:
                has_photos = get_stats_from_photos(file_ops, full_survey_image_path, survey)

            survey["json_folder"] = full_survey_json_path
            survey["image_folder"] = full_survey_image_path
            survey["samba"] = samba
            if "id" not in survey:
                survey["id"] = os.path.basename(full_survey_image_path)
                save_survey(survey, json_folder, backup_folder)
            if has_photos:
                data[survey["id"]] = survey
            progress_queue.set_progress_value()
    return data


def find_json_folder(survey_id, json_folder):
    for root, dirs, files in os.walk(json_folder):
        for dir in dirs:
            full_dir = f"{root}/{dir}".replace("\\", "/")
            survey_json_path = f"{full_dir}/survey.json"
            if os.path.exists(survey_json_path):
                survey = read_json_file(survey_json_path)
                if "id" in survey and survey["id"] == survey_id:
                    return f"{root}/{dir}"

    return json_folder + "/" + survey_id


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
            survey["photos"] = count_photos
            last_photo_index = len(photos) - 1
            photo_index = 0
            while (survey["start_lat"] is None or survey["start_lat"] == "") and photo_index < last_photo_index:
                first_photo = f'{full_path}/{photos[photo_index]}'
                start_exif = get_exif_data(first_photo, False)
                survey["start_date"] = start_exif["date_taken"]
                survey["start_lat"] = start_exif["latitude"]
                survey["start_lon"] = start_exif["longitude"]
                photo_index += 1

            photo_index = last_photo_index
            while (survey["finish_lat"] is None or survey["finish_lat"] == "") and photo_index > 0:
                last_photo = f'{full_path}/{photos[photo_index]}'
                finish_exif = get_exif_data(last_photo, False)
                survey["finish_date"] = finish_exif["date_taken"]
                survey["finish_lat"] = finish_exif["latitude"]
                survey["finish_lon"] = finish_exif["longitude"]
                photo_index -= 1
    except Exception as e:
        logger.warning("Error getting metadata for folder " + full_path, e)

    return count_photos > 0


