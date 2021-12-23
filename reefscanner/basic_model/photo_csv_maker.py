import os
from reefscanner.basic_model import exif_utils
import pandas as pd
from reefscanner.basic_model.samba.file_ops_factory import get_file_ops


def make_photo_csv(folder):
    csv_file_name = folder + "/photos.csv"
    if os.path.exists("csv_file_name"):
        raise Exception(csv_file_name + " already exists.")

    if not os.path.isdir(folder):
        raise Exception("folder " + folder + " does not exist.")

    photos = [name for name in os.listdir(folder) if name.lower().endswith(".jpg")]

    df = pd.DataFrame()
    for photo in photos:
        exif = exif_utils.get_exif_data(folder + "/" + photo, open_photo_if_needed=False)
        df = df.append({"filename":photo, "latitude": exif["latitude"], "longitude": exif["longitude"],
                        "date_taken": exif["date_taken"]}, ignore_index=True)

    df.sort_values(by=["date_taken", "filename"])
    df.to_csv(csv_file_name, index=False)
    return df


def track(folder, samba):
    file_ops = get_file_ops(samba)
    csv_file_name = folder + "/photos.csv"
    if file_ops.exists(csv_file_name):
        with file_ops.open(csv_file_name) as file:
            df = pd.read_csv(file)
    else:
        if not samba:
            df = make_photo_csv(folder)
        else:
            return None

    t = df[["latitude", "longitude"]].values.tolist()
    return t


# tt = track("C:/aims/reef-scanner/images/20210727_232530_Seq01")
# print(str(tt))





