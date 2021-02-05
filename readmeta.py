import tifffile

tag_index = 34119

def readtags(filehandle):
    tif_tags = {}
    for tag in filehandle.pages[0].tags.values():
        name, value = tag.name, tag.value
        tif_tags[name] = value

    tif_tags["image"] = {}

    imgtags = tif_tags[str(tag_index)].replace("\x00","").split("\r\n")

    for tag in imgtags:
        if "=" in tag:
            tag = tag.split("=")
            name, value = tag[0].strip(), tag[1].strip()
            tif_tags["image"][name] = value

    pixsize = tif_tags["image"]["Image Pixel Size"]

    tif_tags["Pixel Size"] = pixsize
    
    pixsize = pixsize.split(' ')

    tif_tags["Pixel Size Value"] = float(pixsize[0])
    tif_tags["Pixel Size Unit"] = pixsize[1]

    return tif_tags