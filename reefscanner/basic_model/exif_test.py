from reefscanner.basic_model import exif_utils

exif = exif_utils.get_exif_data("D:/reefscan-test-data/20211214_225242_Seq02/reefcloud/20211214_225243_000_0001.jpg", open_photo_if_needed=True)

print (exif)
