import tifffile

import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np

# import tkinter as tk
# from tkinter import filedialog


from lib import readtif
from lib import segment


# cropping
def crop_square(tifimg):
    barheight = 0.11
    newHeight = round(tags["ImageLength"] * (1 - barheight))
    left = round((tags["ImageWidth"] - newHeight) / 2)
    right = tags["ImageWidth"] - left

    tifimg = tifimg[0:newHeight, left:right]

    return tifimg


def plotty(tifimg):
    f = plt.figure(
        figsize=(tifimg.shape[1] / 300, tifimg.shape[0] / 300)
    )  # figure with correct aspect ratio
    ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
    ax.imshow(tifimg, cmap="gray")

    text = u""
    ax.text(50, 50, text, color=(1, 1, 1))
    ax.axis("off")

    scalebar = ScaleBar(
        tags["Pixel Size Value"],
        tags["Pixel Size Unit"],
        length_fraction=0.25,
        width_fraction=0.022,
        location="lower right",
        color="w",
        box_alpha=0,
        scale_loc="top",
        border_pad=1.5,
        sep=0.2,
    )
    ax.add_artist(scalebar)

    # plt.show()
    plt.savefig("output.png", bbox_inches="tight", pad_inches=0, dpi=300)
    print("Output written")


def printtoarr():
    """
    io_buf = io.BytesIO()
    fig.savefig(io_buf, format='raw', dpi=DPI)
    io_buf.seek(0)
    img_arr = np.reshape(np.frombuffer(io_buf.getvalue(), dtype=np.uint8),
                        newshape=(int(fig.bbox.bounds[3]), int(fig.bbox.bounds[2]), -1))
    io_buf.close()
    """


if __name__ == "__main__":
    # MAIN()

    file_path = "test2.tif"

    tifimg, tags = readtif.importtif(file_path)

    tifimg = crop_square(tifimg)

    # plotty(tifimg)

    segment.seg_watershed(tifimg, 1.3, 2.5, 12, 100)

    # plotty(tifimg)
    pass
