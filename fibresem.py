import tifffile

import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
import numpy as np

# import tkinter as tk
# from tkinter import filedialog


from lib import readtif

# from lib import segment


# cropping
def crop_square(tifimg):
    # Crop to Square and omit the SEM meta bar

    barheight = 0.11
    newHeight = round(tifimg.shape[0] * (1 - barheight))
    left = round((tifimg.shape[1] - newHeight) / 2)
    right = tifimg.shape[1] - left

    tifimg = tifimg[0:newHeight, left:right]

    return tifimg


def annotate(*args):
    # Annotate

    tifimg = args[0]
    tags = args[1]
    if len(args) == 3:
        outputname = args[2]
    else:
        outputname = "output.png"

    f = plt.figure(
        figsize=(tifimg.shape[1] / 300, tifimg.shape[0] / 300)
    )  # figure with correct aspect ratio
    ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
    ax.imshow(tifimg, cmap="gray")

    ax.axis("off")

    # Calculate dynamic border padding and font size, so the annotations are independent from image size
    imgpadding = 0.001 * tifimg.shape[0]
    dynFontSize = round(0.013 * tifimg.shape[0])
    fntScalebar = {"weight": "bold", "size": dynFontSize}
    fntAnnotation = {"weight": "normal", "size": dynFontSize}

    if not tags["Pixel Size"] == "NaN":
        scalebar = ScaleBar(
            tags["Pixel Size Value"],
            tags["Pixel Size Unit"],
            length_fraction=0.25,
            width_fraction=0.022,
            location="lower right",
            color="w",
            box_alpha=0,
            scale_loc="top",
            border_pad=imgpadding,
            font_properties=fntScalebar,
            sep=0.2,
        )
        ax.add_artist(scalebar)

    # Add sample name in lower right corner
    filenameparts = tags["filename"].split("_")
    text = filenameparts[1] + " " + filenameparts[2]
    ax.text(
        0.05 * tifimg.shape[0],  # x coordinate text
        0.95 * tifimg.shape[0],  # y coordinate text
        text,  # text string
        color=(1, 1, 1),  # color
        size=dynFontSize * 0.7,  # size
    )

    # plt.show()
    plt.savefig(outputname, bbox_inches="tight", pad_inches=0, dpi=300)
    print("Output written")

    plt.close()


def save_cropped(pathin, pathout):
    tifimg, tags = readtif.importtif(pathin)

    img = crop_square(tifimg)

    save_img(img, pathout)


def save_img(imgarray, pathout):
    f = plt.figure(
        figsize=(imgarray.shape[1] / 300, imgarray.shape[0] / 300)
    )  # figure with correct aspect ratio
    ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
    ax.imshow(tifimg, cmap="gray", vmin=0, vmax=255)
    ax.axis("off")

    plt.savefig(pathout, bbox_inches="tight", pad_inches=0, dpi=300)
    print("Output written")


def read(pathin):
    tifimg, tags = readtif.importtif(pathin)
    return (tifimg, tags)


def getPixelSize(tags):
    pass


def printtoarr():
    # This function 'burns' the information into the image array

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

    import os

    baseDir = r"I:\Projekte\Projekte\121250_PolyKARD\5-Data\10_Cell Culture\210920_CPD_R3\renamed"
    fileExt = ".tif"

    outputFolderName = "cropped"

    # for root, dirs, files in os.walk(baseDir):
    files = []

    for item in os.listdir(baseDir):
        if os.path.isfile(os.path.join(baseDir, item)):
            files.append(item)

    files = [fi for fi in files if fi.endswith(fileExt)]

    if len(files) > 0:

        outputPath = os.path.join(baseDir, outputFolderName)
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)

        for i in range(len(files)):
            currentFileName = files[i]

            print(currentFileName)

            img, tags = read(os.path.join(baseDir, currentFileName))

            img = crop_square(img)

            outFileName = currentFileName.replace(".tif", ".png")
            annotate(img, tags, os.path.join(outputPath, outFileName))

    """
    file_path = r"I:\Projekte\Projekte\121250_PolyKARD\5-Data\01_Electrospinning\SEM\SEM 2021.02.24\COLL.209_0020u_img57_hres.tif"

    img, tags = read(file_path)

    img = crop_square(img)

    annotate(img, tags)
    """
    # plotty(tifimg)

    # segment.seg_watershed(tifimg, 1.3, 2.5, 12, 100)

    # plotty(tifimg)
    pass
