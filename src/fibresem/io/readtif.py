from fibresem.io import tifffile

# ZEISS SEM tag index for pixel size information
TAG_INDEX = 34119


def importtif(path):
    with tifffile.TiffFile(path) as fh:
        tif = fh.pages[0].asarray()
        tags = readtags(fh)

    return (tif, tags)


def readtags(filehandle):
    tif_tags = {}
    for tag in filehandle.pages[0].tags.values():
        name, value = tag.name, tag.value
        tif_tags[name] = value

    tif_tags["image"] = {}

    tif_tags["filename"] = filehandle.filename

    try:
        imgtags = tif_tags[str(TAG_INDEX)].replace("\x00", "").split("\r\n")

        for tag in imgtags:
            if "=" in tag:
                tag = tag.split("=")
                name, value = tag[0].strip(), tag[1].strip()
                tif_tags["image"][name] = value

        pixsize = tif_tags["image"]["Image Pixel Size"]

        tif_tags["Pixel Size"] = pixsize

        pixsize = pixsize.split(" ")

        tif_tags["Pixel Size Value"] = float(pixsize[0])
        tif_tags["Pixel Size Unit"] = pixsize[1]
    except:
        print("Could not find ZEISS SEM TAG.")

        tif_tags["Pixel Size"] = "NaN"
        tif_tags["Pixel Size Value"] = 0
        tif_tags["Pixel Size Unit"] = None

    return tif_tags
