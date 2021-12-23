import piexif
from PIL import Image


def get_exif_data(photo, open_photo_if_needed):
    try:
        exif_dict = piexif.load(photo)
    except:
        raise Exception("Can't get exif data for " + photo)

    try:
        width = exif_dict["Exif"][piexif.ExifIFD.PixelXDimension]
        height = exif_dict["Exif"][piexif.ExifIFD.PixelYDimension]
    except:
        if open_photo_if_needed:
            try:
                im = Image.open(photo)
                width, height = im.size
            except:
                raise Exception("Can't get width and height for " + photo)
        else:
            width=None
            height=None
    try:
        gps = exif_dict["GPS"]
        (lat, lon, date1) = get_coordinates(gps)
    except:
        raise Exception("Can't get exif data for " + photo)

    return {"latitude": lat, "longitude": lon, "date_taken": date1, "width": width, "height": height}


def get_coordinates(geotags):
    lat = get_decimal_from_dms(geotags[piexif.GPSIFD.GPSLatitude], geotags[piexif.GPSIFD.GPSLatitudeRef])
    lon = get_decimal_from_dms(geotags[piexif.GPSIFD.GPSLongitude], geotags[piexif.GPSIFD.GPSLongitudeRef])
    date = geotags[piexif.GPSIFD.GPSDateStamp]
    date = "".join(map(chr, date))
    # date format returned is weird. Has colons in the data part and no T
    date1 = date[0:4] + "-" + date[5:7] + "-" + date[8:10] + "T" + date[11:20]
    return (lat, lon, date1)


def get_decimal_from_dms(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in [b'S', b'W', 'S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)
