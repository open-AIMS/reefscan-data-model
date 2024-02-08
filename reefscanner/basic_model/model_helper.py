import datetime
import os
import logging
from pytz import utc

from reefscanner.basic_model import model_utils
from reefscanner.basic_model.basic_model import BasicModel
from reefscanner.basic_model.reader_writer import save_survey
logger = logging.getLogger(__name__)


def check_model(model):
    names = set()
    for folder in model.surveys_data.keys():
        survey = model.surveys_data[folder]
        friendly_name = survey.friendly_name
        if friendly_name is not None and friendly_name != "":
            if friendly_name in names:
                raise Exception(f"Duplicate Name {friendly_name}")
            names.add(friendly_name)


def rename_folders(model: BasicModel, local_tz):
    primary_folder = model.data_folder
    backup_folder = model.backup_folder
    names = set()
    for folder in model.surveys_data.keys():
        survey = model.surveys_data[folder]

        friendly_name = survey.friendly_name
        if friendly_name is None:
            friendly_name = ""
        else:
            friendly_name = f"-{friendly_name}"

        site = survey.site
        if site is None:
            site = ""
        else:
            site = f"-{site}"

        id = survey.id
        new_folder = f"{id}{site}{friendly_name}"

        old_primary_survey_folder = survey.folder

        try:
            start_date = survey.start_date
            naive_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
            utc_date = utc.localize(naive_date)
            local_date = utc_date.astimezone(local_tz)
            date_name = datetime.datetime.strftime(local_date, "%Y-%m-%d")
            primary_date_folder = f"{primary_folder}/{date_name}"
            print(f"os.makedirs({primary_date_folder}, exist_ok=True)")
            os.makedirs(primary_date_folder, exist_ok=True)
            if backup_folder is not None:
                backup_date_folder = f"{backup_folder}/{date_name}"
                print(f"os.makedirs({backup_date_folder}, exist_ok=True)")
                os.makedirs(backup_date_folder, exist_ok=True)

            new_relative_survey_folder = f"{date_name}/{new_folder}"
        except:
            new_relative_survey_folder = new_folder

        new_primary_survey_folder = f"{primary_folder}/{new_relative_survey_folder}"
        rename_folder(old_primary_survey_folder, new_primary_survey_folder)

        enhanced_folder = model_utils.replace_last(old_primary_survey_folder, "/reefscan/", "/reefscan_enhanced/")
        enhanced_folder_new = model_utils.replace_last(new_primary_survey_folder, "/reefscan/", "/reefscan_enhanced/")
        rename_folder(enhanced_folder, enhanced_folder_new)

        cache_folder = model_utils.replace_last(old_primary_survey_folder, "/reefscan/", "/reefscan_cache/")
        cache_folder_new = model_utils.replace_last(new_primary_survey_folder, "/reefscan/", "/reefscan_cache/")
        rename_folder(cache_folder, cache_folder_new)

        eod_folder = model_utils.replace_last(old_primary_survey_folder, "/reefscan/", "/reefscan_eod_cots/")
        eod_folder_new = model_utils.replace_last(new_primary_survey_folder, "/reefscan/", "/reefscan_eod_cots/")
        rename_folder(eod_folder, eod_folder_new)

        thumbnails_folder = model_utils.replace_last(old_primary_survey_folder, "/reefscan/", "/reefscan_thumbnails/")
        thumbnails_folder_new = model_utils.replace_last(new_primary_survey_folder, "/reefscan/", "/reefscan_thumbnails/")
        rename_folder(thumbnails_folder, thumbnails_folder_new)

        inference_folder = model_utils.replace_last(old_primary_survey_folder, "/reefscan/", "/reefscan_inference/")
        inference_folder_new = model_utils.replace_last(new_primary_survey_folder, "/reefscan/", "/reefscan_inference/")
        rename_folder(inference_folder, inference_folder_new)

        if backup_folder is not None:
            old_backup_survey_folder = old_primary_survey_folder.replace(primary_folder, backup_folder)
            new_backup_survey_folder = f"{backup_folder}/{new_relative_survey_folder}"
            rename_folder(old_backup_survey_folder, new_backup_survey_folder)


def rename_folder(old_folder, new_folder):
    if os.path.exists(old_folder):
        if old_folder != new_folder:
            dir = os.path.dirname(new_folder)
            os.makedirs(dir, exist_ok=True)
            print(f"os.rename({old_folder}, {new_folder})")
            os.rename(old_folder, new_folder)
