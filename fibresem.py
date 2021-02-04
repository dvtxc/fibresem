import tifffile

import readtags

with tifffile.TiffFile('test.tif') as tif:
    tags = readtags.readtags(tif)

    image = tif.pages[0].asarray()



print(tags)

