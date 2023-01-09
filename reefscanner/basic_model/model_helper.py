import datetime
import os
import logging

from pytz import utc

from reefscanner.basic_model.reader_writer import save_survey
logger = logging.getLogger(__name__)

def check_model(model):
    names = set()
    for folder in model.surveys_data.keys():
        survey = model.surveys_data[folder]
        friendly_name = survey["friendly_name"]
        if friendly_name is not None and friendly_name != "":
            if friendly_name in names:
                raise Exception(f"Duplicate Name {friendly_name}")
            names.add(friendly_name)


def rename_folders(model, primary_folder, backup_folder, local_tz):
    names = set()
    for folder in model.surveys_data.keys():
        survey = model.surveys_data[folder]
        if "original_folder" in survey:
            original_folder = survey["original_folder"]
        else:
            original_folder = survey["id"]
            survey["original_folder"] = original_folder
            save_survey(survey, primary_folder, backup_folder)

        try:
            friendly_name = survey["friendly_name"]
        except:
            friendly_name = ""

        if friendly_name != "":
            friendly_name = f"-{friendly_name}"
        site = survey["site"]
        if site != "":
            site = f"-{site}"

        new_folder = f"{original_folder}{site}{friendly_name}"

        id = survey["id"]

        old_primary_survey_folder = survey.pop('json_folder')

        try:
            date_part = id[:15]
            naive_date = datetime.datetime.strptime(date_part, "%Y%m%d_%H%M%S")
            utc_date = utc.localize(naive_date)
            local_date = utc_date.astimezone(local_tz)
            date_name = datetime.datetime.strftime(local_date, "%Y-%m-%d")
            primary_date_folder = old_primary_survey_folder.replace(id, date_name)

            os.makedirs(primary_date_folder, exist_ok=True)

            new_primary_survey_folder = f"{primary_date_folder}/{new_folder}"
        except:
            new_primary_survey_folder = old_primary_survey_folder.replace(id, new_folder)

        # old_backup_survey_folder = old_primary_survey_folder.replace(primary_folder, backup_folder)
        # new_backup_survey_folder = old_backup_survey_folder.replace(id, new_folder)

        # print(f"os.rename({old_primary_survey_folder}, {new_primary_survey_folder})")
        os.rename(old_primary_survey_folder, new_primary_survey_folder)

        # try:
        #     os.rename(old_backup_survey_folder, new_backup_survey_folder)
        # except:
        #     logger.warning(f"Error renaming back up survey {old_backup_survey_folder}")

