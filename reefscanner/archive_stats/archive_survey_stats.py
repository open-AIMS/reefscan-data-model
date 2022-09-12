class ArchiveSurveyStats:
    def __init__(self):
        self.name = None
        self.archive_files = 0
        self.save_files = 0
        self.status = "counting"

    def to_string(self):
        archive_files = f"{self.archive_files:,}"
        saved_files = f"{self.save_files:,}"
        return f"{self.name:<25}   archived files: {archive_files:<8}   saved files: {saved_files:<8}   status: {self.status:<8}"
