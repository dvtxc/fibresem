import tifffile

import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np

import readmeta

with tifffile.TiffFile("test.tif") as tif:
    tags = readmeta.readtags(tif)
    tifimg = tif.pages[0].asarray()


text = u"lolol"

# cropping
barheight = 0.11
newHeight = round(tags["ImageLength"] * (1 - barheight))
left = round((tags["ImageWidth"] - newHeight) / 2)
right = tags["ImageWidth"] - left

tifimg = tifimg[0:newHeight, left:right]


f = plt.figure(
    figsize=(tifimg.shape[1] / 300, tifimg.shape[0] / 300)
)  # figure with correct aspect ratio
ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
ax.imshow(tifimg, cmap="gray")
ax.text(50, 50, text, color=(1, 1, 1))
ax.axis("off")

scalebar = ScaleBar(
    tags["Pixel Size Value"],
    tags["Pixel Size Unit"],
    length_fraction=0.25,
    width_fraction=0.015,
    location="lower right",
    color="w",
    box_alpha=0,
    scale_loc="top",
)
ax.add_artist(scalebar)

plt.show()
