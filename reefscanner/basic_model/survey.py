from reefscanner.basic_model.survey_reefcloud_info import ReefcloudUploadInfo


class Survey(object):
    def __init__(self, survey_json):
        self.id: str = survey_json.get("id")
        self.friendly_name: str = survey_json.get("friendly_name")
        self.samba: bool = survey_json.get("samba")
        self.folder: str = survey_json.get("folder")
        self.site: str = survey_json.get("site")

        self.photos = None
        self.start_date = None
        self.start_lat = None
        self.start_lon = None
        self.finish_date = None
        self.finish_lat = None
        self.finish_lon = None
        self.time_name = None
        self.start_depth = None
        self.finish_depth = None

        self.camera_dirs = {}

        self.operator: str = self.none_to_empty_string(survey_json.get("operator"))
        self.observer: str = self.none_to_empty_string(survey_json.get("observer"))
        self.vessel: str = self.none_to_empty_string(survey_json.get("operator"))
        self.sea: str = self.none_to_empty_string(survey_json.get("sea"))

        if 'wind_speed' in survey_json:
            self.wind_speed: str = self.none_to_empty_string(survey_json.get("wind_speed"))
        else:
            self.wind_speed: str = self.none_to_empty_string(survey_json.get("wind"))

        self.wind_direction: str = self.none_to_empty_string(survey_json.get("wind_direction"))

        self.cloud: str = self.none_to_empty_string(survey_json.get("cloud"))
        self.visibility: str = self.none_to_empty_string(survey_json.get("visibility"))
        self.tide: str = self.none_to_empty_string(survey_json.get("tide"))
        self.comments: str = self.none_to_empty_string(survey_json.get("comments"))
        self.reefcloud_project: str = self.none_to_empty_string(survey_json.get("reefcloud_project"))
        self.reefcloud_site: int = self.none_to_empty_string(survey_json.get("reefcloud_site"))

        if "reefcloud" in survey_json:
            self.reefcloud = ReefcloudUploadInfo(survey_json["reefcloud"])
        else:
            self.reefcloud = None

    def none_to_empty_string(self, str_in):
        if str_in is None:
            return ""
        else:
            return str_in

    def to_json(self):
        r = {"id": self.id,
                "friendly_name": self.friendly_name,
                "samba": self.samba,
                "folder": self.folder,
                "photos": self.photos,
                "start_date": self.start_date,
                "start_lat": self.start_lat,
                "start_lon": self.start_lon,
                "finish_date": self.finish_date,
                "finish_lat": self.finish_lat,
                "finish_lon": self.finish_lon,
                "site": self.site,
                "operator": self.operator,
                "observer": self.observer,
                "sea": self.sea,
                "wind_speed": self.wind_speed,
                "wind_direction": self.wind_direction,
                "cloud": self.cloud,
                "visibility": self.visibility,
                "tide": self.tide,
                "comments": self.comments,
                "reefcloud_project": self.reefcloud_project,
                "reefcloud_site": self.reefcloud_site
                }
        if self.reefcloud is not None:
            r["reefcloud"] = self.reefcloud.to_json()
        return r

    def best_name(self):
        if self.friendly_name is None or self.friendly_name == "":
            return self.id
        else:
            return self.friendly_name

