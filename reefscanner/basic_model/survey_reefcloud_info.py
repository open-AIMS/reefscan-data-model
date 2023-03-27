import datetime


class ReefcloudUploadInfo(object):
    def __init__(self, json):
        self.uploaded_date = json.get("uploaded_date")
        self.uploaded_photo_count = json.get("uploaded_photo_count")
        self.first_photo_uploaded = json.get("first_photo_uploaded")
        self.last_photo_uploaded = json.get("last_photo_uploaded")
        self.total_photo_count = json.get("total_photo_count")

    def to_json(self):
        return {
            "uploaded_date": self.uploaded_date,
            "uploaded_photo_count": self.uploaded_photo_count,
            "first_photo_uploaded": self.first_photo_uploaded,
            "last_photo_uploaded": self.last_photo_uploaded,
            "total_photo_count": self.total_photo_count
        }
