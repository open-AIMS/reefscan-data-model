import csv
import datetime
import glob
import logging
import os
import re
import tempfile
from time import process_time

from reefscanner.archive_stats.archive_stats import ArchiveStats
from reefscanner.archive_stats.archive_survey_stats import ArchiveSurveyStats
from reefscanner.basic_model.exif_utils import get_exif_data
from reefscanner.basic_model.json_utils import write_json_file, read_json_file
from reefscanner.basic_model.progress_queue import ProgressQueue
from reefscanner.basic_model.samba.file_ops_factory import get_file_ops
from reefscanner.basic_model.samba.samba_file_ops import SambaFileOps
from reefscanner.basic_model.survey import Survey

logger = logging.getLogger(__name__)


def save_survey(survey: Survey, primary_folder, backup_folder, samba):
    survey_to_save = survey.to_json()
    folder = survey_to_save.pop('folder')
    samba = survey_to_save.pop('samba')
    if samba:
        with tempfile.TemporaryDirectory() as temp_folder:
            write_json_file(temp_folder, 'survey.json', survey_to_save)
            ops = SambaFileOps()
            ops.copyfile(f"{temp_folder}\\survey.json", f"{folder}\\survey.json")
    else:
        write_json_file(folder, 'survey.json', survey_to_save)
    if backup_folder is not None:
        write_json_file(folder.replace(primary_folder, backup_folder), 'survey.json', survey_to_save)



def dict_has(dict, column):
    if column not in dict:
        return False

    if dict[column] is None:
        return False

    if dict[column] == "":
        return False

    return True

# search folder and all it's sub folders for surveys. We know it's a survey if the folder has has "survey.json"
# or if it has subfolders such as cam_1
# Or maybe any folder with photos in it we should also include (except cam_1, cam_2 etc)
def find_surveys_local_disk(base_folder, file_ops):
    survey_image_folders = []
    for root, dirs, files in os.walk(base_folder):
        for dir in dirs:
            # skip camera directories (cam_1, cam_2 etc)
            if re.search("^cam_[0-9]$", dir):
                break
            full_dir = f"{root}/{dir}".replace("\\", "/")
            survey_json = f"{full_dir}/survey.json"
            if file_ops.exists(survey_json):
                survey_image_folders.append(full_dir)
            elif file_ops.isdir(f"{full_dir}/cam_1"):
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


def read_survey_data(base_folder,
                     backup_folder,
                     progress_queue: ProgressQueue, samba, slow_network, message, archive=False):

    progress_queue.set_progress_label("Counting Files")
    logger.info(f"message Counting Files {process_time()}")

    file_ops = get_file_ops(samba)
    if base_folder is None:
        return {}

    data = {}
    if not file_ops.isdir(base_folder):
        return {}
    else:
        if samba:
            survey_folders =find_surveys_camera(base_folder, file_ops)
        else:
            survey_folders = find_surveys_local_disk(base_folder, file_ops)

    progress_queue.set_progress_max(len(survey_folders) + 1)
    progress_queue.set_progress_label(message)
    for full_survey_path in survey_folders:
        if file_ops.isdir(full_survey_path):
            survey_file = f'{full_survey_path}/survey.json'

            survey = read_survey_file(survey_file, samba)
            # multi camera system will have folders of the form cam_1, cam_2 for images
            # old format has photos in the survey folder
            survey.camera_dirs = {}
            cam_num =1
            while True:
                cam_dir = f"{full_survey_path}/cam_{cam_num}"
                if file_ops.isdir(cam_dir):
                    survey.camera_dirs[cam_num] = cam_dir
                    cam_num+=1
                else:
                    break

            if not survey.camera_dirs:
                survey.camera_dirs[1] = full_survey_path

            full_stats = not (samba or slow_network)
            if archive:
                has_photos = True
            else:
                has_photos = get_stats_from_photos(file_ops, survey.camera_dirs, survey, full_stats)

            survey.folder = full_survey_path
            survey.samba = samba

            if survey.id is None:
                survey.id = os.path.basename(full_survey_path)
                if not samba:
                    save_survey(survey, base_folder, backup_folder, samba)
            if has_photos:
                data[survey.id] = survey
            progress_queue.set_progress_value()
    return data


def read_survey_file(survey_file, samba: bool):
    try:
        ops = get_file_ops(samba)
        if ops.exists(survey_file):
            if samba:
                with tempfile.TemporaryDirectory() as folder:
                    fname = f"{folder}\\survey.json"
                    ops.copyfile(survey_file, fname)
                    survey_json = read_json_file(fname)
            else:
                survey_json = read_json_file(survey_file)
        else:
            survey_json = {}
        survey = Survey(survey_json)
        return survey
    except Exception as e:
        logger.warning(f"erros reading survey {survey_file}: {e}")
        return Survey({})


# def find_json_folder(survey_id, json_folder):
#     for root, dirs, files in os.walk(json_folder):
#         for dir in dirs:
#             full_dir = f"{root}/{dir}".replace("\\", "/")
#             survey_json_path = f"{full_dir}/survey.json"
#             if os.path.exists(survey_json_path):
#                 survey = read_json_file(survey_json_path)
#                 if "id" in survey and survey["id"] == survey_id:
#                     return f"{root}/{dir}"
#
#     return json_folder + "/" + survey_id


def get_stats_from_photos(file_ops, camera_paths, survey, full):
    count_photos = 0
    dir_num = 0
    counting_finished = False
    for full_path in camera_paths.values():
        # count the photos
        if count_photos is not None:
            files = file_ops.listjpegsfast(full_path)
            photos = [name for name in files if name.lower().endswith(".jpg") or name.lower().endswith(".jpeg")]
            photos.sort()
            count_photos += len(photos)
            if not full and counting_finished:
                survey.photos = ">1000"
            else:
                survey.photos = count_photos
                counting_finished = True

        # get start and end dates, depths and positions only do this for the first camera
        if dir_num == 0:
            try:
                if full and count_photos > 0:
                    last_photo_index = len(photos) - 1
                    photo_index = 0
                    photo_name = "2000"
                    while (survey.start_lat is None or abs(survey.start_lat) < 0.01 or photo_name < "2020") and photo_index < last_photo_index:
                        try:
                            first_photo = f'{full_path}/{photos[photo_index]}'
                            start_exif = get_exif_data(first_photo, False)
                            survey.start_date = start_exif["date_taken"]
                            survey.start_lat = start_exif["latitude"]
                            survey.start_lon = start_exif["longitude"]
                            survey.start_depth = start_exif["altitude"]
                            photo_name = photos[photo_index]
                        except:
                            pass
                        photo_index += 1

                    photo_index = last_photo_index
                    while (survey.finish_lat is None or abs(survey.finish_lat) < 0.01) and photo_index > 0 :
                        try:
                            last_photo = f'{full_path}/{photos[photo_index]}'
                            finish_exif = get_exif_data(last_photo, False)
                            survey.finish_date = finish_exif["date_taken"]
                            survey.finish_lat = finish_exif["latitude"]
                            survey.finish_lon = finish_exif["longitude"]
                            survey.finish_depth = finish_exif["altitude"]
                        except:
                            pass
                        photo_index -= 1

            except Exception as e:
                logger.warning("Error getting metadata for folder " + full_path, e)
        dir_num+=1
    return count_photos > 0
