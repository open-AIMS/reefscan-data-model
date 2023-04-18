import math
import os
from reefscanner.basic_model import exif_utils
import pandas as pd
from reefscanner.basic_model.samba.file_ops_factory import get_file_ops


def make_photo_csv(folder):
    csv_file_name = folder + "/photo_log.csv"
    if os.path.exists("csv_file_name"):
        raise Exception(csv_file_name + " already exists.")

    if not os.path.isdir(folder):
        raise Exception("folder " + folder + " does not exist.")

    photos = [name for name in os.listdir(folder) if name.lower().endswith(".jpg")]

    df = pd.DataFrame()
    for photo in photos:
        exif = exif_utils.get_exif_data(folder + "/" + photo, open_photo_if_needed=False)
        df = df.append({"filename_string":photo, "latitude": exif["latitude"], "longitude": exif["longitude"],
                        "date_taken": exif["date_taken"]}, ignore_index=True)

    df.sort_values(by=["date_taken", "filename_string"])
    df.to_csv(csv_file_name, index=False)
    return df


def track(folder, samba):
    file_ops = get_file_ops(samba)
    csv_file_name = folder + "/photo_log.csv"
    if file_ops.exists(csv_file_name):
        with file_ops.open(csv_file_name) as file:
            df = pd.read_csv(file)
    else:
        raise Exception("No photo log found.")
        # if not samba:
        #     df = make_photo_csv(folder)
        # else:
        #     return None

    t = df[["latitude", "longitude", "filename_string"]]
    t = t[pd.to_numeric(t['latitude'], errors='coerce').notnull()]
    t.filename_string = folder + "/" +  t.filename_string
    t = t.values.tolist()
    interval = math.ceil(len(t)/200)
    t = t[::interval]
    return t



