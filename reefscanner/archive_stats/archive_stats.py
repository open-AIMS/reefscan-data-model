import fnmatch
from array import array

import smbclient

from reefscanner.archive_stats.archive_survey_stats import ArchiveSurveyStats
from reefscanner.basic_model.samba.file_ops_factory import get_file_ops


class ArchiveStats:
    def __init__(self):
        self.surveys = []
        self.space = None
        self.counting = True
        self.cancelled = False

    def available_size(self):
        if self.space is None:
            return 0
        else:
            return self.space.actual_available_size


    def to_string(self):
        if self.cancelled:
            return "cancelled"
        s = ""
        if self.surveys is not None and self.surveys:
            still_counting = False
            errors = False
            for survey in self.surveys:
                s = survey.to_string() + "\n" + s
                if survey.status == "counting":
                    still_counting = True
                if survey.status == "different":
                    errors = True

            if still_counting:
                s = "counting ...\n\n" + s
            else:
                if errors:
                    s = "Archive does not match saved surveys. There has been an error.\n\n" + s
                else:
                    s = "Archive matches saved surveys. It is OK do delete the archive.\n\n" + s

        if self.space is not None:
            s = f"total disk space: {round(self.space.total_size):,}mb\n\n" + s
            s = f"available disk space: {round(self.space.actual_available_size):,}mb\n" + s
            if not self.surveys:
                s = "There are no archives\n\n" + s

        return s

    def get_archive_stats(self, model, hardware_folder=r"\\192.168.3.2\images"):
        self.__init__()
        archive_folder = model.camera_data_folder + "/archive"
        samba_file_ops = get_file_ops(True)
        os_file_ops = get_file_ops(False)
        if self.cancelled:
            return
        if samba_file_ops.isdir(archive_folder):
            archive_surveys = samba_file_ops.listdir(archive_folder)
            for survey_folder in archive_surveys:
                if self.cancelled:
                    return
                archive_survey_stats = ArchiveSurveyStats()
                archive_survey_stats.name = survey_folder
                archive_survey_stats.status = "counting"
                self.surveys.append(archive_survey_stats)

        for archive_survey_stats in self.surveys:
            if self.cancelled:
                return
            survey_folder = archive_survey_stats.name
            full_archive_folder = archive_folder + "/" + survey_folder
            files = fnmatch.filter(samba_file_ops.listdir(full_archive_folder), "*.jpg")
            archive_survey_stats.archive_files = len(files)
            saved_survey_folder = model.data_folder + "/" + survey_folder
            try:
                friendly_name = model.surveys_data[survey_folder]["friendly_name"]
            except:
                friendly_name = None
            if friendly_name is not None:
                archive_survey_stats.name = friendly_name
            if not os_file_ops.isdir(saved_survey_folder):
                archive_survey_stats.save_files = 0
            else:
                files = fnmatch.filter(os_file_ops.listdir(saved_survey_folder), "*.jpg")
                archive_survey_stats.save_files = len(files)

            if abs(archive_survey_stats.save_files - archive_survey_stats.archive_files) < 20:
                archive_survey_stats.status = "match"
            else:
                archive_survey_stats.status = "different"

        self.space = smbclient._os.stat_volume(hardware_folder)

        # self.archive_size = 0.0
        # for archive_survey_stats in self.surveys:
        #     if self.cancelled:
        #         return
        #     survey_folder = archive_survey_stats.name
        #     full_archive_folder = archive_folder + "/" + survey_folder
        #     files = samba_file_ops.listdir(full_archive_folder)
        #     for file in files:
        #         if self.cancelled:
        #             return
        #         print(f"archive size {self.archive_size}")
        #         full_file_name = full_archive_folder + "/" + file
        #         self.archive_size = self.archive_size + samba_file_ops.file_size_mb(full_file_name)
        #
        # self.active_size = 0.0
        # camera_surveys = samba_file_ops.listdir(model.camera_data_folder)
        # for survey_folder in camera_surveys:
        #     if self.cancelled:
        #         return
        #     if survey_folder != "archive":
        #         full_survey_folder = model.camera_data_folder + "/" + survey_folder
        #         files = samba_file_ops.listdir(full_survey_folder)
        #         for file in files:
        #             if self.cancelled:
        #                 return
        #             print(f"active size {self.active_size}")
        #             full_file_name = full_survey_folder + "/" + file
        #             self.active_size = self.active_size + samba_file_ops.file_size_mb(full_file_name)
        #
        # self.free_space = 1000000 - (self.active_size + self.archive_size)
